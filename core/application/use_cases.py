from __future__ import annotations

from decimal import Decimal

from core.application.dtos import (
    CreateOrderRequest,
    OrderDTO,
    PaymentDTO,
    OrderPaymentResult,
    CertificateRequest,
    CertificateDTO,
    CertificateCreateRequest,
    CertificateSummaryDTO,
    OrderSummaryDTO,
    OrderDetailDTO,
)
from core.application.errors import ConflictError, PermissionDeniedError, ValidationError
from core.application.ports import (
    OrderRepositoryPort,
    PaymentGatewayPort,
    CertificateProviderPort,
    CertificateRepositoryPort,
)
from core.domain.entities import Certificate, Order, OrderStatus, PaymentStatus


class CreateOrderUseCase:
    def __init__(self, repository: OrderRepositoryPort):
        self.repository = repository

    def execute(self, request: CreateOrderRequest) -> OrderDTO:
        self._validate_amount(request.total_amount)
        order = Order(
            id=None,
            customer_name=request.customer_name,
            customer_email=request.customer_email,
            total_amount=request.total_amount,
            status=OrderStatus.PENDING,
            product_id=request.product_id,
            user_id=request.user_id,
        )
        saved = self.repository.create_order(order)
        return OrderDTO(
            id=saved.id,
            customer_name=saved.customer_name,
            customer_email=saved.customer_email,
            total_amount=saved.total_amount,
            status=saved.status,
            product_id=saved.product_id,
            user_id=saved.user_id,
            created_at=saved.created_at,
        )

    @staticmethod
    def _validate_amount(amount: Decimal) -> None:
        if amount is None or amount <= 0:
            raise ValidationError('El monto debe ser mayor que 0.')


class ProcessPaymentUseCase:
    def __init__(self, repository: OrderRepositoryPort, payment_gateway: PaymentGatewayPort):
        self.repository = repository
        self.payment_gateway = payment_gateway

    def execute(self, order_id: int, provider: str) -> OrderPaymentResult:
        order = self.repository.get_order(order_id)
        payment = self.payment_gateway.charge(order, provider)
        saved_payment = self.repository.save_payment(payment)

        if saved_payment.status == PaymentStatus.SUCCEEDED:
            updated_order = self.repository.update_order_status(order_id, OrderStatus.PAID)
        elif saved_payment.status == PaymentStatus.FAILED:
            updated_order = self.repository.update_order_status(order_id, OrderStatus.FAILED)
        else:
            updated_order = order

        return OrderPaymentResult(
            order=OrderDTO(
                id=updated_order.id,
                customer_name=updated_order.customer_name,
                customer_email=updated_order.customer_email,
                total_amount=updated_order.total_amount,
                status=updated_order.status,
                product_id=updated_order.product_id,
                user_id=updated_order.user_id,
                created_at=updated_order.created_at,
            ),
            payment=PaymentDTO(
                id=saved_payment.id,
                order_id=saved_payment.order_id,
                provider=saved_payment.provider,
                amount=saved_payment.amount,
                status=saved_payment.status,
                external_id=saved_payment.external_id,
                created_at=saved_payment.created_at,
            ),
        )


class GenerateCertificateUseCase:
    def __init__(self, provider: CertificateProviderPort):
        self.provider = provider

    def execute(self, request: CertificateRequest) -> CertificateDTO:
        return self.provider.generate_certificate(request)


class GetOrderUseCase:
    def __init__(self, repository: OrderRepositoryPort):
        self.repository = repository

    def execute(self, order_id: int) -> OrderDTO:
        order = self.repository.get_order(order_id)
        return OrderDTO(
            id=order.id,
            customer_name=order.customer_name,
            customer_email=order.customer_email,
            total_amount=order.total_amount,
            status=order.status,
            product_id=order.product_id,
            user_id=order.user_id,
            created_at=order.created_at,
        )


class GetOrderDetailUseCase:
    def __init__(self, repository: OrderRepositoryPort):
        self.repository = repository

    def execute(self, order_id: int, user_id: int | None = None) -> OrderDetailDTO:
        order = self.repository.get_order(order_id)
        if user_id is not None and order.user_id != user_id:
            raise PermissionDeniedError('No tienes acceso a esta orden.')
        payments = self.repository.list_payments_for_order(order_id)
        return OrderDetailDTO(
            order=OrderDTO(
                id=order.id,
                customer_name=order.customer_name,
                customer_email=order.customer_email,
                total_amount=order.total_amount,
                status=order.status,
                product_id=order.product_id,
                user_id=order.user_id,
                created_at=order.created_at,
            ),
            payments=[
                PaymentDTO(
                    id=payment.id,
                    order_id=payment.order_id,
                    provider=payment.provider,
                    amount=payment.amount,
                    status=payment.status,
                    external_id=payment.external_id,
                    created_at=payment.created_at,
                )
                for payment in payments
            ],
        )


