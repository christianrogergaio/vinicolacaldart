import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing imports...")
    from core import firestore_client
    print("Import firestore_client success.")
    
    # Try to initialize (this triggers the secrets loader path if file missing, 
    # but here file likely exists, so we might need to simulate)
    
    from core import secrets_loader
    print("Import secrets_loader success.")
    
    print("Checking key reconstruction...")
    key = secrets_loader.FIREBASE_CONFIG['private_key']
    if "-----BEGIN PRIVATE KEY-----" in key and "-----END PRIVATE KEY-----" in key:
        print("Key structure looks valid.")
    else:
        print("INVALID KEY STRUCTURE")
        
    print("\nAttempting to fetch data (using whichever method worked)...")
    data = firestore_client.buscar_historico_cloud(limit=5)
    print(f"Fetched {len(data)} records.")
    
    print("TEST COMPLETED SUCCESSFULLY")
    
except Exception as e:
    print(f"TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
