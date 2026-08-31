from django.contrib import admin
from .models import Bet


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_odds', 'amount', 'potential_winnings', 'status', 'currency', 'created_at']
    list_filter = ['status', 'currency']
    search_fields = ['user__email']
    readonly_fields = ['total_odds', 'potential_winnings', 'items', 'created_at', 'updated_at']
    list_editable = ['status']
    date_hierarchy = 'created_at'
