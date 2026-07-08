from django import forms
from .models import Payment

TW_INPUT = 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amicale focus:border-transparent'


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ('montant', 'reference', 'date_paiement', 'notes')
        widgets = {
            'date_paiement': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': TW_INPUT}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': TW_INPUT}),
            'montant': forms.NumberInput(attrs={'class': TW_INPUT}),
            'reference': forms.TextInput(attrs={'class': TW_INPUT}),
        }