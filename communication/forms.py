from django import forms
from django.contrib.auth.models import User
from .models import Publication, Message

TW_INPUT = 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amicale focus:border-transparent'


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ('titre', 'contenu', 'type', 'est_public')
        widgets = {
            'titre': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Titre de la publication'}),
            'contenu': forms.Textarea(attrs={'class': TW_INPUT, 'rows': 8, 'placeholder': 'Contenu...'}),
            'type': forms.Select(attrs={'class': TW_INPUT}),
            'est_public': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-amicale focus:ring-amicale'}),
        }


class MessageForm(forms.ModelForm):
    destinataire = forms.CharField(
        label='Destinataire',
        widget=forms.TextInput(attrs={
            'class': TW_INPUT,
            'placeholder': 'Nom d\'utilisateur du destinataire',
            'list': 'member-list',
        }),
    )

    class Meta:
        model = Message
        fields = ('destinataire', 'sujet', 'corps')
        widgets = {
            'sujet': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Sujet du message'}),
            'corps': forms.Textarea(attrs={'class': TW_INPUT, 'rows': 6, 'placeholder': 'Votre message...'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_destinataire(self):
        username = self.cleaned_data['destinataire']
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError("Cet utilisateur n'existe pas.")

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.destinataire = self.cleaned_data['destinataire']
        if commit:
            instance.save()
        return instance
