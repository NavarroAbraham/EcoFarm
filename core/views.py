from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db.models import Sum, Count
from django.urls import reverse

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
from .models import Order, Product
from decimal import Decimal


def _get_cart_from_session(request):
    """Obtiene el carrito de la sesión"""
    if 'cart' not in request.session:
        request.session['cart'] = {}
    return request.session['cart']

def _get_cart_count(request):
    cart = _get_cart_from_session(request)
    return sum(cart.values())


def _calculate_cart_total(cart):
    """Calcula el total del carrito"""
    total = Decimal('0.00')
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            total += product.price * int(quantity)
        except (Product.DoesNotExist, ValueError):
            continue
    return total


def _get_cart_items(cart):
    """Obtiene los items del carrito con detalles del producto"""
    items = []
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            items.append({
                'product': product,
                'quantity': int(quantity),
                'subtotal': product.price * int(quantity)
            })
        except (Product.DoesNotExist, ValueError):
            continue
    return items


def home(request):
    """Vista principal del sitio - Dashboard"""
    # Estadísticas
    total_orders = Order.objects.count()
    paid_orders = Order.objects.filter(status=Order.STATUS_PAID).count()
    
    # Ingresos totales
    total_revenue = Order.objects.filter(
        status=Order.STATUS_PAID
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Productos destacados (los 3 primeros)
    featured_products = Product.objects.all()[:3]
    
    # Carrito
    cart_count = _get_cart_count(request)
    
    context = {
        'total_orders': total_orders,
        'paid_orders': paid_orders,
        'total_revenue': f"{total_revenue:.2f}",
        'featured_products': featured_products,
        'cart_count': cart_count,
    }
    return render(request, 'core/home.html', context)


def shop(request):
    """Vista de tienda - Catálogo de productos"""
    products = Product.objects.all()
    category_counts = (
        Product.objects.values('category')
        .annotate(total=Count('id'))
        .order_by('category')
    )

    context = {
        'products': products,
        'category_counts': category_counts,
        'cart_count': _get_cart_count(request),
    }
    return render(request, 'core/shop.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
        'cart_count': _get_cart_count(request),
    }
    return render(request, 'core/product_detail.html', context)


def add_to_cart(request, product_id):
    """Agrega un producto al carrito y vuelve a la tienda"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart = _get_cart_from_session(request)

        quantity_raw = request.POST.get('quantity', '1')
        try:
            quantity = int(quantity_raw)
        except (TypeError, ValueError):
            quantity = 1
        if quantity < 1:
            quantity = 1

        product_key = str(product.id)
        if product_key in cart:
            cart[product_key] += quantity
        else:
            cart[product_key] = quantity
        
        request.session['cart'] = cart
        request.session.modified = True
        
        # Redirige de nuevo a shop para mostrar otro producto aleatorio
        return redirect('core:shop')
    
    return redirect('core:shop')


def view_cart(request):
    """Muestra el carrito con todos los productos"""
    cart = _get_cart_from_session(request)
    cart_items = _get_cart_items(cart)
    cart_total = _calculate_cart_total(cart)
    
    context = {
        'cart_items': cart_items,
        'cart_total': f"{cart_total:.2f}",
        'cart_total_raw': cart_total,
        'cart_count': sum(cart.values()),
    }
    return render(request, 'core/cart.html', context)


def remove_from_cart(request, product_id):
    """Elimina un producto del carrito"""
    if request.method == 'POST':
        cart = _get_cart_from_session(request)
        product_key = str(product_id)
        
        if product_key in cart:
            del cart[product_key]
        
        request.session['cart'] = cart
        request.session.modified = True
    
    return redirect('core:view_cart')


def checkout_view(request):
    """Vista de checkout - Procesa la compra del carrito completo"""
    cart = _get_cart_from_session(request)
    
    # Si el carrito está vacío, redirige a shop
    if not cart:
        return redirect('core:shop')
    
    cart_items = _get_cart_items(cart)
    total_amount = _calculate_cart_total(cart)
    
    if request.method == 'POST':
        # Obtener datos del formulario
        customer_name = request.POST.get('customer_name', '')
        customer_email = request.POST.get('customer_email', '')
        provider = request.POST.get('provider', 'dummy')
        
        # Validar datos
        if not customer_name or not customer_email:
            context = {
                'cart_items': cart_items,
                'cart_total': f"{total_amount:.2f}",
                'cart_count': _get_cart_count(request),
                'error': 'Por favor completa todos los campos'
            }
            return render(request, 'core/checkout.html', context)
        
        try:
            # Crear orden y pago
            service = OrderPaymentService()
            order_data = {
                'customer_name': customer_name,
                'customer_email': customer_email,
                'total_amount': total_amount,
                'provider': provider,
            }
            order, payment = service.create_order_and_payment(order_data)
            
            # Limpiar carrito
            request.session['cart'] = {}
            request.session.modified = True
            
            context = {
                'order': order,
                'payment': payment,
                'cart_count': _get_cart_count(request),
            }
            return render(request, 'core/order_payment_success.html', context)
            
        except ValueError as exc:
            context = {
                'cart_items': cart_items,
                'cart_total': f"{total_amount:.2f}",
                'cart_count': _get_cart_count(request),
                'error': str(exc)
            }
            return render(request, 'core/checkout.html', context)
        except ValidationError as exc:
            context = {
                'cart_items': cart_items,
                'cart_total': f"{total_amount:.2f}",
                'cart_count': _get_cart_count(request),
                'error': 'Error en validación de datos'
            }
            return render(request, 'core/checkout.html', context)
    
    context = {
        'cart_items': cart_items,
        'cart_total': f"{total_amount:.2f}",
        'cart_count': sum(cart.values()),
    }
    return render(request, 'core/checkout.html', context)


class OrderPaymentCreateView(View):
    template_name = 'core/order_payment_form.html'
    success_template_name = 'core/order_payment_success.html'

    def get(self, request):
        form = OrderPaymentForm()
        return render(request, self.template_name, {'form': form, 'cart_count': _get_cart_count(request)})

    def post(self, request):
        form = OrderPaymentForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form, 'cart_count': _get_cart_count(request)})

        service = OrderPaymentService()
        order, payment = service.create_order_and_payment(form.cleaned_data)
        context = {
            'order': order,
            'payment': payment,
            'cart_count': _get_cart_count(request),
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
