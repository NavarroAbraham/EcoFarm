from .builders import OrderBuilder
from .factories import PaymentProcessorFactory


class OrderPaymentService:
    def __init__(self, builder=None, factory=None):
        self.builder = builder or OrderBuilder()
        self.factory = factory or PaymentProcessorFactory()

    def create_order_and_payment(self, data):
        """Main business flow: build the order and process a payment.

        Any business-related validation is done in the builder or the models.
        The factory selects a suitable payment processor implementation.
        """
        order = self.builder.build(data)
        processor = self.factory.get_processor(data['provider'])
        payment = processor.charge(order, data['provider'])
        return order, payment

    def get_order(self, pk):
        from .models import Order

        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise ValueError(f"Order with id {pk} not found")
