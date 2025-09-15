# users/admin.py:
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser
@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = ('username', 'full_name', 'email', 'is_active', 'is_staff', 'is_subscribed', 'phone_number', 'location')  # added is_subscribed
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'is_subscribed')  #
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'location', 'bio', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Subscription', {'fields': ('is_subscribed',)}),  #
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active')
        }),
    )
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)