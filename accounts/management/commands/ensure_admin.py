from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from decouple import config


class Command(BaseCommand):
    help = 'Crée un superadmin si aucun n\'existe'

    def handle(self, *args, **options):
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write('Un superadmin existe déjà.')
            return

        username = config('ADMIN_USERNAME', default='admin')
        email = config('ADMIN_EMAIL', default='admin@ameek.sn')
        password = config('ADMIN_PASSWORD', default='')

        if not password:
            raise CommandError(
                'ADMIN_PASSWORD must be set in environment. '
                'Run: python manage.py ensure_admin --password=<strong-password>'
            )

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Superadmin "{username}" créé avec succès.'))
