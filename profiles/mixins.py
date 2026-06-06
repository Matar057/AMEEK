from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect


class CarteRequiredMixin(UserPassesTestMixin):
    """Restreint l'accès aux membres ayant acheté leur carte."""

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if self.request.user.is_staff:
            return True
        profile = getattr(self.request.user, 'profile', None)
        return profile is not None and profile.carte_achetee

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)
        messages.warning(self.request,
            'Vous devez acheter votre carte membre pour accéder à cette fonctionnalité.')
        return redirect('profiles:buy_card')
