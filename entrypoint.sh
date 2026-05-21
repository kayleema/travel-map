#!/bin/sh
set -e

python manage.py migrate --noinput
exec gunicorn travelmap.wsgi:application \
  --bind 0.0.0.0:8000 \
  --access-logfile - --error-logfile - \
  --capture-output \
  --enable-stdio-inheritance \
  --log-level info \
  --workers 1 --threads 4
