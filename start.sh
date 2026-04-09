#!/bin/bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.filter(username='admin').first(); u.set_password('contraseña') if u else User.objects.create_superuser('admin', 'admin@email.com', 'contraseña'); u.save() if u else None; print('Listo')"
gunicorn volante_al_hilo.wsgi --log-file -