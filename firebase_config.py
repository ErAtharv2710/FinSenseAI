import firebase_admin
from firebase_admin import credentials, firestore

# use the exact filename that you downloaded
cred = credentials.Certificate("finsenseai-834cf-firebase-adminsdk-fbsvc-e8ef115421.json")

firebase_admin.initialize_app(cred)

db = firestore.client()
