gunicorn passenger_wsgi:application -e WSGI_ENV=dev.py -b 127.0.0.1:8000 --debug
