#!/bin/sh

cd payshare/purchases/static/client
yarn install --check-files
npm run build

cd -
mkdir -p /public/static/
python manage.py collectstatic --noinput
