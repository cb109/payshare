#!/bin/sh
gunicorn payshare.wsgi:application --workers 2 --bind 0.0.0.0:1234
