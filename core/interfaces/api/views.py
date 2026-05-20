from __future__ import annotations

from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.adapters.external import AllyInboundAdapter
from core.application.errors import ApplicationError
from core.infrastructure.wiring import (
    build_order_payment_facade,
    build_get_order_use_case,
    build_get_order_detail_use_case,
    build_list_user_orders_use_case,
    build_external_order_provider,
    build_create_certificate_use_case,
    build_get_certificate_use_case,
    build_list_user_certificates_use_case,
    build_certificate_provider,
)
from core.interfaces.api.errors import handle_application_error
from core.interfaces.api.serializers import (
    OrderPaymentInputSerializer,
    OrderPaymentResultSerializer,
    OrderSerializer,
    AllyOrderInputSerializer,
    ExternalOrderSerializer,
    OrderSummarySerializer,
    OrderDetailSerializer,
    CertificateCreateSerializer,
    CertificateSerializer,
    CertificateSummarySerializer,
)


class OrderPaymentAPIView(APIView):
    """API endpoint to create an order along with a payment."""

    def post(self, request):
        serializer = OrderPaymentInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            facade = build_order_payment_facade()
            result = facade.create_order_and_payment(serializer.to_dto())
        except ApplicationError as exc:
            return handle_application_error(exc)

        return Response(OrderPaymentResultSerializer(result).data, status=status.HTTP_201_CREATED)


class OrderDetailAPIView(APIView):
    """Retrieve a single order by its primary key."""

    def get(self, request, pk):
        try:
            use_case = build_get_order_use_case()
            order = use_case.execute(pk)
        except ApplicationError as exc:
            return handle_application_error(exc)

        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)


class AllyOrderCreateAPIView(APIView):
    """Endpoint for ally inbound orders (external contract)."""

    def post(self, request):
        serializer = AllyOrderInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            adapter = AllyInboundAdapter()
            create_request = adapter.to_create_order_request(serializer.validated_data)
            facade = build_order_payment_facade()
            result = facade.create_order_and_payment(create_request)
        except ApplicationError as exc:
            return handle_application_error(exc)

        return Response(OrderPaymentResultSerializer(result).data, status=status.HTTP_201_CREATED)


class ExternalOrderFetchAPIView(APIView):
    """Fetch an external order from ally provider (outbound adapter)."""

    def get(self, request, external_id):
        try:
            provider = build_external_order_provider()
            external_order = provider.fetch_order(external_id)
        except ApplicationError as exc:
            return handle_application_error(exc)

        return Response(ExternalOrderSerializer(external_order).data, status=status.HTTP_200_OK)


class MyAccountOrdersAPIView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Auth required', 'code': 'UNAUTHORIZED'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            use_case = build_list_user_orders_use_case()
            orders = use_case.execute(request.user.id)
        except ApplicationError as exc:
            return handle_application_error(exc)
        serializer = OrderSummarySerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyAccountOrderDetailAPIView(APIView):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return Response({'error': 'Auth required', 'code': 'UNAUTHORIZED'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            use_case = build_get_order_detail_use_case()
            detail = use_case.execute(pk, user_id=request.user.id)
        except ApplicationError as exc:
            return handle_application_error(exc)
        return Response(OrderDetailSerializer(detail).data, status=status.HTTP_200_OK)


class CertificateCreateAPIView(APIView):
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Auth required', 'code': 'UNAUTHORIZED'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = CertificateCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            use_case = build_create_certificate_use_case()
            certificate = use_case.execute(serializer.to_dto(user_id=request.user.id))
        except ApplicationError as exc:
            return handle_application_error(exc)
        return Response(CertificateSerializer(certificate).data, status=status.HTTP_201_CREATED)


class CertificateDetailAPIView(APIView):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return Response({'error': 'Auth required', 'code': 'UNAUTHORIZED'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            use_case = build_get_certificate_use_case()
            certificate = use_case.execute(pk, user_id=request.user.id)
        except ApplicationError as exc:
            return handle_application_error(exc)
        return Response(CertificateSerializer(certificate).data, status=status.HTTP_200_OK)


class CertificateListAPIView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Auth required', 'code': 'UNAUTHORIZED'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            use_case = build_list_user_certificates_use_case()
            certificates = use_case.execute(request.user.id)
        except ApplicationError as exc:
            return handle_application_error(exc)
        return Response(CertificateSummarySerializer(certificates, many=True).data, status=status.HTTP_200_OK)


class CertificateDownloadAPIView(APIView):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return Response({'error': 'Auth required', 'code': 'UNAUTHORIZED'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            certificate_use_case = build_get_certificate_use_case()
            certificate = certificate_use_case.execute(pk, user_id=request.user.id)
            provider = build_certificate_provider()
            pdf_bytes = provider.download_certificate_pdf(certificate.download_url or '')
        except ApplicationError as exc:
            return handle_application_error(exc)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=\"certificate-{certificate.id}.pdf\"'
        return response
