from django.contrib import admin
from .models import Sport, Country, League, SportEvent, Market


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    search_fields = ['name']


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ['name', 'sport', 'country', 'is_active']
    list_filter = ['sport', 'is_active']
    search_fields = ['name']


class MarketInline(admin.TabularInline):
    model = Market
    extra = 1


@admin.register(SportEvent)
class SportEventAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'sport', 'league', 'start_time', 'status', 'home_odds', 'draw_odds', 'away_odds']
    list_filter = ['sport', 'status', 'league']
    search_fields = ['home_team', 'away_team']
    list_editable = ['status', 'home_odds', 'draw_odds', 'away_odds']
    inlines = [MarketInline]
    date_hierarchy = 'start_time'


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ['name', 'event', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'event__home_team', 'event__away_team']
