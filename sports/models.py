from django.db import models


class Sport(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'sports'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=5, blank=True)

    class Meta:
        db_table = 'countries'
        ordering = ['name']
        verbose_name_plural = 'countries'

    def __str__(self):
        return self.name


class League(models.Model):
    name = models.CharField(max_length=150)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='leagues')
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='leagues')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'leagues'
        ordering = ['name']
        unique_together = ['name', 'sport']

    def __str__(self):
        return f'{self.name} ({self.sport.name})'


class SportEvent(models.Model):
    STATUS_SCHEDULED = 'scheduled'
    STATUS_LIVE = 'live'
    STATUS_FINISHED = 'finished'
    STATUS_CANCELLED = 'cancelled'
    STATUS_POSTPONED = 'postponed'
    STATUS_CHOICES = [
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_LIVE, 'Live'),
        (STATUS_FINISHED, 'Finished'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_POSTPONED, 'Postponed'),
    ]

    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='events')
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='events')
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    home_team = models.CharField(max_length=150)
    away_team = models.CharField(max_length=150)
    home_score = models.PositiveIntegerField(null=True, blank=True)
    away_score = models.PositiveIntegerField(null=True, blank=True)
    start_time = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    home_odds = models.DecimalField(max_digits=6, decimal_places=2, default=1.00)
    draw_odds = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    away_odds = models.DecimalField(max_digits=6, decimal_places=2, default=1.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sport_events'
        ordering = ['start_time']

    def __str__(self):
        return f'{self.home_team} vs {self.away_team}'

    @property
    def is_live(self):
        return self.status == self.STATUS_LIVE


class Market(models.Model):
    event = models.ForeignKey(SportEvent, on_delete=models.CASCADE, related_name='markets')
    name = models.CharField(max_length=150)
    options = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'markets'
        ordering = ['name']

    def __str__(self):
        return f'{self.event} - {self.name}'
