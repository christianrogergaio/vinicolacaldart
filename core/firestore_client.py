import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import datetime
from . import config

# Singleton initialization
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(config.CREDENCIAIS_FIREBASE)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Warning: Could not initialize Firebase: {e}")

def get_db():
    try:
        return firestore.client()
    except Exception as e:
        print(f"Error getting firestore client: {e}")
        return None

def buscar_historico_cloud(limit=50):
    """Busca histórico do Firestore para substituir o SQLite local"""
    db = get_db()
    if not db:
        return []

    try:
        readings_ref = db.collection('teste')
        # Order by document ID (which is YYYY-MM-DD_HH-MM-SS) descending
        # Or by a specific field if available. Doc ID is reliable defined in readings.py
        
        # Firestore IDs are strings, so lexical sort works for this format
        query = readings_ref.order_by(firestore.FieldPath.document_id(), direction=firestore.Query.DESCENDING).limit(limit)
        docs = query.stream()
        
        historico = []
        for doc in docs:
            data = doc.to_dict()
            # Normalize to match SQLite format for frontend compatibility
            # SQLite: { 'temperatura': X, 'umidade': Y, 'data_hora': 'YYYY-MM-DD HH:MM:SS' ... }
            # Firestore (current): { 'temperatura': X, 'umidade': Y, 'data': 'YYYY-MM-DD', 'hora': 'HH:MM:SS' }
            
            dt_str = f"{data.get('data')} {data.get('hora')}"
            
            item = {
                "temperatura": data.get("temperatura", 0),
                "umidade": data.get("umidade", 0),
                "latitude": data.get("latitude", 0),
                "longitude": data.get("longitude", 0),
                "data_hora": dt_str,
                "origem": data.get("origem", "Cloud")
            }
            historico.append(item)
            
        # The frontend often expects ascending order for charts
        historico.reverse()
        return historico

    except Exception as e:
        print(f"Error reading Firestore: {e}")
        return []
