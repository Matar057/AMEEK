from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    TYPE_CHOICES = [
        ('orientation', "Journée d'orientation"),
        ('reunion', 'Réunion'),
        ('formation', 'Formation'),
        ('conference', 'Conférence'),
        ('social', 'Événement social'),
        ('autre', 'Autre'),
    ]

    titre = models.CharField('Titre', max_length=200)
    description = models.TextField('Description')
    type_event = models.CharField('Type', max_length=20, choices=TYPE_CHOICES, default='autre')
    date = models.DateTimeField('Date')
    lieu = models.CharField('Lieu', max_length=200)
    organisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='organized_events')
    participants = models.ManyToManyField(User, related_name='events', blank=True)
    max_participants = models.IntegerField('Nombre max de participants', null=True, blank=True)
    est_public = models.BooleanField('Événement public', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Événement'
        verbose_name_plural = 'Événements'
        ordering = ['-date']

    def __str__(self):
        return self.titre

    @property
    def participant_count(self):
        return self.participants.count()

    @property
    def places_restantes(self):
        if self.max_participants:
            return self.max_participants - self.participant_count
        return None
