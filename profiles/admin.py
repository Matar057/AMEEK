from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Profile


class TypeMembreFilter(admin.SimpleListFilter):
    title = _('type de membre')
    parameter_name = 'type_membre'

    def lookups(self, request, model_admin):
        return [
            ('nouveau_bachelier', _('Nouveau bachelier')),
            ('etudiant', _('Étudiant')),
            ('professionnel', _('Professionnel')),
            ('diplome', _('Diplômé')),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'nouveau_bachelier':
            return queryset.filter(
                promotion_bac__isnull=False, promotion_bac__gte=2024,
                profession='', universite=''
            )
        if value == 'etudiant':
            return queryset.filter(universite__gt='').exclude(profession__gt='')
        if value == 'professionnel':
            return queryset.filter(profession__gt='')
        if value == 'diplome':
            return queryset.filter(
                promotion_bac__isnull=True
            ).exclude(profession__gt='').exclude(universite__gt='')
        return queryset


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'type_membre', 'promotion_bac', 'serie', 'universite', 'filiere', 'est_mentor')
    list_filter = ('est_mentor', 'serie', 'promotion_bac', TypeMembreFilter)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'universite', 'filiere', 'profession')
    list_select_related = ('user',)
