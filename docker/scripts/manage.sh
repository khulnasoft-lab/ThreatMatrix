#!/bin/bash
docker exec -ti threatmatrix_uwsgi python3 manage.py "$@"
