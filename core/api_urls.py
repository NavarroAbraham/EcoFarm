from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('v1/orders/', views.OrderPaymentAPIView.as_view(), name='api-order-create'),
    path('v1/orders/<int:pk>/', views.OrderDetailAPIView.as_view(), name='api-order-detail'),
]