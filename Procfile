release: python manage.py makemigrations api
release: python manage.py migrate
web: gunicorn wsgi --log-file -
