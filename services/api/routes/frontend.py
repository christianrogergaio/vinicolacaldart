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
        import datetime
        
        # Get coordinates from config
        lat = config.LATITUDE
        lon = config.LONGITUDE
        
        # Open-Meteo API for Forecast (Hourly for Risk Model)
        # Fetching 2 days to have enough history for the simulation loop
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,precipitation,is_day&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=America%2FSao_Paulo&forecast_days=2"
        
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            daily = data.get("daily", {})
            hourly = data.get("hourly", {})
            
            # --- 1. Basic Daily Stats (for display) ---
            temp_max = daily["temperature_2m_max"][1] if len(daily.get("temperature_2m_max", [])) > 1 else 0
            temp_min = daily["temperature_2m_min"][1] if len(daily.get("temperature_2m_min", [])) > 1 else 0
            precip = daily["precipitation_sum"][1] if len(daily.get("precipitation_sum", [])) > 1 else 0
            
            # --- 2. Advanced Risk Model (Plasmopara Viticola) ---
            # Prepare hourly data list for the simulation
            lista_dados_horarios = []
            
            # Open-Meteo returns parallel arrays. We explicitly zip them.
            times = hourly.get("time", [])
            temps = hourly.get("temperature_2m", [])
            umids = hourly.get("relative_humidity_2m", [])
            precips = hourly.get("precipitation", [])
            is_days = hourly.get("is_day", [])
            
            for i in range(len(times)):
                lista_dados_horarios.append({
                    "time_str": times[i],
                    "temp": temps[i],
                    "umid": umids[i],
                    "precip": precips[i],
                    "is_day": is_days[i]
                })
            
            # Run Simulation
            resultado_simulacao = calculos.simular_risco_plasmopara(lista_dados_horarios)
            
            # Extract Results
            semaforo = resultado_simulacao.get("semaforo", "VERDE")
            mensagem = resultado_simulacao.get("mensagem", "Sem dados")
            sev = resultado_simulacao.get("sev_acumulado", 0.0)
            incubacao_percent = resultado_simulacao.get("incubacao_dia_percent", 0.0)
            detalhes_log = resultado_simulacao.get("detalhes_log", [])
            
            # --- 3. Construct Response ---
            return {
                "semaforo": semaforo,
                "mensagem": mensagem,
                "sev": sev,
                "incubacao_percent": incubacao_percent,
                "gdd_previsto": calculos.calcular_gdd(temp_max, temp_min, temp_base=10),
                "detalhes_clima": f"Chuva: {precip}mm | Max: {temp_max}°C",
                "debug_log": detalhes_log[-5:]
            }
            
    except Exception as e:
        print(f"Erro na previsao: {e}")
        import traceback
        traceback.print_exc()
        
    # Fallback
    return {"tendencia": "Indisponível", "risco": "--", "detalhes": "Erro ao conectar API externa"}

@router.get("/api/relatorios/diario")
async def get_relatorio_diario(dias: int = 30):
    """
    Returns a daily summary of agricultural risk (SaaS Premium Report).
    Aggregates raw sensor data into daily metrics:
    - Min/Avg/Max Temp
    - Total Wetness Hours per day
    - Max Severity (SEV) calculated via Hourly Simulation
    - Final Risk Status (Traffic Light)
    """
    try:
        from collections import defaultdict
        import datetime
        
        # 1. Fetch Raw Data
        historico_raw = database.buscar_historico(dias=dias) # List of sqlite3.Row or dict
        
        # 2. Group by Date -> Hour -> Readings (for Resampling)
        # Structure: date_str -> hour_str -> [readings]
        dados_por_hora = defaultdict(lambda: defaultdict(list))
        
        for row in historico_raw:
            # Parse timestamp. Assumes format "YYYY-MM-DD HH:MM:SS"
            ts_str = row['data_hora']
            try:
                dt = datetime.datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                 # Try ISO format if T exists
                dt = datetime.datetime.strptime(ts_str.replace("T", " "), "%Y-%m-%d %H:%M:%S")
            
            date_key = dt.strftime("%Y-%m-%d")
            hour_key = dt.hour # 0-23 integer
            
            dados_por_hora[date_key][hour_key].append(row)
            
        # 3. Process each Day
        relatorio = []
        
        # Sort dates descending
        sorted_dates = sorted(dados_por_hora.keys(), reverse=True)
        
        for data_dia in sorted_dates:
            horas_do_dia = dados_por_hora[data_dia]
            
            # 3.1 Resample to Hourly Data (Required for Scientific Model)
            hourly_inputs = []
            temps_do_dia = []
            molhamento_total_horas = 0
            
            # Iterate 0 to 23 to ensure timeline consistency
            for h in range(24):
                leituras = horas_do_dia.get(h, [])
                
                if not leituras:
                    # Missing data handling: skip or interpolate?
                    # For risk model, gaps break accumulation. We'll skip adding to simulation input, 
                    # effectively resetting consecutive counters, which is safer (under-estimating risk requires caution).
                    continue
                    
                # Hourly Averages
                avg_temp = sum(d['temperatura'] for d in leituras) / len(leituras)
                avg_umid = sum(d['umidade'] for d in leituras) / len(leituras)
                
                # Simple Wetness Check for Stats (Any reading > 80% or Avg > 80%?)
                # Scientific: usually "Hours where avg > Threshold".
                if avg_umid >= 80.0:
                    molhamento_total_horas += 1
                
                temps_do_dia.append(avg_temp)
                
                # Check Day/Night (Simple approximation: 6h to 18h is Day)
                is_day = 1 if 6 <= h < 18 else 0
                
                hourly_inputs.append({
                    "time_str": f"{data_dia} {h:02d}:00",
                    "temp": avg_temp,
                    "umid": avg_umid,
                    "is_day": is_day,
                    "precip": 0.0 # TODO: Integrate rain sensor if available
                })
            
            if not hourly_inputs:
                continue
                
            # 3.2 Run Simulation for the Day
            # This calculates the SEV accumulation hour by hour for this specific day
            resultado_sim = calculos.simular_risco_plasmopara(hourly_inputs)
            
            # 3.3 Aggregates
            t_min = min(temps_do_dia) if temps_do_dia else 0
            t_max = max(temps_do_dia) if temps_do_dia else 0
            
            relatorio.append({
                "data": data_dia,
                "t_min": round(t_min, 1),
                "t_max": round(t_max, 1),
                "molhamento_h": molhamento_total_horas,
                "sev": resultado_sim.get("sev_acumulado", 0.0),
                "semaforo": resultado_sim.get("semaforo", "VERDE"),
                "risco_msg": resultado_sim.get("mensagem", ""),
                "incubacao_pct": resultado_sim.get("incubacao_dia_percent", 0.0)
            })
            
        return {"relatorio": relatorio}
            
    except Exception as e:
        print(f"Erro relatório diário: {e}")
        import traceback
        traceback.print_exc()
        return {"relatorio": []}
