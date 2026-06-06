from django import forms
from .models import Event

TW_INPUT = 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amicale focus:border-transparent'


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('titre', 'description', 'type_event', 'date', 'lieu', 'max_participants', 'est_public')
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': TW_INPUT}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': TW_INPUT}),
            'titre': forms.TextInput(attrs={'class': TW_INPUT}),
            'lieu': forms.TextInput(attrs={'class': TW_INPUT}),
            'max_participants': forms.NumberInput(attrs={'class': TW_INPUT}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type_event'].widget.attrs['class'] = TW_INPUT