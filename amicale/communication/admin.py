from django.contrib import admin
from .models import Publication, Notification, Message


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type', 'auteur', 'est_public', 'publie_le')
    list_filter = ('type', 'est_public', 'publie_le')
    search_fields = ('titre', 'contenu')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'destinataire', 'type', 'lu', 'cree_le')
    list_filter = ('type', 'lu', 'cree_le')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sujet', 'expediteur', 'destinataire', 'lu', 'envoye_le')
    list_filter = ('lu', 'envoye_le')
    search_fields = ('sujet', 'corps')
