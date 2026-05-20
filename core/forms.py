from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Order, UserProfile


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


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=False)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, initial=UserProfile.ROLE_BUYER)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email', '')
        if commit:
            user.save()
            UserProfile.objects.update_or_create(
                user=user,
                defaults={'role': self.cleaned_data.get('role', UserProfile.ROLE_BUYER)},
            )
        return user
