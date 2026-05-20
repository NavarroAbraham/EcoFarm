from django.contrib import admin

from .models import Certificate, Order, Payment, Product, UserProfile


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'category', 'price', 'provider', 'created_at')
	list_filter = ('category', 'created_at')
	search_fields = ('name', 'description', 'provider__username')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ('id', 'customer_name', 'customer_email', 'total_amount', 'status', 'user', 'created_at')
	list_filter = ('status', 'created_at')
	search_fields = ('customer_name', 'customer_email', 'user__username')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
	list_display = ('id', 'order', 'provider', 'amount', 'status', 'created_at')
	list_filter = ('status', 'provider', 'created_at')
	search_fields = ('order__customer_name', 'order__customer_email', 'external_id')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
	list_display = ('id', 'course_name', 'certificate_number', 'order', 'user', 'issued_date', 'created_at')
	list_filter = ('issued_date', 'created_at')
	search_fields = ('certificate_number', 'course_name', 'user__username')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'role')
	list_filter = ('role',)
	search_fields = ('user__username', 'user__email')

# Register your models here.
