#!/usr/bin/env sh
set -e

if [[ "$1" == 'runserver' ]]; then
    python3 manage.py migrate
    python3 manage.py runserver 0:8080
elif [[ "$1" == 'serve' ]]; then
    python3 manage.py migrate
    python3 manage.py collectstatic --noinput
    exec gunicorn backend.wsgi
