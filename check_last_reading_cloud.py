
from core import firestore_client
from firebase_admin import firestore

try:
    print("Conectando ao Firestore...")
    db = firestore_client.get_db()
    
    # Ordena pelo ID (que é a data/hora) decrescente para pegar o ultimo
    print("Buscando último registro...")
    ref = db.collection('teste')
    docs = ref.order_by('__name__', direction=firestore.Query.DESCENDING).limit(1).stream()
    
    found = False
    for doc in docs:
        found = True
        data = doc.to_dict()
        print("\n" + "="*40)
        print(f" [ÚLTIMO REGISTRO ENCONTRADO]")
        print("="*40)
        print(f"  📅 ID (Timestamp): {doc.id}")
        print(f"  🌡️ Temp:  {data.get('temperatura')} °C")
        print(f"  💧 Umid:  {data.get('umidade')} %")
        print(f"  📍 Origem: {data.get('origem', 'N/A')}")
        print("="*40 + "\n")
    
    if not found:
        print("Nenhum dado encontrado na coleção 'teste'.")

except Exception as e:
    print(f"Erro ao conectar ou buscar: {e}")
