from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type_event', 'date', 'lieu', 'organisateur', 'participant_count')
    list_filter = ('type_event', 'date')
    search_fields = ('titre', 'description', 'lieu')
    filter_horizontal = ('participants',)
