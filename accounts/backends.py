from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q


class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if username is None or password is None:
            return None

        user = self._find_user(username)
        if user is None:
            User().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def _find_user(self, username):
        try:
            return User.objects.get(Q(email__iexact=username) | Q(username__iexact=username))
        except User.DoesNotExist:
            return self._find_user_by_phone(username)
        except User.MultipleObjectsReturned:
            return None

    def _find_user_by_phone(self, username):
        from django.db.utils import DatabaseError
        from profiles.models import Profile
        try:
            profile = Profile.objects.get(telephone=username)
            return profile.user
        except (Profile.DoesNotExist, Profile.MultipleObjectsReturned):
            return None
        except DatabaseError:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
