# payment/admin.py
from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'status', 'payment_date')
    list_filter = ('status', 'payment_date')
    search_fields = ('transaction_id', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('user', 'transaction_id', 'amount', 'status')
        }),
        ('Timestamps', {
            'fields': ('payment_date', 'created_at', 'updated_at')
        }),
    )