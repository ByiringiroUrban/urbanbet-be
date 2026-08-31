from django.db import models
from django.conf import settings


class CasinoGame(models.Model):
    CATEGORY_SLOTS = 'slots'
    CATEGORY_TABLE = 'table-games'
    CATEGORY_LIVE = 'live-casino'
    CATEGORY_JACKPOT = 'jackpots'
    CATEGORY_GAME_SHOW = 'game-shows'
    CATEGORY_CHOICES = [
        (CATEGORY_SLOTS, 'Slots'),
        (CATEGORY_TABLE, 'Table Games'),
        (CATEGORY_LIVE, 'Live Casino'),
        (CATEGORY_JACKPOT, 'Jackpots'),
        (CATEGORY_GAME_SHOW, 'Game Shows'),
    ]

    title = models.CharField(max_length=200)
    provider = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_SLOTS)
    image = models.ImageField(upload_to='casino/games/', null=True, blank=True)
    image_url = models.URLField(blank=True)
    is_new = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    rtp = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='Return to player %')
    min_bet = models.DecimalField(max_digits=10, decimal_places=2, default=100)
    max_bet = models.DecimalField(max_digits=14, decimal_places=2, default=100000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'casino_games'
        ordering = ['-is_popular', '-is_new', 'title']

    def __str__(self):
        return f'{self.title} ({self.provider})'


class CasinoGameSession(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_FINISHED = 'finished'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_FINISHED, 'Finished'),
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
        related_name='casino_sessions',
    )
    game = models.ForeignKey(CasinoGame, on_delete=models.CASCADE, related_name='sessions')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    amount_wagered = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    amount_won = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default=CURRENCY_RWF)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'casino_sessions'
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.user.email} — {self.game.title} ({self.status})'

    @property
    def net_result(self):
        return self.amount_won - self.amount_wagered
