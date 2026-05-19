from __future__ import annotations

from core.application.dtos import AllyOrderRequest, CreateOrderRequest, ExternalOrderDTO
from core.domain.entities import Certificate, Order, Payment


def map_order_model_to_entity(order_model) -> Order:
    return Order(
        id=order_model.id,
        customer_name=order_model.customer_name,
        customer_email=order_model.customer_email,
        total_amount=order_model.total_amount,
        status=order_model.status,
        product_id=order_model.product_id,
        user_id=order_model.user_id,
        created_at=order_model.created_at,
    )


def map_payment_model_to_entity(payment_model) -> Payment:
    return Payment(
        id=payment_model.id,
        order_id=payment_model.order_id,
        provider=payment_model.provider,
        amount=payment_model.amount,
        status=payment_model.status,
        external_id=payment_model.external_id,
        created_at=payment_model.created_at,
    )


def map_certificate_model_to_entity(certificate_model) -> Certificate:
    return Certificate(
        id=certificate_model.id,
        customer_name=certificate_model.order.customer_name if certificate_model.order else '',
        customer_email=certificate_model.order.customer_email if certificate_model.order else '',
        course_name=certificate_model.course_name,
        certificate_number=certificate_model.certificate_number,
        external_certificate_id=certificate_model.external_certificate_id,
        issued_date=certificate_model.issued_date,
        download_url=certificate_model.external_download_url,
        order_id=certificate_model.order_id,
        user_id=certificate_model.user_id,
    )


def map_ally_order_to_create_request(payload: AllyOrderRequest) -> CreateOrderRequest:
    return CreateOrderRequest(
        customer_name=payload.buyer_name,
        customer_email=payload.buyer_email,
        total_amount=payload.amount,
        provider=payload.payment_provider,
    )


def map_order_to_external_dto(order: Order, external_id: str, status: str) -> ExternalOrderDTO:
    return ExternalOrderDTO(
        external_id=external_id,
        status=status,
        total_amount=order.total_amount,
        buyer_name=order.customer_name,
        buyer_email=order.customer_email,
    )
