#!/usr/bin/env bash
python3 manage.py migrate --no-input
#TODO: make docker parameter
python3 manage.py runserver 0.0.0.0:8000