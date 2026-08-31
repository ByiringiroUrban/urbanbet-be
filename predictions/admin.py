from django.contrib import admin
from .models import AIPrediction


@admin.register(AIPrediction)
class AIPredictionAdmin(admin.ModelAdmin):
    list_display = ['match', 'prediction', 'confidence', 'odds', 'is_featured', 'created_at']
    list_filter = ['is_featured']
    search_fields = ['match', 'prediction']
    list_editable = ['is_featured']
    date_hierarchy = 'created_at'
