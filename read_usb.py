import serial
import time

try:
    # Tenta conectar na COM3 (USB do Arduino)
    # Se mudar de porta, altere aqui
    ser = serial.Serial('COM3', 9600, timeout=1)
    print("Conectado na COM3! Aguardando dados do Arduino...\n")
    print("-" * 40)

    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"[Arduino Diz]: {line}")
        time.sleep(0.1)

except Exception as e:
    print(f"Erro ao conectar na COM3: {e}")
    print("Verifique se o Monitor Serial do Arduino IDE está fechado!")
