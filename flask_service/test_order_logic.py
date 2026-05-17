#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from app import app, db, OrderBuilder, PaymentProcessorFactory, OrderPaymentService

with app.app_context():
    try:
        data = {
            'customer_name': 'Test User',
            'customer_email': 'test@example.com',
            'total_amount': 99.99,
            'provider': 'dummy'
        }
        service = OrderPaymentService()
        order, payment = service.create_order_and_payment(data)
        print(f"SUCCESS: Created order {order.id}")
    except Exception as e:
        import traceback
        print(f"ERROR: {e}")
        print(traceback.format_exc())
