from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('titre', 'categorie', 'uploader', 'est_public', 'created_at')
    list_filter = ('categorie', 'est_public')
    search_fields = ('titre', 'description')
