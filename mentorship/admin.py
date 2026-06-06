from django.contrib import admin
from .models import Mentorship


@admin.register(Mentorship)
class MentorshipAdmin(admin.ModelAdmin):
    list_display = ('mentee', 'mentor', 'statut', 'date_debut', 'created_at')
    list_filter = ('statut',)
    search_fields = ('mentor__username', 'mentee__username', 'mentor__first_name', 'mentee__first_name')
