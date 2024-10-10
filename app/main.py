from fastapi import FastAPI, Depends, HTTPException, status
from app.models import UserCreate, UserLogin, PhoneLogin
from app.database import db
from app.auth import hash_password, verify_password, create_access_token
from google.cloud.firestore_v1 import DocumentSnapshot
import tensorflow as tf
from fastapi import FastAPI, UploadFile, File
from PIL import Image
import numpy as np
import io


app = FastAPI()
model = tf.keras.models.load_model("wheat_disdet.h5")


# User Registration
@app.post("/register")
async def register_user(user: UserCreate):
    # Check if email or phone already exists
    user_ref_email = db.collection('users').where('email', '==', user.email).stream()
    user_ref_phone = db.collection('users').where('phone', '==', user.phone).stream()

    if any(user_ref_email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
    if any(user_ref_phone):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already registered.")

    # Hash password
    hashed_password = hash_password(user.password)

    # Save user to Firestore
    user_data = {
        "name": user.name,
        "email": user.email,
        "password": hashed_password,
        "address": user.address,
        "phone": user.phone
    }
    db.collection('users').document(user.email).set(user_data)

    return {"message": "User registered successfully!"}

# User Login via Email/Password
@app.post("/login/email")
async def login_user(user: UserLogin):
    # Fetch user from Firestore
    user_doc: DocumentSnapshot = db.collection('users').document(user.email).get()

    if not user_doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user_data = user_doc.to_dict()

    # Verify password
    if not verify_password(user.password, user_data['password']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

    # Create JWT token
    token = create_access_token({"sub": user.email})

    return {"access_token": token, "token_type": "bearer"}

# User Login via Phone/Password
@app.post("/login/phone")
async def login_user_phone(user: PhoneLogin):
    # Fetch user by phone from Firestore
    user_ref = db.collection('users').where('phone', '==', user.phone).stream()
    user_doc = next(user_ref, None)

    if not user_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user_data = user_doc.to_dict()

    # Verify password
    if not verify_password(user.password, user_data['password']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

    # Create JWT token
    token = create_access_token({"sub": user.phone})

    return {"access_token": token, "token_type": "bearer"}


disease_categories = ['Brown rust', 'Healthy', 'Loose Smut', 'Septoria', 'Yellow rust']

# Preprocessing function to prepare the image
def preprocess_image(image: Image.Image) -> np.ndarray:
    image = image.resize((150, 150))  # Resize image to the input size of your model
    image = image.convert("RGB")      # Ensure the image is in RGB format
    image = np.array(image) / 255.0   # Normalize pixel values
    image = np.expand_dims(image, axis=0)  # Add batch dimension (1, 150, 150, 3)
    return image

# Prediction endpoint
@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    # Read and open the uploaded image
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    # Preprocess the image
    preprocessed_image = preprocess_image(image)

    # Make prediction
    prediction = model.predict(preprocessed_image)

    # Get the predicted class
    predicted_class = np.argmax(prediction, axis=1)[0]

    # Map the predicted class to the disease category
    predicted_disease = disease_categories[predicted_class]

    return {"predicted_disease": predicted_disease}



# Protected Route (Example)
@app.get("/protected")
async def protected_route(token: str = Depends(create_access_token)):
    return {"message": "You are in a protected area."}


