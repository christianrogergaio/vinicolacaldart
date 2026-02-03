import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import datetime

# Setup path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENCIAIS_FIREBASE = os.path.join(BASE_DIR, "config", "evcr-monitor-firebase-key.json")

def check_firestore():
    try:
        if not os.path.exists(CREDENCIAIS_FIREBASE):
            print("ERROR: Credentials file not found!")
            return

        cred = credentials.Certificate(CREDENCIAIS_FIREBASE)
        firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        
        # Query last 5 docs from 'teste'
        docs_ref = db.collection('teste')
        query = docs_ref.order_by('data', direction=firestore.Query.DESCENDING).limit(10)
        results = query.stream()
        
        count = 0
        print("--- LAST 10 READINGS FROM FIRESTORE ---")
        for doc in results:
            data = doc.to_dict()
            print(f"ID: {doc.id} | Data: {data.get('data')} {data.get('hora')} | Temp: {data.get('temperatura')} | Umid: {data.get('umidade')}")
            count += 1
            
        if count == 0:
            print("No documents found in 'teste' collection.")
        else:
            print(f"\nFound {count} recent records.")

    except Exception as e:
        print(f"Error accessing Firestore: {e}")

if __name__ == "__main__":
    check_firestore()
