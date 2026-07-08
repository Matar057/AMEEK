from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from profiles.models import Profile

TW_FORM_INPUT = 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amicale focus:border-transparent'


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': TW_FORM_INPUT}))
    first_name = forms.CharField(max_length=30, required=False, label='Prénom',
                                 widget=forms.TextInput(attrs={'class': TW_FORM_INPUT}))
    last_name = forms.CharField(max_length=30, required=False, label='Nom',
                                widget=forms.TextInput(attrs={'class': TW_FORM_INPUT}))

    statut = forms.ChoiceField(
        choices=[('', '--- Sélectionnez ---')] + Profile.STATUT_CHOICES, required=False, label='Je suis',
        widget=forms.Select(attrs={'class': TW_FORM_INPUT}),
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ('username', 'password1', 'password2'):
            self.fields[field_name].widget.attrs['class'] = TW_FORM_INPUT


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email, téléphone ou nom d\'utilisateur'
        self.fields['username'].widget.attrs['class'] = TW_FORM_INPUT
        self.fields['password'].widget.attrs['class'] = TW_FORM_INPUT