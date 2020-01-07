release: python manage.py makemigrations
release: python manage.py migrate
release: python manage.py makemigrations api
release: python manage.py migrate api
web: gunicorn wsgi --log-file -
