import serial
import time
import logging
import sys
import os
import requests
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add project root to sys.path to allow importing core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core import config, database

# Config
SERIAL_PORT = config.PORTA_SERIAL
BAUD_RATE = config.BAUD_RATE
INTERVALO_LEITURA = config.INTERVALO_LEITURA

def parse_line(line):
    """
    Parses "Temp: 25.00 | Umid: 65.00" -> (25.0, 65.0)
    """
    try:
        limpa = line.replace("C", "").replace("%", "").replace("*", "").replace("|", ":")
        partes = limpa.split(":")
        # parts: ['Temp', ' 25.00 ', ' Umid', ' 65.00']
        
        temperatura = float(''.join(c for c in partes[1] if c.isdigit() or c == '.'))
        umidade = float(''.join(c for c in partes[3] if c.isdigit() or c == '.'))
        return temperatura, umidade
    except Exception as e:
        return None, None

def main():
    # Initialize DB (creates tables if missing)
    database.init_db()
    
    arduino = None
    
    while True:
        try:
            if arduino is None:
                logging.info(f"Attempting to connect to Arduino on {SERIAL_PORT}...")
                arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
                time.sleep(2)
                logging.info(f"Connected to Arduino on {SERIAL_PORT}")
                print(f"\nConectado com sucesso na porta {SERIAL_PORT}!\n")

            if arduino.in_waiting > 0:
                line = arduino.readline().decode('utf-8', errors='ignore').strip()
                if not line:
                    continue
                
                print(f"DEBUG Raw: {line}") # Temporary: View raw data
                # logging.debug(f"Received: {line}")
                
                if ("Umidade" in line or "Umid" in line) and ("Temperatura" in line or "Temp" in line):
                    temp, umid = parse_line(line)
                    
                    if temp is not None and umid is not None:
                        # User requested print
                        print(f"Temperatura: {temp:.1f}C  |  Umidade: {umid:.1f}%")

                        try:
                            # 1. Save directly to DB (Local)
                            success = database.salvar_leitura(temp, umid, config.LATITUDE, config.LONGITUDE)
                            if success:
                                logging.info(f"Saved: {temp}C, {umid}%")
                            else:
                                logging.error("Failed to save to DB")
                                
                            # 2. Sync to Remote Dashboard (Mac) if Configured
                            if config.API_URL_SYNC:
                                try:
                                    payload = {
                                        "temperatura": temp,
                                        "umidade": umid,
                                        "latitude": config.LATITUDE,
                                        "longitude": config.LONGITUDE,
                                        "origem": "Windows Agent"
                                    }
                                    resp = requests.post(config.API_URL_SYNC, json=payload, timeout=2)
                                    if resp.status_code == 200:
                                        print("   📡 Sincronizado com Dashboard remoto!")
                                    else:
                                        print(f"   ⚠️ Falha na sincronização: {resp.status_code}")
                                except Exception as sync_err:
                                    print(f"   ⚠️ Erro de conexão com Dashboard remoto: {sync_err}")
                                    
                        except Exception as db_err:
                            logging.error(f"Database Error: {db_err}")
        
        except serial.SerialException as e:
            if "PermissionError" in str(e) or "Acesso negado" in str(e):
                print(f"\n[X] ERRO: A porta {SERIAL_PORT} está ocupada ou com acesso negado.")
                print("[?] DICA: Feche o Monitor Serial do Arduino IDE ou outros programas usando a porta.")
                print("[*] Tentando novamente em 5 segundos...\n")
                arduino = None
                time.sleep(5)
            else:
                logging.error(f"Serial connection lost: {e}")
                arduino = None
                time.sleep(2)

        except Exception as e:
            logging.error(f"Error: {e}")
            arduino = None
            time.sleep(2)
        
        # Interval control
        time.sleep(INTERVALO_LEITURA)

if __name__ == "__main__":
    main()
