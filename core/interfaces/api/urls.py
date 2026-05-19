from django.urls import path

from core.interfaces.api import views

app_name = 'api'

urlpatterns = [
    path('v1/orders/', views.OrderPaymentAPIView.as_view(), name='api-order-create'),
    path('v1/orders/<int:pk>/', views.OrderDetailAPIView.as_view(), name='api-order-detail'),
    path('v1/ally/orders/', views.AllyOrderCreateAPIView.as_view(), name='api-ally-order-create'),
    path('v1/ally/orders/<str:external_id>/', views.ExternalOrderFetchAPIView.as_view(), name='api-ally-order-fetch'),
    path('v1/account/orders/', views.MyAccountOrdersAPIView.as_view(), name='api-account-orders'),
    path('v1/account/orders/<int:pk>/', views.MyAccountOrderDetailAPIView.as_view(), name='api-account-order-detail'),
    path('v1/certificates/', views.CertificateListAPIView.as_view(), name='api-certificates'),
    path('v1/certificates/create/', views.CertificateCreateAPIView.as_view(), name='api-certificates-create'),
    path('v1/certificates/<int:pk>/', views.CertificateDetailAPIView.as_view(), name='api-certificates-detail'),
    path('v1/certificates/<int:pk>/download/', views.CertificateDownloadAPIView.as_view(), name='api-certificates-download'),
]
