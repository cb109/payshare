#!/bin/sh

workon payshare &&

pip install pip-tools &&
pip-sync &&

cd payshare/purchases/static/client &&
yarn install --check-files &&
npm run build &&

cd - &&
python manage.py collectstatic --noinput

echo "build finished"
