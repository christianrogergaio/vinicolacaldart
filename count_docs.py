from core import firestore_client

try:
    print("Connecting to Firestore...")
    db = firestore_client.get_db()
    ref = db.collection('teste')
    
    # Just get a few to start, see if it works
    print("Attempting to stream...")
    # I can't easily count without paying for reads, but I can iterate and break
    docs = ref.stream()
    
    count = 0
    for d in docs:
        count += 1
        if count % 100 == 0:
            print(f"Counted {count}...")
        if count > 2000:
             print("More than 2000 docs! Stopping count to save time.")
             break
             
    print(f"Total counted (capped): {count}")
    
except Exception as e:
    print(f"Error: {e}")
