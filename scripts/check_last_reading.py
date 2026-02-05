import requests
import datetime
import json

url = "https://vinicolacaldart.onrender.com/api/historico"

try:
    print(f"Fetching history from {url}...")
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            # Assuming the list is ordered or we can find the max date
            # But usually history returns latest first or we sort it.
            # Let's inspect the first item.
            print(f"Found {len(data)} records.")
            latest = data[0] # Usually latest if sorted desc, but let's verify
            
            print(f"Found {len(data)} records. Last 5 entries:")
            for i, record in enumerate(data[:5]):
                 ts = record.get('data_hora', 'N/A')
                 temp = record.get('temperatura', 'N/A')
                 print(f"[{i+1}] {ts} - Temp: {temp}°C")
            
        else:
            print("No records found.")
    else:
        print(f"Error: Status code {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"Error fetching data: {e}")
