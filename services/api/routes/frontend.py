from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
import sys

# Imports core logic
from core import database, config, calculos

router = APIRouter()

# Setup templates (duplicated ref, can be centralized)
templates_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
templates = Jinja2Templates(directory=templates_path)

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/relatorios", response_class=HTMLResponse)
async def relatorios(request: Request):
    return templates.TemplateResponse("relatorios.html", {"request": request})

@router.get("/analise", response_class=HTMLResponse)
async def analise(request: Request):
    return templates.TemplateResponse("analise.html", {"request": request})

# API Endpoints used by Frontend JS
@router.get("/api/historico")
async def get_historico():
    # Reuse logic from database
    # Switch to Cloud Firestore (Persistent)
    # return database.buscar_historico(dias=30) # OLD: Local only
    from core import firestore_client
    return firestore_client.buscar_historico_cloud(limit=100)

@router.get("/api/config")
async def get_config():
    return {
        "plantas": config.PLANTAS,
        "doencas": config.DOENCAS,
        "estadios_por_planta": config.ESTADIOS_POR_PLANTA
    }

@router.get("/api/relatorios/analise")
async def get_analise_relatorio(dias: int = 30):
    # Fetch raw history
    historico = database.buscar_historico(dias=dias)
    
    # Process data to include VDS
    # For this view, we'll use a default context or just show raw values + calculated VDS for a "standard" scenario
    # In a real app, this might accept query params for plant/disease context
    
    processed_data = []
    for leitura in historico:
        # Calculate VDS assuming a default critical scenario (e.g., Videira - Míldio - Frutificação)
        # This is just for the history table visualization
        vds = calculos.calcular_vds_numerico(
            leitura['temperatura'], 
            leitura['umidade'], 
            "Míldio", 
            "Videira", 
            "Frutificação"
        )
        
        # Add to list
        # Convert sqlite3.Row/dict to a new dict to avoid mutation issues if any
        item = dict(leitura)
        item['vds'] = vds
        processed_data.append(item)
        
    return {"vds": processed_data}
    return {"vds": processed_data}

@router.get("/api/previsao")
async def get_previsao():
    try:
        import requests
        # Get coordinates from config
        lat = config.LATITUDE
        lon = config.LONGITUDE
        
        # Open-Meteo API for Forecast (Daily Max/Min Temp, Precipitation Sum, Humidity)
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,relative_humidity_2m_mean&timezone=America%2FSao_Paulo&forecast_days=2"
        
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            daily = data.get("daily", {})
            
            # Get tomorrow's data (index 1)
            temp_max = daily["temperature_2m_max"][1]
            temp_min = daily["temperature_2m_min"][1]
            precip = daily["precipitation_sum"][1]
            umid_media = daily.get("relative_humidity_2m_mean", [0, 0])[1] # Default if missing
            
            # 1. Calculate GDD (Base 10 for Soy/General)
            gdd = calculos.calcular_gdd(temp_max, temp_min, temp_base=10)
            
            # 2. Calculate Disease Risk (VDS)
            # Use 'Videira' + 'Míldio' as default context for now (could be dynamic)
            avg_temp = (temp_max + temp_min) / 2
            vds = calculos.calcular_vds_numerico(avg_temp, umid_media, "Míldio", "Videira", "Frutificação")
            
            # Determine Risk Level Text
            risco_texto = "BAIXO"
            if vds > 1.0 or precip > 10:
                risco_texto = "ALTO" 
            elif vds > 0.5 or precip > 2:
                risco_texto = "MÉDIO"
                
            # Trend Description - NOW PRIORITIZING DISEASE RISK AS REQUESTED
            tendencia = f"Risco {risco_texto}"
            if vds > 1.0:
                tendencia = "Risco Alto (Míldio)"
            elif vds > 0.5:
                tendencia = "Risco Moderado"
            elif precip > 10:
                tendencia = "Risco (Chuva Intensa)"
            else:
                tendencia = "Risco Baixo"

            return {
                "tendencia": tendencia,
                "risco": risco_texto,
                "vds_previsto": vds,
                "gdd_previsto": gdd,
                "detalhes": f"VDS Proj: {vds:.2f} | GDD: {gdd:.1f} | Chuva: {precip}mm"
            }
            
    except Exception as e:
        print(f"Erro na previsao: {e}")
        
    # Fallback
    return {"tendencia": "Indisponível", "risco": "--", "detalhes": ""}
