#!/usr/bin/env python3
import requests
import json

data = {
    "customer_name": "Test User",
    "customer_email": "test@example.com",
    "total_amount": 99.99,
    "provider": "dummy"
}

try:
    response = requests.post(
        "http://localhost:5000/api/v2/orders/",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    print(f"Status: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
