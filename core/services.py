from .builders import OrderBuilder
from .factories import PaymentProcessorFactory


class OrderPaymentService:
    def __init__(self, builder=None, factory=None):
        self.builder = builder or OrderBuilder()
        self.factory = factory or PaymentProcessorFactory()

    def create_order_and_payment(self, data):
        order = self.builder.build(data)
        processor = self.factory.get_processor(data['provider'])
        payment = processor.charge(order, data['provider'])
        return order, payment
