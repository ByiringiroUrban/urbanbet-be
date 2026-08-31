from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'name', 'role', 'balance', 'currency', 'is_active', 'date_joined']
    list_filter = ['role', 'currency', 'provider', 'is_active', 'is_staff']
    search_fields = ['email', 'name', 'phone']
    ordering = ['-date_joined']
    readonly_fields = ['date_joined', 'last_login']

    # Override to use email as the identifier (no 'username' field)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name', 'phone', 'avatar')}),
        (_('Finance'), {'fields': ('balance', 'currency')}),
        (_('Auth Provider'), {'fields': ('provider', 'provider_user_id')}),
        (_('Permissions'), {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        (_('Timestamps'), {'fields': ('date_joined', 'last_login')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'currency', 'role'),
        }),
    )
