from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('order/', views.OrderPaymentCreateView.as_view(), name='order-create'),
]
