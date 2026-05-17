#!/usr/bin/env python3
"""
Test script for the Flask order service
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health/")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_create_order():
    """Test order creation"""
    data = {
        "customer_name": "Test User",
        "customer_email": "test@example.com",
        "total_amount": 99.99,
        "provider": "dummy"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v2/orders/",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Create order: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 201
    except Exception as e:
        print(f"Create order failed: {e}")
        return False

def test_get_order(order_id):
    """Test getting an order"""
    try:
        response = requests.get(f"{BASE_URL}/api/v2/orders/{order_id}/")
        print(f"Get order {order_id}: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Get order failed: {e}")
        return False

def test_create_certificate():
    """Test certificate creation"""
    data = {
        "customer_name": "John Doe",
        "customer_email": "john.doe@example.com",
        "course_name": "Python Web Development"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v2/certificates/",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Create certificate: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"Certificate created: {result['certificate']['certificate_number']}")
            # Store certificate ID for later tests
            global test_certificate_id
            test_certificate_id = result['certificate']['id']
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Create certificate failed: {e}")
        return False

def test_get_certificate(certificate_id):
    """Test getting a certificate"""
    try:
        response = requests.get(f"{BASE_URL}/api/v2/certificates/{certificate_id}/")
        print(f"Get certificate {certificate_id}: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Certificate: {result['certificate_number']} - {result['customer_name']}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Get certificate failed: {e}")
        return False

def test_download_certificate(certificate_id):
    """Test downloading certificate PDF"""
    try:
        response = requests.get(f"{BASE_URL}/api/v2/certificates/{certificate_id}/download/")
        print(f"Download certificate {certificate_id}: {response.status_code}")
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'application/pdf' in content_type:
                print(f"PDF downloaded successfully ({len(response.content)} bytes)")
                return True
            else:
                print(f"Wrong content type: {content_type}")
                return False
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Download certificate failed: {e}")
        return False

# Global variable to store certificate ID for testing
test_certificate_id = None

if __name__ == "__main__":
    print("Testing Flask Service (Orders & Certificates)...")

    # Test health
    if not test_health():
        print("Health check failed!")
        exit(1)

    # Test create order
    if not test_create_order():
        print("Create order failed!")
        exit(1)

    # Test certificate functionality
    print("\n--- Testing Certificate Functionality ---")

    if not test_create_certificate():
        print("Create certificate failed!")
        exit(1)

    if test_certificate_id:
        if not test_get_certificate(test_certificate_id):
            print("Get certificate failed!")
            exit(1)

        if not test_download_certificate(test_certificate_id):
            print("Download certificate failed!")
            exit(1)

    print("All tests passed!")