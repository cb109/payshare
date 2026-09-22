#!/bin/sh

uv sync &&

cd payshare/purchases/static/client &&
yarn install --check-files &&
npm run build &&

cd - &&
uv run manage.py collectstatic --noinput

echo "build finished"
