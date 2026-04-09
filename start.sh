#!/bin/bash
python manage.py migrate
python manage.py collectstatic --noinput
python create_superuser.py
gunicorn volante_al_hilo.wsgi --log-file -