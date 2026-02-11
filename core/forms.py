from django import forms

from .models import Order


class OrderPaymentForm(forms.Form):
    PROVIDER_CHOICES = [
        ('dummy', 'DummyPay'),
    ]

    customer_name = forms.CharField(max_length=120)
    customer_email = forms.EmailField()
    total_amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    provider = forms.ChoiceField(choices=PROVIDER_CHOICES)

    def clean_total_amount(self):
        amount = self.cleaned_data['total_amount']
        if amount <= 0:
            raise forms.ValidationError('El monto debe ser mayor que 0.')
        return amount
