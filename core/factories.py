from uuid import uuid4

from .models import Payment


class PaymentProcessor:
    def charge(self, order, provider):
        raise NotImplementedError


class DummyPaymentProcessor(PaymentProcessor):
    def charge(self, order, provider):
        payment = Payment.objects.create(
            order=order,
            provider=provider,
            amount=order.total_amount,
            status=Payment.STATUS_PENDING,
        )
        payment.mark_succeeded(external_id=str(uuid4()))
        order.mark_paid()
        return payment


class PaymentProcessorFactory:
    def get_processor(self, provider):
        if provider == 'dummy':
            return DummyPaymentProcessor()
        raise ValueError(f"Proveedor no soportado: {provider}")
