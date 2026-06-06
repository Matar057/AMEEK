from django import forms
from .models import Document

TW_INPUT = 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amicale focus:border-transparent'


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('titre', 'description', 'categorie', 'fichier', 'est_public')
        widgets = {
            'titre': forms.TextInput(attrs={'class': TW_INPUT}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': TW_INPUT}),
            'fichier': forms.FileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:bg-amicale file:text-white hover:file:bg-amicale-fonce'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categorie'].widget.attrs['class'] = TW_INPUT