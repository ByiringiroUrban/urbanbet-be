from rest_framework import serializers
from .models import Bet


class BetItemSerializer(serializers.Serializer):
    event = serializers.CharField()
    selection = serializers.CharField()
    odds = serializers.FloatField(min_value=1.0)


class PlaceBetSerializer(serializers.ModelSerializer):
    items = BetItemSerializer(many=True)

    class Meta:
        model = Bet
        fields = ['items', 'amount', 'currency']

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('At least one bet item is required.')
        return value

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than zero.')
        return value

    def create(self, validated_data):
        items = validated_data['items']
        total_odds = 1.0
        for item in items:
            total_odds *= item['odds']

        amount = float(validated_data['amount'])
        potential_winnings = round(amount * total_odds, 2)

        user = self.context['request'].user

        if user.balance < validated_data['amount']:
            raise serializers.ValidationError({'amount': 'Insufficient balance.'})

        bet = Bet.objects.create(
            user=user,
            items=items,
            total_odds=round(total_odds, 4),
            amount=amount,
            potential_winnings=potential_winnings,
            currency=validated_data.get('currency', user.currency),
        )

        user.balance -= validated_data['amount']
        user.save(update_fields=['balance'])

        return bet


class BetSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Bet
        fields = [
            'id', 'user', 'user_email', 'items', 'total_odds',
            'amount', 'potential_winnings', 'status', 'currency', 'created_at',
        ]
        read_only_fields = ['id', 'user', 'total_odds', 'potential_winnings', 'status', 'created_at']


class BetStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bet
        fields = ['status']

    def validate_status(self, value):
        allowed = [Bet.STATUS_WON, Bet.STATUS_LOST, Bet.STATUS_CANCELLED]
        if value not in allowed:
            raise serializers.ValidationError(f'Status must be one of: {allowed}')
        return value

    def update(self, instance, validated_data):
        new_status = validated_data['status']
        old_status = instance.status

        instance.status = new_status
        instance.save(update_fields=['status'])

        if new_status == Bet.STATUS_WON and old_status == Bet.STATUS_PENDING:
            user = instance.user
            user.balance += instance.potential_winnings
            user.save(update_fields=['balance'])
        elif new_status == Bet.STATUS_CANCELLED and old_status == Bet.STATUS_PENDING:
            user = instance.user
            user.balance += instance.amount
            user.save(update_fields=['balance'])

        return instance
