from __future__ import annotations

from datetime import datetime
from urllib.parse import urljoin
import os
import requests

from core.application.dtos import CertificateRequest, CertificateDTO
from core.application.errors import ExternalServiceError
from core.application.ports import CertificateProviderPort


class FlaskCertificateAdapter(CertificateProviderPort):
    def __init__(self, base_url: str | None = None, timeout: int = 10):
        self.base_url = base_url or os.getenv('FLASK_CERTIFICATE_URL', 'http://localhost:5000/')
        if not self.base_url.endswith('/'):
            self.base_url += '/'
        self.timeout = timeout

    def generate_certificate(self, request: CertificateRequest) -> CertificateDTO:
        endpoint = urljoin(self.base_url, 'api/v2/certificates/')
        try:
            response = requests.post(
                endpoint,
                json={
                    'customer_name': request.customer_name,
                    'customer_email': request.customer_email,
                    'course_name': request.course_name,
                },
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise ExternalServiceError('No fue posible conectar al servicio de certificados') from exc

        if response.status_code >= 400:
            raise ExternalServiceError(f"Error del servicio de certificados: {response.text}")

        payload = response.json()
        certificate = payload.get('certificate') or {}
        issued_date = certificate.get('issued_date')
        parsed_date = None
        if issued_date:
            try:
                parsed_date = datetime.fromisoformat(issued_date)
            except ValueError:
                parsed_date = None

        return CertificateDTO(
            id=certificate.get('id', 0),
            customer_name=certificate.get('customer_name', request.customer_name),
            customer_email=certificate.get('customer_email', request.customer_email),
            course_name=certificate.get('course_name', request.course_name),
            certificate_number=certificate.get('certificate_number'),
            external_certificate_id=str(certificate.get('id')) if certificate.get('id') is not None else None,
            issued_date=parsed_date,
            download_url=payload.get('download_url'),
        )

    def download_certificate_pdf(self, download_url: str) -> bytes:
        if not download_url:
            raise ExternalServiceError('URL de descarga no disponible')
        try:
            response = requests.get(urljoin(self.base_url, download_url.lstrip('/')), timeout=self.timeout)
        except requests.RequestException as exc:
            raise ExternalServiceError('No fue posible descargar el certificado') from exc
        if response.status_code >= 400:
            raise ExternalServiceError(f"Error al descargar certificado: {response.text}")
        return response.content
