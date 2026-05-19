from __future__ import annotations

from typing import Protocol

from core.application.dtos import CertificateRequest, CertificateDTO, ExternalOrderDTO
from core.domain.entities import Order, Payment, Certificate


class OrderRepositoryPort(Protocol):
    def create_order(self, order: Order) -> Order:
        ...

    def get_order(self, order_id: int) -> Order:
        ...

    def update_order_status(self, order_id: int, status: str) -> Order:
        ...

    def save_payment(self, payment: Payment) -> Payment:
        ...

    def list_orders_for_user(self, user_id: int) -> list[Order]:
        ...

    def list_payments_for_order(self, order_id: int) -> list[Payment]:
        ...


class PaymentGatewayPort(Protocol):
    def charge(self, order: Order, provider: str) -> Payment:
        ...


class ExternalOrderProviderPort(Protocol):
    def create_order(self, order: Order) -> ExternalOrderDTO:
        ...

    def fetch_order(self, external_id: str) -> ExternalOrderDTO:
        ...


class CertificateProviderPort(Protocol):
    def generate_certificate(self, request: CertificateRequest) -> CertificateDTO:
        ...

    def download_certificate_pdf(self, download_url: str) -> bytes:
        ...


class CertificateRepositoryPort(Protocol):
    def create_certificate(self, certificate: Certificate) -> Certificate:
        ...

    def get_certificate(self, certificate_id: int) -> Certificate:
        ...

    def list_certificates_for_user(self, user_id: int) -> list[Certificate]:
        ...

    def get_certificate_by_order(self, order_id: int) -> Certificate | None:
        ...
