from django import forms
from .models import Offre


class OffreForm(forms.ModelForm):
    class Meta:
        model = Offre
        fields = ['titre', 'type', 'description', 'organisation', 'lieu',
                  'date_limite', 'lien', 'contact_email', 'est_public']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-amicale'}),
            'titre': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-amicale'}),
            'organisation': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-amicale'}),
            'lieu': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-amicale'}),
            'date_limite': forms.DateInput(attrs={'type': 'date', 'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-amicale'}),
            'lien': forms.URLInput(attrs={'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-amicale'}),
            'contact_email': forms.EmailInput(attrs={'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-amicale'}),
            'type': forms.Select(attrs={'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-amicale'}),
            'est_public': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300'}),
        }
