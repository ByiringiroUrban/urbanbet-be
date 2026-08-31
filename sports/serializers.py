from rest_framework import serializers
from .models import Sport, Country, League, SportEvent, Market


class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ['id', 'name', 'icon', 'is_active', 'order']


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'code']


class LeagueSerializer(serializers.ModelSerializer):
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)

    class Meta:
        model = League
        fields = ['id', 'name', 'sport', 'sport_name', 'country', 'country_name', 'is_active']


class MarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        fields = ['id', 'name', 'options', 'is_active']


class SportEventListSerializer(serializers.ModelSerializer):
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    league_name = serializers.CharField(source='league.name', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)
    is_live = serializers.BooleanField(read_only=True)

    class Meta:
        model = SportEvent
        fields = [
            'id', 'sport', 'sport_name', 'league', 'league_name',
            'country', 'country_name',
            'home_team', 'away_team', 'home_score', 'away_score',
            'start_time', 'status', 'is_live',
            'home_odds', 'draw_odds', 'away_odds',
        ]


class SportEventDetailSerializer(SportEventListSerializer):
    markets = MarketSerializer(many=True, read_only=True)

    class Meta(SportEventListSerializer.Meta):
        fields = SportEventListSerializer.Meta.fields + ['markets', 'created_at', 'updated_at']


class SportEventWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportEvent
        fields = [
            'sport', 'league', 'country',
            'home_team', 'away_team',
            'start_time', 'status',
            'home_odds', 'draw_odds', 'away_odds',
        ]
