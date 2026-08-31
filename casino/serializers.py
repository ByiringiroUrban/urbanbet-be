from rest_framework import serializers
from .models import CasinoGame, CasinoGameSession


class CasinoGameSerializer(serializers.ModelSerializer):
    image_src = serializers.SerializerMethodField()

    class Meta:
        model = CasinoGame
        fields = [
            'id', 'title', 'provider', 'category', 'image_src',
            'is_new', 'is_popular', 'is_active', 'rtp', 'min_bet', 'max_bet',
        ]

    def get_image_src(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return obj.image_url or ''


class CasinoGameWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CasinoGame
        fields = [
            'title', 'provider', 'category', 'image', 'image_url',
            'is_new', 'is_popular', 'is_active', 'rtp', 'min_bet', 'max_bet',
        ]


class StartSessionSerializer(serializers.Serializer):
    game_id = serializers.IntegerField()
    currency = serializers.ChoiceField(choices=['USD', 'RWF'], default='RWF')


class CasinoGameSessionSerializer(serializers.ModelSerializer):
    game_title = serializers.CharField(source='game.title', read_only=True)
    game_provider = serializers.CharField(source='game.provider', read_only=True)
    net_result = serializers.DecimalField(source='net_result', max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = CasinoGameSession
        fields = [
            'id', 'game', 'game_title', 'game_provider',
            'status', 'amount_wagered', 'amount_won', 'net_result',
            'currency', 'started_at', 'ended_at',
        ]
        read_only_fields = ['id', 'status', 'amount_wagered', 'amount_won', 'started_at', 'ended_at']
