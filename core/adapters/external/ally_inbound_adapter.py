from __future__ import annotations

from decimal import Decimal, InvalidOperation

from core.adapters.mappers import map_ally_order_to_create_request
from core.application.dtos import AllyOrderRequest, CreateOrderRequest
from core.application.errors import AdapterError


class AllyInboundAdapter:
    def to_create_order_request(self, payload: dict) -> CreateOrderRequest:
        try:
            amount = Decimal(str(payload['amount']))
            request = AllyOrderRequest(
                external_reference=str(payload['external_reference']),
                buyer_name=payload['buyer']['name'],
                buyer_email=payload['buyer']['email'],
                amount=amount,
                payment_provider=payload['payment_provider'],
            )
        except (KeyError, TypeError, InvalidOperation) as exc:
            raise AdapterError(f"Falta el campo requerido en el payload externo: {exc}") from exc
        return map_ally_order_to_create_request(request)
