import datetime
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Sauvegarde la base de données et les médias dans une archive zip'

    def add_arguments(self, parser):
        parser.add_argument('--output', '-o', type=str, help='Dossier de destination (défaut: backup/)')

    def handle(self, *args, **options):
        backup_dir = Path(options['output'] or settings.BASE_DIR / 'backup')
        backup_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_name = f'ameek_backup_{now}.zip'
        archive_path = backup_dir / archive_name

        db_path = settings.DATABASES['default']['NAME']
        media_root = settings.MEDIA_ROOT

        with tempfile.TemporaryDirectory() as tmp:
            db_copy = Path(tmp) / 'db.sqlite3'
            shutil.copy2(db_path, db_copy)

            media_copy = Path(tmp) / 'media'
            if os.path.isdir(media_root):
                shutil.copytree(media_root, media_copy, dirs_exist_ok=True)

            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(db_copy, 'db.sqlite3')
                if media_copy.exists():
                    for root, dirs, files in os.walk(media_copy):
                        for f in files:
                            file_path = Path(root) / f
                            arcname = str(file_path.relative_to(tmp))
                            zf.write(file_path, arcname)

        self.stdout.write(self.style.SUCCESS(f'Sauvegarde créée : {archive_path}'))
        self.stdout.write(f'  Base de données : {db_path}')
        if os.path.isdir(media_root):
            self.stdout.write(f'  Médias          : {media_root}/')
