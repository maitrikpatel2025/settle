python3 manage.py migrate
rm -r /var/www/settle/static/*
python3 manage.py collectstatic
