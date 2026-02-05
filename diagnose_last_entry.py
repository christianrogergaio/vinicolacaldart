
from core import firestore_client
import datetime
from firebase_admin import firestore
import json

def serialize_sets(obj):
    if isinstance(obj, set):
        return list(obj)
    return obj

try:
    print("Connecting to Firestore...")
    db = firestore_client.get_db()
    ref = db.collection('teste')
    
    # User says "more than 1 hour ago". Let's look back 4 hours just to be sure we see the "before" state
    # IDs are typically in Brazil time (UTC-3).
    # We will generate a prefix for 4 hours ago.
    
    # utcnow is UTC. 
    # If IDs are Brazil time, we need UTC - 3.
    now_utc = datetime.datetime.utcnow()
    brazil_time = now_utc - datetime.timedelta(hours=3)
    
    search_start_time = brazil_time - datetime.timedelta(hours=4)
    start_id = search_start_time.strftime('%Y-%m-%d_%H-%M-%S')
    
    print(f"Buscando registros a partir de (ID/Timestamp): {start_id}")
    
    query = ref.where('__name__', '>=', start_id)
    docs = query.stream()
    
    last_doc = None
    count = 0
    
    print("\nResumo dos últimos registros encontrados:")
    for doc in docs:
        last_doc = doc
        count += 1
        # Print just the ID to show flow
        # print(f" - {doc.id}")
        
    print(f"\nTotal de registros nas últimas 4 horas: {count}")
    
    if last_doc:
        data = last_doc.to_dict()
        print("\n" + "="*50)
        print(f" ÚLTIMO REGISTRO ({last_doc.id})")
        print("="*50)
        # Sort keys for easier reading
        for k in sorted(data.keys()):
            print(f" {k}: {data[k]}")
        print("="*50)
        
        # Check specific fields for diagnosis
        print("\nDIAGNÓSTICO:")
        if 'vleitura' in data:
            print(f" > Voltagem Leitura (vleitura): {data['vleitura']}")
        if 'vinput' in data:
            print(f" > Voltagem Input (vinput): {data['vinput']}")
        if 'bateria' in data:
            print(f" > Bateria: {data['bateria']}")
            
    else:
        print("Nenhum registro encontrado nas últimas 4 horas.")
        
except Exception as e:
    print(f"Erro: {e}")