class ListUserOrdersUseCase:
    def __init__(self, repository: OrderRepositoryPort):
        self.repository = repository

    def execute(self, user_id: int) -> list[OrderSummaryDTO]:
        orders = self.repository.list_orders_for_user(user_id)
        summaries = []
        for order in orders:
            payments = self.repository.list_payments_for_order(order.id)
            last_payment = payments[-1] if payments else None
            summaries.append(
                OrderSummaryDTO(
                    id=order.id,
                    total_amount=order.total_amount,
                    status=order.status,
                    created_at=order.created_at,
                    payment_status=last_payment.status if last_payment else None,
                    payment_provider=last_payment.provider if last_payment else None,
                )
            )
        return summaries


class CreateCertificateUseCase:
    def __init__(
        self,
        order_repository: OrderRepositoryPort,
        certificate_provider: CertificateProviderPort,
        certificate_repository: CertificateRepositoryPort,
    ):
        self.order_repository = order_repository
        self.certificate_provider = certificate_provider
        self.certificate_repository = certificate_repository

    def execute(self, request: CertificateCreateRequest) -> CertificateDTO:
        order = self.order_repository.get_order(request.order_id)
        if request.user_id is not None and order.user_id != request.user_id:
            raise PermissionDeniedError('No tienes acceso a esta orden.')
        existing = self.certificate_repository.get_certificate_by_order(order.id)
        if existing is not None:
            raise ConflictError('La orden ya tiene un certificado asociado.')
        provider_result = self.certificate_provider.generate_certificate(
            CertificateRequest(
                customer_name=order.customer_name,
                customer_email=order.customer_email,
                course_name=request.course_name,
            )
        )
        certificate = Certificate(
            id=None,
            customer_name=provider_result.customer_name,
            customer_email=provider_result.customer_email,
            course_name=provider_result.course_name,
            certificate_number=provider_result.certificate_number,
            external_certificate_id=provider_result.external_certificate_id,
            issued_date=provider_result.issued_date,
            download_url=provider_result.download_url,
            order_id=order.id,
            user_id=order.user_id,
        )
        stored = self.certificate_repository.create_certificate(certificate)
        return CertificateDTO(
            id=stored.id,
            customer_name=stored.customer_name,
            customer_email=stored.customer_email,
            course_name=stored.course_name,
            certificate_number=stored.certificate_number,
            external_certificate_id=stored.external_certificate_id,
            issued_date=stored.issued_date,
            download_url=stored.download_url,
        )


class GetCertificateUseCase:
    def __init__(self, repository: CertificateRepositoryPort):
        self.repository = repository

    def execute(self, certificate_id: int, user_id: int | None = None) -> CertificateDTO:
        certificate = self.repository.get_certificate(certificate_id)
        if user_id is not None and certificate.user_id != user_id:
            raise PermissionDeniedError('No tienes acceso a este certificado.')
        return CertificateDTO(
            id=certificate.id,
            customer_name=certificate.customer_name,
            customer_email=certificate.customer_email,
            course_name=certificate.course_name,
            certificate_number=certificate.certificate_number,
            external_certificate_id=certificate.external_certificate_id,
            issued_date=certificate.issued_date,
            download_url=certificate.download_url,
        )


class ListUserCertificatesUseCase:
    def __init__(self, repository: CertificateRepositoryPort):
        self.repository = repository

    def execute(self, user_id: int) -> list[CertificateSummaryDTO]:
        certificates = self.repository.list_certificates_for_user(user_id)
        return [
            CertificateSummaryDTO(
                id=certificate.id,
                course_name=certificate.course_name,
                certificate_number=certificate.certificate_number,
                issued_date=certificate.issued_date,
                order_id=certificate.order_id,
            )
            for certificate in certificates
        ]


class GetCertificateByOrderUseCase:
    def __init__(self, repository: CertificateRepositoryPort):
        self.repository = repository

    def execute(self, order_id: int, user_id: int | None = None) -> CertificateDTO | None:
        certificate = self.repository.get_certificate_by_order(order_id)
        if certificate is None:
            return None
        if user_id is not None and certificate.user_id != user_id:
            raise PermissionDeniedError('No tienes acceso a este certificado.')
        return CertificateDTO(
            id=certificate.id,
            customer_name=certificate.customer_name,
            customer_email=certificate.customer_email,
            course_name=certificate.course_name,
            certificate_number=certificate.certificate_number,
            external_certificate_id=certificate.external_certificate_id,
            issued_date=certificate.issued_date,
            download_url=certificate.download_url,
        )
