from core.application.dtos import CreateOrderRequest
from core.infrastructure.wiring import build_get_order_use_case, build_order_payment_facade


class OrderPaymentService:
    def __init__(self, facade=None):
        self.facade = facade or build_order_payment_facade()

    def create_order_and_payment(self, data):
        request = CreateOrderRequest(
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            total_amount=data['total_amount'],
            provider=data['provider'],
            product_id=data.get('product_id'),
            user_id=data.get('user_id'),
        )
        result = self.facade.create_order_and_payment(request)
        return result.order, result.payment

    def get_order(self, pk):
        use_case = build_get_order_use_case()
        return use_case.execute(pk)
