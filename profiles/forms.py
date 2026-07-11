import mimetypes

from django import forms
from .models import Profile

TW_FORM_INPUT = 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amicale focus:border-transparent'
ALLOWED_PHOTO_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp']
MAX_PHOTO_SIZE = 2 * 1024 * 1024


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'telephone', 'photo', 'date_naissance', 'adresse',
            'promotion_bac', 'serie', 'universite', 'filiere',
            'profession', 'bio', 'est_visible',
        )
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': TW_FORM_INPUT}),
            'bio': forms.Textarea(attrs={'rows': 4, 'class': TW_FORM_INPUT}),
            'adresse': forms.Textarea(attrs={'rows': 3, 'class': TW_FORM_INPUT}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = TW_FORM_INPUT
        for field in self.fields:
            if field in ('bio', 'adresse'):
                self.fields[field].required = False
            else:
                self.fields[field].required = True

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if not photo:
            return photo

        if photo.size > MAX_PHOTO_SIZE:
            raise forms.ValidationError('La photo ne doit pas dépasser 2 Mo.')

        ext = photo.name.rsplit('.', 1)[-1].lower() if '.' in photo.name else ''
        if ext not in ALLOWED_PHOTO_EXTENSIONS:
            raise forms.ValidationError(
                f'Extension .{ext} non autorisée. Formats acceptés : {", ".join(ALLOWED_PHOTO_EXTENSIONS)}'
            )

        content_type, _ = mimetypes.guess_type(photo.name)
        if content_type and not content_type.startswith('image/'):
            raise forms.ValidationError('Seules les images sont autorisées.')

        return photo


class ProfileSearchForm(forms.Form):
    q = forms.CharField(label='Rechercher', required=False,
                        widget=forms.TextInput(attrs={'class': TW_FORM_INPUT, 'placeholder': 'Nom, prénom...'}))
    filiere = forms.CharField(label='Filière', required=False,
                              widget=forms.TextInput(attrs={'class': TW_FORM_INPUT, 'placeholder': 'Ex: Informatique'}))
    universite = forms.CharField(label='Université', required=False,
                                 widget=forms.TextInput(attrs={'class': TW_FORM_INPUT, 'placeholder': 'Ex: UCAD'}))
    profession = forms.CharField(label='Profession', required=False,
                                 widget=forms.TextInput(attrs={'class': TW_FORM_INPUT, 'placeholder': 'Ex: Développeur'}))