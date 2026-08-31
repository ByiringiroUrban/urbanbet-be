from django.db import models
from django.conf import settings


class AIPrediction(models.Model):
    CONFIDENCE_LOW = 'low'
    CONFIDENCE_MEDIUM = 'medium'
    CONFIDENCE_HIGH = 'high'

    match = models.CharField(max_length=255)
    prediction = models.CharField(max_length=255)
    confidence = models.PositiveSmallIntegerField(help_text='Confidence percentage 0-100')
    analysis = models.TextField()
    trend = models.CharField(max_length=255, blank=True)
    odds = models.CharField(max_length=20)
    is_featured = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='predictions',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_predictions'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.match} — {self.prediction} ({self.confidence}%)'
