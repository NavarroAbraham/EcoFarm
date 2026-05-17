#!/usr/bin/env python3
"""
Example script demonstrating certificate generation functionality
"""
import requests
import json

FLASK_URL = "http://localhost:5000"

def create_sample_certificate():
    """Create a sample certificate"""
    certificate_data = {
        "customer_name": "Ana García López",
        "customer_email": "ana.garcia@example.com",
        "course_name": "Arquitectura de Microservicios con Patrón Strangler"
    }

    print("Creating certificate...")
    response = requests.post(
        f"{FLASK_URL}/api/v2/certificates/",
        json=certificate_data,
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code == 201:
        result = response.json()
        certificate = result['certificate']
        download_url = result['download_url']

        print("✅ Certificate created successfully!")
        print(f"   Certificate Number: {certificate['certificate_number']}")
        print(f"   Customer: {certificate['customer_name']}")
        print(f"   Course: {certificate['course_name']}")
        print(f"   Download URL: {FLASK_URL}{download_url}")

        return certificate['id']
    else:
        print(f"❌ Error creating certificate: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def download_certificate(certificate_id):
    """Download the certificate PDF"""
    print(f"\nDownloading certificate PDF (ID: {certificate_id})...")

    response = requests.get(f"{FLASK_URL}/api/v2/certificates/{certificate_id}/download/")

    if response.status_code == 200:
        filename = f"certificate_{certificate_id}.pdf"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"✅ PDF downloaded successfully: {filename}")
        print(f"   File size: {len(response.content)} bytes")
    else:
        print(f"❌ Error downloading PDF: {response.status_code}")
        print(f"   Response: {response.text}")

def get_certificate_details(certificate_id):
    """Get certificate details"""
    print(f"\nGetting certificate details (ID: {certificate_id})...")

    response = requests.get(f"{FLASK_URL}/api/v2/certificates/{certificate_id}/")

    if response.status_code == 200:
        certificate = response.json()
        print("✅ Certificate details retrieved:")
        print(f"   ID: {certificate['id']}")
        print(f"   Number: {certificate['certificate_number']}")
        print(f"   Customer: {certificate['customer_name']}")
        print(f"   Email: {certificate['customer_email']}")
        print(f"   Course: {certificate['course_name']}")
        print(f"   Issued: {certificate['issued_date']}")
    else:
        print(f"❌ Error getting certificate details: {response.status_code}")
        print(f"   Response: {response.text}")

if __name__ == "__main__":
    print("🧾 Certificate Generation Demo")
    print("=" * 40)

    # Create certificate
    certificate_id = create_sample_certificate()

    if certificate_id:
        # Get certificate details
        get_certificate_details(certificate_id)

        # Download PDF
        download_certificate(certificate_id)

        print("\n" + "=" * 40)
        print("🎉 Demo completed successfully!")
        print("📄 Check the generated certificate PDF file")
    else:
        print("❌ Demo failed - could not create certificate")