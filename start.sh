#!/bin/bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py loaddata stock/fixtures/stock_inicial.json
gunicorn volante_al_hilo.wsgi --log-file -