#!/bin/bash
echo "=== Collecting static files ==="
python manage.py collectstatic --noinput 2>&1
echo "=== Running migrations ==="
python manage.py migrate --noinput 2>&1
echo "=== Ensuring admin user ==="
python manage.py ensure_admin 2>&1
echo "=== Starting gunicorn ==="
gunicorn amicale.wsgi --log-file -
