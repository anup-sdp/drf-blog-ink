# payment/serializers.py
from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'username', 'transaction_id', 
            'amount', 'status', 'payment_date', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']