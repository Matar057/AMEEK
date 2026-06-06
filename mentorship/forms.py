from django import forms
from .models import Mentorship

TW_INPUT = 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amicale focus:border-transparent'


class MentorshipRequestForm(forms.ModelForm):
    class Meta:
        model = Mentorship
        fields = ('message',)
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'class': TW_INPUT, 'placeholder': 'Expliquez pourquoi vous souhaitez ce mentor...'}),
        }
        labels = {
            'message': 'Votre message',
        }


class MentorshipResponseForm(forms.ModelForm):
    class Meta:
        model = Mentorship
        fields = ('statut', 'commentaires')
        widgets = {
            'commentaires': forms.Textarea(attrs={'rows': 3, 'class': TW_INPUT}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['statut'].widget.attrs['class'] = TW_INPUT