import requests
import json

url = "https://vinicolacaldart.onrender.com/api/readings"

payload = {
    "temperatura": 25.5,
    "umidade": 60.0,
    "latitude": -29.0,
    "longitude": -51.0,
    "origem": "TestScript"
}

headers = {
    "Content-Type": "application/json"
}

try:
    print(f"Sending POST request to {url}...")
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
