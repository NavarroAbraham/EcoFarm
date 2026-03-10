from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('order/', views.OrderPaymentCreateView.as_view(), name='order-create'),

    # DRF endpoints
    path('api/orders/', views.OrderPaymentAPIView.as_view(), name='api-order-create'),
    path('api/orders/<int:pk>/', views.OrderDetailAPIView.as_view(), name='api-order-detail'),
]
