from django.db import models
from django.contrib.auth.models import User


class Document(models.Model):
    CATEGORY_CHOICES = [
        ('statuts', 'Statuts'),
        ('reglement', 'Règlement intérieur'),
        ('pv', 'Procès-verbal'),
        ('rapport_financier', 'Rapport financier'),
        ('rapport_activite', "Rapport d'activités"),
        ('guide', "Guide d'orientation universitaire"),
        ('autre', 'Autre'),
    ]

    titre = models.CharField('Titre', max_length=200)
    description = models.TextField('Description', blank=True)
    fichier = models.FileField('Fichier', upload_to='documents/')
    categorie = models.CharField('Catégorie', max_length=20, choices=CATEGORY_CHOICES, default='autre')
    uploader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents')
    est_public = models.BooleanField('Document public', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        ordering = ['-created_at']

    def __str__(self):
        return self.titre

    @property
    def extension(self):
        name = self.fichier.name
        if '.' in name:
            return name.rsplit('.', 1)[1].lower()
        return ''
