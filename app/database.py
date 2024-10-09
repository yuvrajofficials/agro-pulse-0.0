import os
import json
from google.cloud import firestore
from google.oauth2 import service_account

# Get the FIRESTORE_CREDENTIALS_JSON environment variable
firestore_credentials_json = os.getenv('FIRESTORE_CREDENTIALS_JSON')
if firestore_credentials_json:
    # Parse the JSON string
    credentials_info = json.loads(firestore_credentials_json)

    # Create credentials from the parsed JSON
    credentials = service_account.Credentials.from_service_account_info(credentials_info)

    # Initialize Firestore client with the credentials
    db = firestore.Client(credentials=credentials)
else:
    raise Exception("Firestore credentials not provided.")
