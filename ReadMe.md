Steps to Install WellNet Server

1. sudo apt-get install libjpeg-dev libxml2-dev libxslt1-dev python3-dev python3-pip python3-lxml libcairo2 libpango1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info libmysqlclient-dev memcached
2. Create virtual env
3. source venv/bin/activate
4. pip3 install -r requirements.txt
5. rm db.sqlite3
6. python3 manage.py makemigrations services django_cron
7. python3 manage.py migrate
8. python3 manage.py loaddata services/fixtures/initial_data.json
9. python3 manage.py createsuperuser
10. python3 manage.py runserver 0.0.0.0:8084
