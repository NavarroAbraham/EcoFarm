from django.core.exceptions import ValidationError

from .models import Order


class OrderBuilder:
    def build(self, data):
        order = Order(
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            total_amount=data['total_amount'],
        )
        # Ensure the model is valid before saving
        order.full_clean()
        order.save()
        return order
