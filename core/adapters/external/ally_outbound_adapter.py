from __future__ import annotations

from decimal import Decimal

from core.adapters.mappers import map_order_to_external_dto
from core.application.dtos import ExternalOrderDTO
from core.application.errors import ExternalServiceError
from core.application.ports import ExternalOrderProviderPort


_DEFAULT_DATASET = {
    'ALLY-SAMPLE-1': ExternalOrderDTO(
        external_id='ALLY-SAMPLE-1',
        status='received',
        total_amount=Decimal('25.00'),
        buyer_name='Sample Buyer',
        buyer_email='sample@example.com',
    )
}


class StubExternalOrderProvider(ExternalOrderProviderPort):
    def __init__(self, dataset=None):
        self.dataset = dataset or _DEFAULT_DATASET

    def create_order(self, order) -> ExternalOrderDTO:
        external_id = f"ALLY-{order.id}"
        external_dto = map_order_to_external_dto(order, external_id, status='received')
        self.dataset[external_id] = external_dto
        return external_dto

    def fetch_order(self, external_id: str) -> ExternalOrderDTO:
        if external_id not in self.dataset:
            raise ExternalServiceError(f"Orden externa {external_id} no encontrada")
        return self.dataset[external_id]
