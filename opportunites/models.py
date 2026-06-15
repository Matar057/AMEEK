from django.db import models
from django.contrib.auth.models import User


class Offre(models.Model):
    TYPE_CHOICES = [
        ('stage', 'Stage'),
        ('emploi', 'Emploi'),
        ('concours', 'Concours'),
    ]

    titre = models.CharField('Titre', max_length=200)
    type = models.CharField('Type', max_length=20, choices=TYPE_CHOICES)
    description = models.TextField('Description')
    organisation = models.CharField('Organisation / Entreprise', max_length=200, blank=True)
    lieu = models.CharField('Lieu', max_length=200, blank=True)
    date_limite = models.DateField('Date limite', null=True, blank=True)
    lien = models.URLField('Lien', blank=True)
    contact_email = models.EmailField('Email de contact', blank=True)
    auteur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='offres')
    est_public = models.BooleanField('Publique', default=True)
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Offre'
        verbose_name_plural = 'Offres'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_type_display()} — {self.titre}'
