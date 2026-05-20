from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class CreateOrderRequest:
    customer_name: str
    customer_email: str
    total_amount: Decimal
    provider: str
    product_id: Optional[int] = None
    user_id: Optional[int] = None


@dataclass(frozen=True)
class OrderDTO:
    id: int
    customer_name: str
    customer_email: str
    total_amount: Decimal
    status: str
    product_id: Optional[int] = None
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass(frozen=True)
class PaymentDTO:
    id: int
    order_id: int
    provider: str
    amount: Decimal
    status: str
    external_id: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass(frozen=True)
class OrderPaymentResult:
    order: OrderDTO
    payment: PaymentDTO


@dataclass(frozen=True)
class CertificateRequest:
    customer_name: str
    customer_email: str
    course_name: str


@dataclass(frozen=True)
class CertificateDTO:
    id: int
    customer_name: str
    customer_email: str
    course_name: str
    certificate_number: Optional[str]
    external_certificate_id: Optional[str]
    issued_date: Optional[datetime]
    download_url: Optional[str]


@dataclass(frozen=True)
class CertificateCreateRequest:
    order_id: int
    course_name: str
    user_id: Optional[int] = None


@dataclass(frozen=True)
class CertificateSummaryDTO:
    id: int
    course_name: str
    certificate_number: Optional[str]
    issued_date: Optional[datetime]
    order_id: Optional[int]


@dataclass(frozen=True)
class OrderSummaryDTO:
    id: int
    total_amount: Decimal
    status: str
    created_at: Optional[datetime]
    payment_status: Optional[str]
    payment_provider: Optional[str]


@dataclass(frozen=True)
class OrderDetailDTO:
    order: OrderDTO
    payments: list[PaymentDTO]


@dataclass(frozen=True)
class AllyOrderRequest:
    external_reference: str
    buyer_name: str
    buyer_email: str
    amount: Decimal
    payment_provider: str


@dataclass(frozen=True)
class ExternalOrderDTO:
    external_id: str
    status: str
    total_amount: Decimal
    buyer_name: Optional[str] = None
    buyer_email: Optional[str] = None
