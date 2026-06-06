from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('member', 'montant', 'mode_paiement', 'date_paiement', 'reference')
    list_filter = ('mode_paiement', 'date_paiement')
    search_fields = ('member__username', 'member__first_name', 'member__last_name', 'reference')
    date_hierarchy = 'date_paiement'
