from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers

from core.application.dtos import (
    CreateOrderRequest,
    OrderPaymentResult,
    AllyOrderRequest,
    ExternalOrderDTO,
    CertificateCreateRequest,
    CertificateDTO,
    CertificateSummaryDTO,
    OrderSummaryDTO,
    OrderDetailDTO,
)


class OrderPaymentInputSerializer(serializers.Serializer):
    customer_name = serializers.CharField(max_length=120)
    customer_email = serializers.EmailField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    provider = serializers.CharField(max_length=40)

    def to_dto(self) -> CreateOrderRequest:
        return CreateOrderRequest(**self.validated_data)


class OrderSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    customer_name = serializers.CharField()
    customer_email = serializers.EmailField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField()
    product_id = serializers.IntegerField(required=False, allow_null=True)
    created_at = serializers.DateTimeField(required=False, allow_null=True)


class PaymentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    order_id = serializers.IntegerField()
    provider = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField()
    external_id = serializers.CharField(required=False, allow_null=True)
    created_at = serializers.DateTimeField(required=False, allow_null=True)


class OrderPaymentResultSerializer(serializers.Serializer):
    order = OrderSerializer()
    payment = PaymentSerializer()

    def to_representation(self, instance: OrderPaymentResult):
        return {
            'order': OrderSerializer(instance.order).data,
            'payment': PaymentSerializer(instance.payment).data,
        }


class OrderSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField()
    created_at = serializers.DateTimeField(required=False, allow_null=True)
    payment_status = serializers.CharField(required=False, allow_null=True)
    payment_provider = serializers.CharField(required=False, allow_null=True)

    def to_representation(self, instance: OrderSummaryDTO):
        return {
            'id': instance.id,
            'total_amount': instance.total_amount,
            'status': instance.status,
            'created_at': instance.created_at,
            'payment_status': instance.payment_status,
            'payment_provider': instance.payment_provider,
        }


class OrderDetailSerializer(serializers.Serializer):
    order = OrderSerializer()
    payments = PaymentSerializer(many=True)

    def to_representation(self, instance: OrderDetailDTO):
        return {
            'order': OrderSerializer(instance.order).data,
            'payments': PaymentSerializer(instance.payments, many=True).data,
        }


class AllyOrderInputSerializer(serializers.Serializer):
    external_reference = serializers.CharField(max_length=100)
    buyer = serializers.DictField(child=serializers.CharField())
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    payment_provider = serializers.CharField(max_length=40)

    def to_dto(self) -> AllyOrderRequest:
        buyer = self.validated_data.get('buyer') or {}
        return AllyOrderRequest(
            external_reference=self.validated_data['external_reference'],
            buyer_name=buyer.get('name', ''),
            buyer_email=buyer.get('email', ''),
            amount=self.validated_data['amount'],
            payment_provider=self.validated_data['payment_provider'],
        )


class ExternalOrderSerializer(serializers.Serializer):
    external_id = serializers.CharField()
    status = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    buyer_name = serializers.CharField(required=False, allow_null=True)
    buyer_email = serializers.EmailField(required=False, allow_null=True)

    def to_representation(self, instance: ExternalOrderDTO):
        return {
            'external_id': instance.external_id,
            'status': instance.status,
            'total_amount': instance.total_amount,
            'buyer_name': instance.buyer_name,
            'buyer_email': instance.buyer_email,
        }


class CertificateCreateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    course_name = serializers.CharField(max_length=200)

    def to_dto(self, user_id: int | None = None) -> CertificateCreateRequest:
        return CertificateCreateRequest(
            order_id=self.validated_data['order_id'],
            course_name=self.validated_data['course_name'],
            user_id=user_id,
        )


class CertificateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    customer_name = serializers.CharField()
    customer_email = serializers.EmailField()
    course_name = serializers.CharField()
    certificate_number = serializers.CharField(required=False, allow_null=True)
    external_certificate_id = serializers.CharField(required=False, allow_null=True)
    issued_date = serializers.DateTimeField(required=False, allow_null=True)
    download_url = serializers.CharField(required=False, allow_null=True)

    def to_representation(self, instance: CertificateDTO):
        return {
            'id': instance.id,
            'customer_name': instance.customer_name,
            'customer_email': instance.customer_email,
            'course_name': instance.course_name,
            'certificate_number': instance.certificate_number,
            'external_certificate_id': instance.external_certificate_id,
            'issued_date': instance.issued_date,
            'download_url': instance.download_url,
        }


class CertificateSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    course_name = serializers.CharField()
    certificate_number = serializers.CharField(required=False, allow_null=True)
    issued_date = serializers.DateTimeField(required=False, allow_null=True)
    order_id = serializers.IntegerField(required=False, allow_null=True)

    def to_representation(self, instance: CertificateSummaryDTO):
        return {
            'id': instance.id,
            'course_name': instance.course_name,
            'certificate_number': instance.certificate_number,
            'issued_date': instance.issued_date,
            'order_id': instance.order_id,
        }
