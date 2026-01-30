import serial.tools.list_ports
import time
import sys

def get_ports():
    return {p.device: p for p in serial.tools.list_ports.comports()}

def monitor_ports():
    print("Iniciando monitoramento de portas COM...")
    print("Mexa nos fios e observe se a porta aparece/desaparece.")
    print("Pressione Ctrl+C para parar.")
    print("-" * 50)
    
    last_ports = get_ports()
    
    # Print initial state
    if last_ports:
        print("Portas atuais:")
        for dev, p in last_ports.items():
            print(f"  [EXISTE] {dev}: {p.description}")
    else:
        print("  [NENHUMA] Nenhuma porta detectada inicialmente.")
        
    print("-" * 50)

    try:
        while True:
            current_ports = get_ports()
            
            # Check for new ports
            for dev in current_ports:
                if dev not in last_ports:
                    print(f"[{time.strftime('%H:%M:%S')}] [+] CONECTADO: {dev} - {current_ports[dev].description}")
            
            # Check for removed ports
            for dev in last_ports:
                if dev not in current_ports:
                    print(f"[{time.strftime('%H:%M:%S')}] [-] DESCONECTADO: {dev} - {last_ports[dev].description}")
            
            last_ports = current_ports
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nMonitoramento encerrado.")

if __name__ == "__main__":
    monitor_ports()
