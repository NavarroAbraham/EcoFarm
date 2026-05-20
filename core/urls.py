from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/', views.OrderPaymentCreateView.as_view(), name='order-create'),
    path('account/', views.account_view, name='account'),
    path('account/orders/', views.order_history_view, name='order-history'),
    path('account/orders/<int:order_id>/', views.order_detail_view, name='order-detail'),
    path('account/orders/<int:order_id>/certificate/', views.create_certificate_view, name='certificate-create'),
    path('account/certificates/<int:certificate_id>/', views.certificate_detail_view, name='certificate-detail'),
    path('account/certificates/<int:certificate_id>/download/', views.certificate_download_view, name='certificate-download'),
    path('account/login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('account/logout/', auth_views.LogoutView.as_view(next_page='core:home'), name='logout'),
    path('account/register/', views.register_view, name='register'),
]
