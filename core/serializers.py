from rest_framework import serializers

from .models import Order, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id',
            'provider',
            'amount',
            'status',
            'external_id',
            'created_at',
        ]
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'customer_name',
            'customer_email',
            'total_amount',
            'status',
            'created_at',
            'payments',
        ]
        read_only_fields = fields


class OrderPaymentInputSerializer(serializers.Serializer):
    # provider is kept as free text so that the factory/service layer is
    # responsible for deciding whether the provider is supported. This makes it
    # possible to return a 409 Conflict when an unknown provider is supplied.
    customer_name = serializers.CharField(max_length=120)
    customer_email = serializers.EmailField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    provider = serializers.CharField(max_length=40)

    def validate_total_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('El monto debe ser mayor que 0.')
        return value
