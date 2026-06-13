import os
from pathlib import Path

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amicale.settings')

BASE_DIR = Path(__file__).resolve().parent.parent

application = WhiteNoise(get_wsgi_application())
application.add_files(str(BASE_DIR / 'media'), prefix='media/')
