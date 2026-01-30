import serial
import serial.tools.list_ports
import time
import sys
import os

# Add project root to path to import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import config

print(f"Testing connection to {config.PORTA_SERIAL} at {config.BAUD_RATE} baud...")

try:
    ser = serial.Serial(config.PORTA_SERIAL, config.BAUD_RATE, timeout=5)
    print(f"Successfully opened {config.PORTA_SERIAL}!")
    print("Waiting for data (10s)...")
    
    start_time = time.time()
    while time.time() - start_time < 10:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"Received data: {line}")
        time.sleep(0.1)
    
    print("Finished listening.")
    ser.close()

except Exception as e:
    print(f"Connection failed: {e}")
