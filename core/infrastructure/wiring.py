from __future__ import annotations

from core.adapters.external import FlaskCertificateAdapter, StubExternalOrderProvider
from core.adapters.payments import DummyPaymentGateway
from core.adapters.persistence import DjangoCertificateRepository, DjangoOrderRepository
from core.application.use_cases import (
    CreateOrderUseCase,
    ProcessPaymentUseCase,
    GenerateCertificateUseCase,
    GetOrderUseCase,
    GetOrderDetailUseCase,
    ListUserOrdersUseCase,
    CreateCertificateUseCase,
    GetCertificateUseCase,
    ListUserCertificatesUseCase,
    GetCertificateByOrderUseCase,
)


class OrderPaymentFacade:
    def __init__(self, create_use_case: CreateOrderUseCase, payment_use_case: ProcessPaymentUseCase):
        self.create_use_case = create_use_case
        self.payment_use_case = payment_use_case

    def create_order_and_payment(self, request):
        order = self.create_use_case.execute(request)
        return self.payment_use_case.execute(order.id, request.provider)


def build_order_repository():
    return DjangoOrderRepository()


def build_payment_gateway():
    return DummyPaymentGateway()


def build_order_payment_facade():
    repository = build_order_repository()
    payment_gateway = build_payment_gateway()
    create_use_case = CreateOrderUseCase(repository)
    payment_use_case = ProcessPaymentUseCase(repository, payment_gateway)
    return OrderPaymentFacade(create_use_case, payment_use_case)


def build_certificate_provider():
    return FlaskCertificateAdapter()


def build_certificate_use_case():
    return GenerateCertificateUseCase(build_certificate_provider())


def build_external_order_provider():
    return StubExternalOrderProvider()


def build_get_order_use_case():
    return GetOrderUseCase(build_order_repository())


def build_get_order_detail_use_case():
    return GetOrderDetailUseCase(build_order_repository())


def build_list_user_orders_use_case():
    return ListUserOrdersUseCase(build_order_repository())


def build_certificate_repository():
    return DjangoCertificateRepository()


def build_create_certificate_use_case():
    return CreateCertificateUseCase(
        order_repository=build_order_repository(),
        certificate_provider=build_certificate_provider(),
        certificate_repository=build_certificate_repository(),
    )


def build_get_certificate_use_case():
    return GetCertificateUseCase(build_certificate_repository())


def build_list_user_certificates_use_case():
    return ListUserCertificatesUseCase(build_certificate_repository())


def build_get_certificate_by_order_use_case():
    return GetCertificateByOrderUseCase(build_certificate_repository())
