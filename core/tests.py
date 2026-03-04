from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from .models import Order, Payment
from .builders import OrderBuilder
from .services import OrderPaymentService


class ModelValidationTests(TestCase):
    def test_order_negative_amount_raises(self):
        order = Order(
            customer_name="Foo",
            customer_email="foo@example.com",
            total_amount=Decimal("-10.00"),
        )
        with self.assertRaises(ValidationError):
            order.full_clean()

    def test_payment_amount_mismatch_raises(self):
        order = Order.objects.create(
            customer_name="Bar",
            customer_email="bar@example.com",
            total_amount=Decimal("50.00"),
        )
        payment = Payment(
            order=order,
            provider="dummy",
            amount=Decimal("40.00"),
            status=Payment.STATUS_PENDING,
        )
        with self.assertRaises(ValidationError):
            payment.full_clean()


class BuilderTests(TestCase):
    def test_builder_creates_valid_order(self):
        data = {
            'customer_name': 'Alice',
            'customer_email': 'alice@example.com',
            'total_amount': Decimal('25.00'),
        }
        builder = OrderBuilder()
        order = builder.build(data)
        self.assertIsInstance(order, Order)
        self.assertEqual(order.total_amount, Decimal('25.00'))
        self.assertEqual(order.status, Order.STATUS_PENDING)

    def test_builder_rejects_invalid(self):
        data = {
            'customer_name': 'Bob',
            'customer_email': 'bob@example.com',
            'total_amount': Decimal('-5.00'),
        }
        builder = OrderBuilder()
        with self.assertRaises(ValidationError):
            builder.build(data)


class ServiceLayerTests(TestCase):
    def test_create_order_and_payment_sets_statuses(self):
        data = {
            'customer_name': 'Carol',
            'customer_email': 'carol@example.com',
            'total_amount': Decimal('10.00'),
            'provider': 'dummy',
        }
        service = OrderPaymentService()
        order, payment = service.create_order_and_payment(data)
        self.assertEqual(order.status, Order.STATUS_PAID)
        self.assertEqual(payment.status, Payment.STATUS_SUCCEEDED)
        self.assertEqual(payment.amount, order.total_amount)

    def test_get_order_not_found_raises(self):
        service = OrderPaymentService()
        with self.assertRaises(ValueError):
            service.get_order(9999)


class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('core:api-order-create')

    def test_post_creates_order_and_payment(self):
        payload = {
            'customer_name': 'Diana',
            'customer_email': 'diana@example.com',
            'total_amount': '15.00',
            'provider': 'dummy',
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('order', response.data)
        self.assertIn('payment', response.data)

    def test_post_invalid_data_returns_400(self):
        payload = {'customer_name': '', 'customer_email': 'notanemail'}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_unsupported_provider_returns_409(self):
        payload = {
            'customer_name': 'Eve',
            'customer_email': 'eve@example.com',
            'total_amount': '5.00',
            'provider': 'unknown',
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_get_order_detail(self):
        # create via service to have a real object
        data = {
            'customer_name': 'Frank',
            'customer_email': 'frank@example.com',
            'total_amount': Decimal('20.00'),
            'provider': 'dummy',
        }
        service = OrderPaymentService()
        order, _payment = service.create_order_and_payment(data)
        url = reverse('core:api-order-detail', kwargs={'pk': order.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], order.pk)

    def test_get_nonexistent_returns_404(self):
        url = reverse('core:api-order-detail', kwargs={'pk': 123456})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
