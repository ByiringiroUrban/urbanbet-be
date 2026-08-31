from django.db import models
from django.conf import settings


class Bet(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_WON = 'won'
    STATUS_LOST = 'lost'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_WON, 'Won'),
        (STATUS_LOST, 'Lost'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    CURRENCY_USD = 'USD'
    CURRENCY_RWF = 'RWF'
    CURRENCY_CHOICES = [
        (CURRENCY_USD, 'USD'),
        (CURRENCY_RWF, 'RWF'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bets',
    )
    items = models.JSONField(default=list)
    total_odds = models.DecimalField(max_digits=10, decimal_places=4)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    potential_winnings = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default=CURRENCY_RWF)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bets'
        ordering = ['-created_at']

    def __str__(self):
        return f'Bet #{self.pk} by {self.user.email} - {self.status}'
