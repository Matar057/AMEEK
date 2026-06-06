from django import forms
from .models import Question, Answer

TW_INPUT = 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amicale focus:border-transparent'


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('titre', 'contenu')
        widgets = {
            'titre': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Ex: Comment intégrer l\'ESP ?'}),
            'contenu': forms.Textarea(attrs={'rows': 6, 'class': TW_INPUT, 'placeholder': 'Décrivez votre question en détail...'}),
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('contenu',)
        widgets = {
            'contenu': forms.Textarea(attrs={'rows': 4, 'class': TW_INPUT, 'placeholder': 'Votre réponse...'}),
        }
        labels = {'contenu': 'Votre réponse'}