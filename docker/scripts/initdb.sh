#!/bin/bash
docker exec threatmatrix_uwsgi python3 manage.py makemigrations
docker exec threatmatrix_uwsgi python3 manage.py migrate
docker exec -ti threatmatrix_uwsgi python3 manage.py createsuperuser \
--username admin --email admin@admin.com --first_name admin --last_name admin
