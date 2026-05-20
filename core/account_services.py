from __future__ import annotations

from dataclasses import dataclass
from django.db.models import Sum

from .models import Certificate, Order, Product
from .roles import ROLE_BUYER, ROLE_PROVIDER, get_user_role


@dataclass(frozen=True)
class ProviderAccountSummary:
    products: list[Product]
    orders: list[Order]
    metrics: dict


def build_provider_account_summary(user, products_limit: int = 8, orders_limit: int = 8) -> ProviderAccountSummary:
    provider_products_qs = Product.objects.filter(provider=user).order_by('-created_at')
    provider_orders_qs = Order.objects.filter(product__provider=user).select_related('product')
    metrics = {
        'products_count': provider_products_qs.count(),
        'orders_count': provider_orders_qs.count(),
        'paid_orders_count': provider_orders_qs.filter(status=Order.STATUS_PAID).count(),
        'total_revenue': provider_orders_qs.filter(status=Order.STATUS_PAID).aggregate(
            Sum('total_amount')
        )['total_amount__sum'] or 0,
    }
    return ProviderAccountSummary(
        products=list(provider_products_qs[:products_limit]),
        orders=list(provider_orders_qs.order_by('-created_at')[:orders_limit]),
        metrics=metrics,
    )


def build_indicator_context(user) -> dict:
    role = get_user_role(user)
    indicator_title = 'Indicadores de confianza'
    indicator_subtitle = 'Transparencia y control en cada operación.'
    indicator_cards = []

    if role == ROLE_PROVIDER:
        provider_orders = Order.objects.filter(product__provider=user)
        total_revenue = provider_orders.filter(status=Order.STATUS_PAID).aggregate(
            Sum('total_amount')
        )['total_amount__sum'] or 0
        indicator_title = 'Resumen del proveedor'
        indicator_subtitle = 'Tu desempeño y operaciones recientes.'
        indicator_cards = [
            {
                'badge': 'Productos',
                'value': Product.objects.filter(provider=user).count(),
                'description': 'Productos publicados en la plataforma.',
            },
            {
                'badge': 'Pedidos',
                'value': provider_orders.count(),
                'description': 'Pedidos asociados a tus productos.',
            },
            {
                'badge': 'Ingresos',
                'value': f"${total_revenue:.2f}",
                'description': 'Ventas confirmadas en EcoFarm.',
            },
            {
                'badge': 'Soporte',
                'value': '24/6',
                'description': 'Acompañamiento operativo para tus entregas.',
            },
        ]
    elif role == ROLE_BUYER:
        buyer_orders = Order.objects.filter(user=user)
        total_spent = buyer_orders.filter(status=Order.STATUS_PAID).aggregate(
            Sum('total_amount')
        )['total_amount__sum'] or 0
        indicator_title = 'Tu actividad'
        indicator_subtitle = 'Resumen de tus compras en EcoFarm.'
        indicator_cards = [
            {
                'badge': 'Pedidos',
                'value': buyer_orders.count(),
                'description': 'Órdenes realizadas por tu cuenta.',
            },
            {
                'badge': 'Pagos',
                'value': buyer_orders.filter(status=Order.STATUS_PAID).count(),
                'description': 'Pagos confirmados con éxito.',
            },
            {
                'badge': 'Certificados',
                'value': Certificate.objects.filter(user=user).count(),
                'description': 'Certificados disponibles para tus compras.',
            },
            {
                'badge': 'Total',
                'value': f"${total_spent:.2f}",
                'description': 'Monto acumulado en compras pagadas.',
            },
        ]
    else:
        total_orders = Order.objects.count()
        paid_orders = Order.objects.filter(status=Order.STATUS_PAID).count()
        total_revenue = Order.objects.filter(status=Order.STATUS_PAID).aggregate(
            Sum('total_amount')
        )['total_amount__sum'] or 0
        indicator_cards = [
            {
                'badge': 'Operaciones',
                'value': total_orders,
                'description': 'Órdenes gestionadas por nuestra red de proveedores.',
            },
            {
                'badge': 'Pagos',
                'value': paid_orders,
                'description': 'Pagos procesados con confirmación segura.',
            },
            {
                'badge': 'Ingresos',
                'value': f"${total_revenue:.2f}",
                'description': 'Volumen transaccionado por la comunidad EcoFarm.',
            },
            {
                'badge': 'Soporte',
                'value': '24/6',
                'description': 'Asesoría técnica y logística para tus pedidos.',
            },
        ]

    return {
        'indicator_title': indicator_title,
        'indicator_subtitle': indicator_subtitle,
        'indicator_cards': indicator_cards,
    }
