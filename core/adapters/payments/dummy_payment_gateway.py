from __future__ import annotations

from uuid import uuid4

from core.application.errors import ConflictError
from core.application.ports import PaymentGatewayPort
from core.domain.entities import Payment, PaymentStatus


class DummyPaymentGateway(PaymentGatewayPort):
    def __init__(self, supported_providers=None):
        self.supported_providers = supported_providers or {'dummy'}

    def charge(self, order, provider: str) -> Payment:
        if provider not in self.supported_providers:
            raise ConflictError(f"Proveedor no soportado: {provider}")
        return Payment(
            id=None,
            order_id=order.id,
            provider=provider,
            amount=order.total_amount,
            status=PaymentStatus.SUCCEEDED,
            external_id=str(uuid4()),
        )
