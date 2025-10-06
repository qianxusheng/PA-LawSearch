import requests
import json

BASE_URL = "http://localhost:5000"

# Test retrieve endpoint (for ranking team)
print("Testing /retrieve endpoint...\n")

data = {
    "query": "murder evidence",
    "top_k": 10
}

response = requests.post(f"{BASE_URL}/retrieve", json=data)
print(f"Status: {response.status_code}")
print(f"Response:\n{json.dumps(response.json(), indent=2)}")
