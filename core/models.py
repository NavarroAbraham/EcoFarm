from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class Order(models.Model):
	STATUS_PENDING = 'pending'
	STATUS_PAID = 'paid'
	STATUS_FAILED = 'failed'

	STATUS_CHOICES = [
		(STATUS_PENDING, 'Pending'),
		(STATUS_PAID, 'Paid'),
		(STATUS_FAILED, 'Failed'),
	]

	customer_name = models.CharField(max_length=120)
	customer_email = models.EmailField()
	total_amount = models.DecimalField(max_digits=10, decimal_places=2)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Order #{self.pk} - {self.customer_name}"

	def clean(self):
		super().clean()
		# business validation: total must be positive
		if self.total_amount is not None and self.total_amount <= 0:
			raise ValidationError({'total_amount': 'Total amount must be greater than zero.'})

	def mark_paid(self):
		self.status = self.STATUS_PAID
		self.save(update_fields=['status'])

	def mark_failed(self):
		self.status = self.STATUS_FAILED
		self.save(update_fields=['status'])


class Payment(models.Model):
	STATUS_PENDING = 'pending'
	STATUS_SUCCEEDED = 'succeeded'
	STATUS_FAILED = 'failed'

	STATUS_CHOICES = [
		(STATUS_PENDING, 'Pending'),
		(STATUS_SUCCEEDED, 'Succeeded'),
		(STATUS_FAILED, 'Failed'),
	]

	order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
	provider = models.CharField(max_length=40)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
	external_id = models.CharField(max_length=120, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Payment #{self.pk} - {self.provider}"

	def clean(self):
		super().clean()
		# the amount should always be positive and match the order total
		if self.amount is not None and self.amount <= 0:
			raise ValidationError({'amount': 'Payment amount must be positive.'})
		if self.order_id and self.amount != self.order.total_amount:
			raise ValidationError('Payment amount must equal the order total.')

	def mark_succeeded(self, external_id):
		self.status = self.STATUS_SUCCEEDED
		self.external_id = external_id
		self.save(update_fields=['status', 'external_id'])

	def mark_failed(self):
		self.status = self.STATUS_FAILED
		self.save(update_fields=['status'])
