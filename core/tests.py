from decimal import Decimal
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.adapters.external import AllyInboundAdapter
from core.application.dtos import CertificateDTO, CreateOrderRequest
from core.application.errors import AdapterError, ApplicationError, ValidationError as AppValidationError
from core.application.use_cases import CreateCertificateUseCase, CreateOrderUseCase, ProcessPaymentUseCase
from core.domain.entities import Order, Payment, OrderStatus, PaymentStatus
from core.infrastructure.wiring import build_certificate_repository, build_order_repository

from .models import Certificate, Order as OrderModel, Payment as PaymentModel
from .services import OrderPaymentService


class ModelValidationTests(TestCase):
    def test_order_negative_amount_raises(self):
        order = OrderModel(
            customer_name="Foo",
            customer_email="foo@example.com",
            total_amount=Decimal("-10.00"),
        )
        with self.assertRaises(ValidationError):
            order.full_clean()

    def test_payment_amount_mismatch_raises(self):
        order = OrderModel.objects.create(
            customer_name="Bar",
            customer_email="bar@example.com",
            total_amount=Decimal("50.00"),
        )
        payment = PaymentModel(
            order=order,
            provider="dummy",
            amount=Decimal("40.00"),
            status=PaymentModel.STATUS_PENDING,
        )
        with self.assertRaises(ValidationError):
            payment.full_clean()


class _FakeOrderRepository:
    def __init__(self):
        self._orders = {}
        self._payments = {}
        self._next_id = 1
        self._next_payment_id = 1

    def create_order(self, order: Order) -> Order:
        order_id = self._next_id
        self._next_id += 1
        stored = Order(
            id=order_id,
            customer_name=order.customer_name,
            customer_email=order.customer_email,
            total_amount=order.total_amount,
            status=order.status,
            user_id=order.user_id,
        )
        self._orders[order_id] = stored
        return stored

    def get_order(self, order_id: int) -> Order:
        return self._orders[order_id]

    def update_order_status(self, order_id: int, status: str) -> Order:
        order = self._orders[order_id]
        updated = Order(
            id=order.id,
            customer_name=order.customer_name,
            customer_email=order.customer_email,
            total_amount=order.total_amount,
            status=status,
            user_id=order.user_id,
        )
        self._orders[order_id] = updated
        return updated

    def save_payment(self, payment: Payment) -> Payment:
        payment_id = self._next_payment_id
        self._next_payment_id += 1
        stored = Payment(
            id=payment_id,
            order_id=payment.order_id,
            provider=payment.provider,
            amount=payment.amount,
            status=payment.status,
            external_id=payment.external_id,
        )
        self._payments[payment_id] = stored
        return stored


class _FakePaymentGateway:
    def charge(self, order: Order, provider: str) -> Payment:
        return Payment(
            id=None,
            order_id=order.id,
            provider=provider,
            amount=order.total_amount,
            status=PaymentStatus.SUCCEEDED,
            external_id='FAKE-123',
        )


class UseCaseTests(TestCase):
    def test_create_order_use_case_validates_amount(self):
        repo = _FakeOrderRepository()
        use_case = CreateOrderUseCase(repo)
        with self.assertRaises(AppValidationError):
            use_case.execute(
                CreateOrderRequest(
                    customer_name='Alice',
                    customer_email='alice@example.com',
                    total_amount=Decimal('-5.00'),
                    provider='dummy',
                )
            )

    def test_process_payment_updates_status(self):
        repo = _FakeOrderRepository()
        order = repo.create_order(
            Order(
                id=None,
                customer_name='Bob',
                customer_email='bob@example.com',
                total_amount=Decimal('10.00'),
                status=OrderStatus.PENDING,
            )
        )
        use_case = ProcessPaymentUseCase(repo, _FakePaymentGateway())
        result = use_case.execute(order.id, 'dummy')
        self.assertEqual(result.order.status, OrderStatus.PAID)
        self.assertEqual(result.payment.status, PaymentStatus.SUCCEEDED)


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
        self.assertEqual(order.status, OrderStatus.PAID)
        self.assertEqual(payment.status, PaymentStatus.SUCCEEDED)
        self.assertEqual(payment.amount, order.total_amount)

    def test_get_order_not_found_raises(self):
        service = OrderPaymentService()
        with self.assertRaises(ApplicationError):
            service.get_order(9999)


