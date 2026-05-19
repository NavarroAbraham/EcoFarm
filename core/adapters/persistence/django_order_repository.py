from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError

from core.adapters.mappers import map_order_model_to_entity, map_payment_model_to_entity
from core.application.errors import NotFoundError, ValidationError
from core.application.ports import OrderRepositoryPort
from core.domain.entities import Order, Payment
from core.models import Order as OrderModel, Payment as PaymentModel


class DjangoOrderRepository(OrderRepositoryPort):
    def create_order(self, order: Order) -> Order:
        order_model = OrderModel(
            customer_name=order.customer_name,
            customer_email=order.customer_email,
            total_amount=order.total_amount,
            status=order.status,
            product_id=order.product_id,
            user_id=order.user_id,
        )
        try:
            order_model.full_clean()
        except DjangoValidationError as exc:
            raise ValidationError(str(exc)) from exc
        order_model.save()
        return map_order_model_to_entity(order_model)

    def get_order(self, order_id: int) -> Order:
        try:
            order_model = OrderModel.objects.get(pk=order_id)
        except OrderModel.DoesNotExist as exc:
            raise NotFoundError(f"Order with id {order_id} not found") from exc
        return map_order_model_to_entity(order_model)

    def update_order_status(self, order_id: int, status: str) -> Order:
        try:
            order_model = OrderModel.objects.get(pk=order_id)
        except OrderModel.DoesNotExist as exc:
            raise NotFoundError(f"Order with id {order_id} not found") from exc
        order_model.status = status
        order_model.save(update_fields=['status'])
        return map_order_model_to_entity(order_model)

    def save_payment(self, payment: Payment) -> Payment:
        payment_model = PaymentModel(
            order_id=payment.order_id,
            provider=payment.provider,
            amount=payment.amount,
            status=payment.status,
            external_id=payment.external_id or '',
        )
        try:
            payment_model.full_clean()
        except DjangoValidationError as exc:
            raise ValidationError(str(exc)) from exc
        payment_model.save()
        return map_payment_model_to_entity(payment_model)

    def list_orders_for_user(self, user_id: int) -> list[Order]:
        orders = OrderModel.objects.filter(user_id=user_id).order_by('-created_at')
        return [map_order_model_to_entity(order) for order in orders]

    def list_payments_for_order(self, order_id: int) -> list[Payment]:
        payments = PaymentModel.objects.filter(order_id=order_id).order_by('created_at')
        return [map_payment_model_to_entity(payment) for payment in payments]
