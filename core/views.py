from django.shortcuts import render
from django.views import View

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.core.exceptions import ValidationError

from .forms import OrderPaymentForm
from .services import OrderPaymentService
from .serializers import (
    OrderPaymentInputSerializer,
    OrderSerializer,
    PaymentSerializer,
)



def home(request):
    """Vista principal del sitio"""
    return render(request, 'core/home.html')


class OrderPaymentCreateView(View):
    template_name = 'core/order_payment_form.html'
    success_template_name = 'core/order_payment_success.html'

    def get(self, request):
        form = OrderPaymentForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = OrderPaymentForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        service = OrderPaymentService()
        order, payment = service.create_order_and_payment(form.cleaned_data)
        context = {
            'order': order,
            'payment': payment,
        }
        return render(request, self.success_template_name, context)


class OrderPaymentAPIView(APIView):
    """API endpoint to create an order along with a payment."""

    def post(self, request):
        serializer = OrderPaymentInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            service = OrderPaymentService()
            order, payment = service.create_order_and_payment(serializer.validated_data)
        except ValueError as exc:
            # unsupported provider or other business conflict
            return Response({'detail': str(exc)}, status=status.HTTP_409_CONFLICT)
        except ValidationError as exc:
            # builder/model validation failed
            return Response(exc.message_dict or str(exc), status=status.HTTP_400_BAD_REQUEST)

        output = {
            'order': OrderSerializer(order).data,
            'payment': PaymentSerializer(payment).data,
        }
        return Response(output, status=status.HTTP_201_CREATED)


class OrderDetailAPIView(APIView):
    """Retrieve a single order by its primary key."""

    def get(self, request, pk):
        from .models import Order

        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
