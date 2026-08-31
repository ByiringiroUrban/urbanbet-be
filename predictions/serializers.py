from rest_framework import serializers
from .models import AIPrediction


class AIPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIPrediction
        fields = [
            'id', 'match', 'prediction', 'confidence',
            'analysis', 'trend', 'odds', 'is_featured', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class AIPredictionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIPrediction
        fields = [
            'match', 'prediction', 'confidence',
            'analysis', 'trend', 'odds', 'is_featured',
        ]

    def validate_confidence(self, value):
        if not (0 <= value <= 100):
            raise serializers.ValidationError('Confidence must be between 0 and 100.')
        return value
