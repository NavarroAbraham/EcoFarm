from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


class OrderStatus:
    PENDING = 'pending'
    PAID = 'paid'
    FAILED = 'failed'


class PaymentStatus:
    PENDING = 'pending'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'


@dataclass(frozen=True)
class Order:
    id: Optional[int]
    customer_name: str
    customer_email: str
    total_amount: Decimal
    status: str = OrderStatus.PENDING
    product_id: Optional[int] = None
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass(frozen=True)
class Payment:
    id: Optional[int]
    order_id: int
    provider: str
    amount: Decimal
    status: str
    external_id: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass(frozen=True)
class Certificate:
    id: Optional[int]
    customer_name: str
    customer_email: str
    course_name: str
    certificate_number: Optional[str] = None
    external_certificate_id: Optional[str] = None
    issued_date: Optional[datetime] = None
    download_url: Optional[str] = None
    order_id: Optional[int] = None
    user_id: Optional[int] = None
