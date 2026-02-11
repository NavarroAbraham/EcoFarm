from django.contrib import admin

from .models import Order, Payment


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ('id', 'customer_name', 'customer_email', 'total_amount', 'status', 'created_at')
	list_filter = ('status', 'created_at')
	search_fields = ('customer_name', 'customer_email')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
	list_display = ('id', 'order', 'provider', 'amount', 'status', 'created_at')
	list_filter = ('status', 'provider', 'created_at')
	search_fields = ('order__customer_name', 'order__customer_email', 'external_id')

# Register your models here.
