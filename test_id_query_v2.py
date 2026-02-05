from core import firestore_client
import datetime
from firebase_admin import firestore

try:
    print("Connecting...")
    db = firestore_client.get_db()
    ref = db.collection('teste')
    
    # Calculate ID prefix for 2 hours ago
    now = datetime.datetime.utcnow() - datetime.timedelta(hours=3) # Brasil
    two_hours_ago = now - datetime.timedelta(hours=2)
    start_id = two_hours_ago.strftime('%Y-%m-%d_%H-%M-%S')
    
    print(f"Querying for ID >= {start_id}")
    
    # Correct way to range on ID: order_by __name__ and start_at
    # Default order is ASC. We want IDs > start_id.
    query = ref.order_by(firestore.FieldPath.document_id()).start_at({
        firestore.FieldPath.document_id(): start_id
    })
    
    # Or simpler:
    # query = ref.order_by('__name__').start_at([start_id])
    
    docs = query.stream()
    
    count = 0
    first = None
    last = None
    for d in docs:
        if count == 0: first = d.id
        last = d.id
        count += 1
        
    print(f"Found {count} docs.")
    print(f"First: {first}")
    print(f"Last: {last}")
    
except Exception as e:
    print(f"Error: {e}")
