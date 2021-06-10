#!/bin/bash

set -e

echo "${0}: running migrations."
python manage.py makemigrations
python manage.py migrate

echo "${0}: collecting statics."

python manage.py collectstatic --noinput


gunicorn penzi.wsgi:application \
    --name penzi \
    --bind 0.0.0.0:8001 \
    --timeout 600 \
    --workers 4 \
    --log-level=info \
    --reload