class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('api:api-order-create')

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
        url = reverse('api:api-order-detail', kwargs={'pk': order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], order.id)

    def test_get_nonexistent_returns_404(self):
        url = reverse('api:api-order-detail', kwargs={'pk': 123456})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_ally_order_creates_order(self):
        url = reverse('api:api-ally-order-create')
        payload = {
            'external_reference': 'EXT-100',
            'buyer': {'name': 'Ally User', 'email': 'ally@example.com'},
            'amount': '12.50',
            'payment_provider': 'dummy',
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('order', response.data)
        self.assertIn('payment', response.data)

    def test_get_external_order_sample(self):
        url = reverse('api:api-ally-order-fetch', kwargs={'external_id': 'ALLY-SAMPLE-1'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['external_id'], 'ALLY-SAMPLE-1')


class AdapterTests(TestCase):
    def test_ally_adapter_missing_field_raises(self):
        adapter = AllyInboundAdapter()
        with self.assertRaises(AdapterError):
            adapter.to_create_order_request({'amount': '10.00'})


class _StubCertificateProvider:
    def generate_certificate(self, request):
        return CertificateDTO(
            id=99,
            customer_name=request.customer_name,
            customer_email=request.customer_email,
            course_name=request.course_name,
            certificate_number='CERT-123',
            external_certificate_id='EXT-99',
            issued_date=None,
            download_url='/api/v2/certificates/99/download/',
        )

    def download_certificate_pdf(self, download_url: str) -> bytes:
        return b'%PDF-FAKE-CERT%'


class CertificateAndAccountTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='member',
            email='member@example.com',
            password='pass12345',
        )

    def test_account_requires_login(self):
        response = self.client.get(reverse('core:account'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_account_shows_orders_and_certificates(self):
        order = OrderModel.objects.create(
            customer_name='User',
            customer_email='member@example.com',
            total_amount=Decimal('20.00'),
            status=OrderModel.STATUS_PAID,
            user=self.user,
        )
        Certificate.objects.create(
            order=order,
            user=self.user,
            course_name='Compra EcoFarm',
            certificate_number='CERT-ABC',
            external_certificate_id='EXT-ABC',
            external_download_url='/api/v2/certificates/1/download/',
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse('core:account'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Compra EcoFarm')

    def test_order_detail_forbidden_for_other_user(self):
        other = get_user_model().objects.create_user(username='other', password='pass12345')
        order = OrderModel.objects.create(
            customer_name='User',
            customer_email='member@example.com',
            total_amount=Decimal('20.00'),
            status=OrderModel.STATUS_PAID,
            user=other,
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse('core:order-detail', kwargs={'order_id': order.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_certificate_create_api(self):
        order = OrderModel.objects.create(
            customer_name='User',
            customer_email='member@example.com',
            total_amount=Decimal('30.00'),
            status=OrderModel.STATUS_PAID,
            user=self.user,
        )
        use_case = CreateCertificateUseCase(
            order_repository=build_order_repository(),
            certificate_provider=_StubCertificateProvider(),
            certificate_repository=build_certificate_repository(),
        )
        self.client.force_login(self.user)
        with patch('core.interfaces.api.views.build_create_certificate_use_case', return_value=use_case):
            response = self.client.post(
                reverse('api:api-certificates-create'),
                {'order_id': order.id, 'course_name': 'Compra EcoFarm'},
                format='json',
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Certificate.objects.filter(order=order).exists())

    def test_certificate_download_api(self):
        order = OrderModel.objects.create(
            customer_name='User',
            customer_email='member@example.com',
            total_amount=Decimal('30.00'),
            status=OrderModel.STATUS_PAID,
            user=self.user,
        )
        certificate = Certificate.objects.create(
            order=order,
            user=self.user,
            course_name='Compra EcoFarm',
            certificate_number='CERT-XYZ',
            external_certificate_id='EXT-XYZ',
            external_download_url='/api/v2/certificates/99/download/',
        )
        self.client.force_login(self.user)
        with patch('core.interfaces.api.views.build_certificate_provider', return_value=_StubCertificateProvider()):
            response = self.client.get(reverse('api:api-certificates-download', kwargs={'pk': certificate.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
