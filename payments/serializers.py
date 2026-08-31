from rest_framework import serializers
from .models import Transaction


class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=1)
    currency = serializers.ChoiceField(choices=['USD', 'RWF'], default='RWF')
    method = serializers.ChoiceField(choices=['momo', 'airtel', 'irembo', 'card'])
    phone_number = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True, default='Deposit')

    def validate(self, attrs):
        method = attrs.get('method')
        phone_number = attrs.get('phone_number', '')
        if method in ('momo', 'airtel') and not phone_number:
            raise serializers.ValidationError({'phone_number': 'Phone number is required for mobile money.'})
        return attrs


class WithdrawalSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=1)
    currency = serializers.ChoiceField(choices=['USD', 'RWF'], default='RWF')
    method = serializers.ChoiceField(choices=['momo', 'airtel', 'card'])
    phone_number = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        method = attrs.get('method')
        if method in ('momo', 'airtel') and not attrs.get('phone_number'):
            raise serializers.ValidationError({'phone_number': 'Phone number is required for mobile money.'})
        return attrs


class TransactionSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'user_email', 'transaction_type', 'method',
            'amount', 'currency', 'status', 'reference', 'pawapay_id',
            'description', 'phone_number', 'created_at',
        ]
        read_only_fields = ['id', 'user', 'status', 'reference', 'created_at']
