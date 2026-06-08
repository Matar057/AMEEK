release: python manage.py collectstatic --noinput; python manage.py migrate
web: python manage.py migrate; gunicorn amicale.wsgi --log-file -
