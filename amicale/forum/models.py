from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    titre = models.CharField('Titre', max_length=200)
    contenu = models.TextField('Contenu')
    est_resolu = models.BooleanField('Résolu', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['-created_at']

    def __str__(self):
        return self.titre

    @property
    def answer_count(self):
        return self.answers.count()


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    contenu = models.TextField('Contenu')
    est_solution = models.BooleanField('Solution acceptée', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Réponse'
        verbose_name_plural = 'Réponses'
        ordering = ['-est_solution', 'created_at']

    def __str__(self):
        return f"Réponse de {self.auteur.username} à {self.question.titre[:30]}"
