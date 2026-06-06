from django.db import models
from django.contrib.auth.models import User


class Publication(models.Model):
    TYPE_CHOICES = [
        ('activite', "Publication d'activité"),
        ('communique', 'Communiqué officiel'),
        ('info', "Information générale"),
    ]

    titre = models.CharField('Titre', max_length=200)
    contenu = models.TextField('Contenu')
    type = models.CharField('Type', max_length=20, choices=TYPE_CHOICES, default='info')
    auteur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='amicale_publications')
    est_public = models.BooleanField('Publique', default=True)
    publie_le = models.DateTimeField('Publié le', auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Publication'
        verbose_name_plural = 'Publications'
        ordering = ['-publie_le']

    def __str__(self):
        return self.titre


class Notification(models.Model):
    TYPE_CHOICES = [
        ('info', 'Information'),
        ('success', 'Succès'),
        ('warning', 'Avertissement'),
        ('event', 'Événement'),
    ]

    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='amicale_notifications')
    titre = models.CharField('Titre', max_length=200)
    message = models.TextField('Message')
    type = models.CharField('Type', max_length=20, choices=TYPE_CHOICES, default='info')
    lien = models.CharField('Lien', max_length=300, blank=True)
    lu = models.BooleanField('Lu', default=False)
    cree_le = models.DateTimeField('Créé le', auto_now_add=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-cree_le']

    def __str__(self):
        return f'{self.destinataire.username} - {self.titre}'


class Message(models.Model):
    expediteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='amicale_messages_envoyes')
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='amicale_messages_recus')
    sujet = models.CharField('Sujet', max_length=200)
    corps = models.TextField('Message')
    lu = models.BooleanField('Lu', default=False)
    envoye_le = models.DateTimeField('Envoyé le', auto_now_add=True)
    lu_le = models.DateTimeField('Lu le', null=True, blank=True)

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-envoye_le']

    def __str__(self):
        return f'{self.expediteur.username} → {self.destinataire.username}: {self.sujet[:50]}'
