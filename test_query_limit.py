from core import firestore_client
import datetime
from firebase_admin import firestore

try:
    print("Connecting...")
    db = firestore_client.get_db()
    ref = db.collection('teste')
    
    # Calculate time string for 2 hours ago
    now = datetime.datetime.utcnow() - datetime.timedelta(hours=3) # Brasil
    two_hours_ago = now - datetime.timedelta(hours=2)
    
    date_str = now.strftime('%Y-%m-%d')
    time_str = two_hours_ago.strftime('%H:%M:%S')
    
    print(f"Querying for Data={date_str} and Hora >= {time_str}")
    
    # Compound query
    query = ref.where('data', '==', date_str).where('hora', '>=', time_str)
    
    docs = query.stream()
    
    count = 0
    for d in docs:
        count += 1
        
    print(f"Found {count} docs in last 2 hours.")
    
except Exception as e:
    print(f"Error: {e}")
