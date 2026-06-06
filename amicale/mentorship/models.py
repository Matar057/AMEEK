from django.db import models
from django.contrib.auth.models import User


class Mentorship(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
        ('terminee', 'Terminée'),
    ]

    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentorships_as_mentor')
    mentee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentorships_as_mentee')
    statut = models.CharField('Statut', max_length=20, choices=STATUT_CHOICES, default='en_attente')
    message = models.TextField('Message du demandeur', blank=True)
    date_debut = models.DateTimeField('Date de début', null=True, blank=True)
    date_fin = models.DateTimeField('Date de fin', null=True, blank=True)
    commentaires = models.TextField('Commentaires', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Mentorat'
        verbose_name_plural = 'Mentorats'
        unique_together = ('mentor', 'mentee')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.mentee} → {self.mentor} ({self.get_statut_display()})"
