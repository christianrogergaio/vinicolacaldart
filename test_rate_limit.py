from fastapi.testclient import TestClient
from services.api.main import app
import time

client = TestClient(app)

print("--- Testing Rate Limiter Logic ---")

# 1. First Request (Should bypass or be saved, depend on valid sensor data)
# Note: My code saves to SQLite. This test might create local DB entries.
payload = {
    "temperatura": 25.0,
    "umidade": 60.0,
    "latitude": -29.0,
    "longitude": -51.0,
    "origem": "TestScript"
}

print("Sending Request 1...")
response = client.post("/api/readings", json=payload)
print(f"Resp 1: {response.status_code} - {response.json()}")

# 2. Immediate Second Request (Should be ignored)
print("Sending Request 2 (Immediate)...")
response = client.post("/api/readings", json=payload)
print(f"Resp 2: {response.status_code} - {response.json()}")

# 3. Validation
if response.status_code == 200 and "ignored_rate_limit" in response.json().get("status", ""):
    print("SUCCESS: Rate limit is working correctly (returned 200 but status=ignored).")
else:
    print("FAILURE: Rate limit did not trigger as expected.")
