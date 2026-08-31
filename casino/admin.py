from django.contrib import admin
from .models import CasinoGame, CasinoGameSession


@admin.register(CasinoGame)
class CasinoGameAdmin(admin.ModelAdmin):
    list_display = ['title', 'provider', 'category', 'rtp', 'min_bet', 'max_bet', 'is_new', 'is_popular', 'is_active']
    list_filter = ['category', 'provider', 'is_new', 'is_popular', 'is_active']
    search_fields = ['title', 'provider']
    list_editable = ['is_new', 'is_popular', 'is_active']


@admin.register(CasinoGameSession)
class CasinoGameSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'game', 'status', 'amount_wagered', 'amount_won', 'currency', 'started_at']
    list_filter = ['status', 'currency']
    search_fields = ['user__email', 'game__title']
    readonly_fields = ['started_at', 'ended_at']
    date_hierarchy = 'started_at'
