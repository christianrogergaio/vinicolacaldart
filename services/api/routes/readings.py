from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import datetime
import sys
import os

# Imports core logic
from core import database, calculos, config

router = APIRouter()

class Reading(BaseModel):
    temperatura: float
    umidade: float
    latitude: float = 0.0
    longitude: float = 0.0
    origem: str = "Unknown"

# --- Background Tasks ---
def sync_to_firestore(reading: Reading):
    """Simulates Firestore sync (migrated from leitor_arduino.py)"""
    try:
        import firebase_admin
        from firebase_admin import credentials
        from firebase_admin import firestore
        
        # Initialize if needed (simple check)
        if not firebase_admin._apps:
             cred = credentials.Certificate(config.CREDENCIAIS_FIREBASE)
             firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        
        # Data/Hora Brasil
        agora_br = datetime.datetime.utcnow() - datetime.timedelta(hours=3)
        
        doc_id = agora_br.strftime('%Y-%m-%d_%H-%M-%S')
        data = reading.dict()
        data['data'] = agora_br.strftime('%Y-%m-%d')
        data['hora'] = agora_br.strftime('%H:%M:%S')
        
        db.collection('teste').document(doc_id).set(data)
        print(f"Synced to Firestore: {doc_id}")
    except Exception as e:
        print(f"Firestore Sync Error: {e}")

@router.post("/readings")
async def receive_reading(reading: Reading, background_tasks: BackgroundTasks):
    # 1. Save to Local SQLite
    success = database.salvar_leitura(
        reading.temperatura, 
        reading.umidade, 
        reading.latitude, 
        reading.longitude
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save reading locally")

    # 2. Trigger Alerts (Simplified logic)
    # In a real microservice, this might publish to a queue (RabbitMQ/Redis)
    # Here we just check and print for simplicity or use a helper
    # check_alerts(reading) 

    # 3. Background Sync to Cloud
    background_tasks.add_task(sync_to_firestore, reading)

    return {"status": "received"}
