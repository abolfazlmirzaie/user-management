#!/bin/bash

echo "Waiting for PostgreSQL..."
sleep 5

python manage.py makemigrations --noinput
python manage.py migrate --noinput

exec "$@"