import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import datetime
from . import config

# Singleton initialization
if not firebase_admin._apps:
    try:
        # Try Loading from File
        if os.path.exists(config.CREDENCIAIS_FIREBASE):
             cred = credentials.Certificate(config.CREDENCIAIS_FIREBASE)
             firebase_admin.initialize_app(cred)
             print("Initialized Firebase from File")
        else:
             # Try Loading from Secret Loader (Bypass for Render)
             try:
                 from . import secrets_loader
                 cred = credentials.Certificate(secrets_loader.FIREBASE_CONFIG)
                 firebase_admin.initialize_app(cred)
                 print("Initialized Firebase from Secrets Loader")
             except ImportError:
                 print("Critical: No Firebase credentials found (File or Loader).")
                 
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
        # Get docs from the last 3 days to avoid downloading thousands of records
        # doc ID is "YYYY-MM-DD_HH-MM-SS"
        # We can use start_at logic on document ID or strict equality on 'data' field
        
        # OPTIMIZED QUERY FOR FREE PLAN
        # Instead of fetching by Date (which might return 3000+ docs and timeout),
        # we fetch by Document ID Range.
        # IDs are "YYYY-MM-DD_HH-MM-SS".
        # We only need the last few hours for the live dashboard.
        
        import datetime
        now = datetime.datetime.utcnow() - datetime.timedelta(hours=3) # Brasil
        # Fetch last 48 hours of data (plenty for "Live" view + History)
        start_time = now - datetime.timedelta(hours=48)
        start_id = start_time.strftime('%Y-%m-%d_%H-%M-%S')
        
        # Range query on __name__ (Document ID)
        # This is extremely fast and requires no index.
        query = readings_ref.order_by('__name__').start_at([start_id])
        
        docs = query.stream()
        
        historico = []
        for doc in docs:
            data = doc.to_dict()
            
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

        # Sort desc (Newest first) for frontend
        historico.sort(key=lambda x: x['data_hora'], reverse=True)
        # Apply limit just in case
        historico = historico[:limit]
        
        # The frontend often expects ascending order for charts
        historico.reverse()
        return historico

    except Exception as e:
        print(f"Error reading Firestore: {e}")
        return []
