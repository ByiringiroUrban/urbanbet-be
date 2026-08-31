from django.db import models
from django.conf import settings


class Transaction(models.Model):
    TYPE_DEPOSIT = 'deposit'
    TYPE_WITHDRAWAL = 'withdrawal'
    TYPE_BET_PLACE = 'bet_place'
    TYPE_BET_WIN = 'bet_win'
    TYPE_BET_REFUND = 'bet_refund'
    TYPE_CHOICES = [
        (TYPE_DEPOSIT, 'Deposit'),
        (TYPE_WITHDRAWAL, 'Withdrawal'),
        (TYPE_BET_PLACE, 'Bet Placed'),
        (TYPE_BET_WIN, 'Bet Win'),
        (TYPE_BET_REFUND, 'Bet Refund'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    METHOD_MOMO = 'momo'
    METHOD_AIRTEL = 'airtel'
    METHOD_IREMBO = 'irembo'
    METHOD_CARD = 'card'
    METHOD_SYSTEM = 'system'
    METHOD_CHOICES = [
        (METHOD_MOMO, 'MTN MoMo'),
        (METHOD_AIRTEL, 'Airtel Money'),
        (METHOD_IREMBO, 'Irembo Pay'),
        (METHOD_CARD, 'Card'),
        (METHOD_SYSTEM, 'System'),
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
        related_name='transactions',
    )
    transaction_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, default=METHOD_SYSTEM)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default=CURRENCY_RWF)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reference = models.CharField(max_length=100, blank=True)
    pawapay_id = models.CharField(max_length=36, blank=True, db_index=True)
    description = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.transaction_type} #{self.pk} - {self.user.email} ({self.currency} {self.amount})'
