gunicorn passenger_wsgi:application -e WSGI_ENV=dev.py -b 0.0.0.0:8000 --debug
