from django.contrib.auth.mixins import LoginRequiredMixin


class CarteRequiredMixin(LoginRequiredMixin):
    """Authentification requise pour accéder à cette fonctionnalité."""
