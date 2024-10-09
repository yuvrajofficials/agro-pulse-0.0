import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Firestore DB
def init_firestore():
    cred = credentials.Certificate(os.getenv('FIRESTORE_CREDENTIALS'))
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db

db = init_firestore()
