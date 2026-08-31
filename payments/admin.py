from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'transaction_type', 'method', 'amount', 'currency', 'status', 'reference', 'created_at']
    list_filter = ['transaction_type', 'method', 'status', 'currency']
    search_fields = ['user__email', 'reference', 'phone_number']
    readonly_fields = ['reference', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
