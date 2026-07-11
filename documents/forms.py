import mimetypes

from django import forms
from django.core.validators import FileExtensionValidator
from .models import Document

TW_INPUT = 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amicale focus:border-transparent'

ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'jpg', 'jpeg', 'png', 'gif', 'txt', 'csv', 'odt', 'ods']
MAX_FILE_SIZE = 10 * 1024 * 1024


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
        self.fields['fichier'].validators.append(
            FileExtensionValidator(ALLOWED_EXTENSIONS)
        )

    def clean_fichier(self):
        fichier = self.cleaned_data.get('fichier')
        if not fichier:
            return fichier

        if fichier.size > MAX_FILE_SIZE:
            raise forms.ValidationError(f'Le fichier ne doit pas dépasser 10 Mo.')

        ext = fichier.name.rsplit('.', 1)[-1].lower() if '.' in fichier.name else ''
        if ext not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError(
                f'Extension .{ext} non autorisée. Extensions acceptées : {", ".join(ALLOWED_EXTENSIONS)}'
            )

        content_type, _ = mimetypes.guess_type(fichier.name)
        if content_type and content_type.startswith(('text/html', 'application/x-php', 'application/x-sh', 'application/javascript')):
            raise forms.ValidationError('Ce type de fichier n\'est pas autorisé pour des raisons de sécurité.')

        return fichier