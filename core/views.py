from django.shortcuts import render
from django.views import View

from .forms import OrderPaymentForm
from .services import OrderPaymentService


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
