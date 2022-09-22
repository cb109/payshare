#!/bin/sh

workon payshare &&

git stash save pre_update &&

git checkout master &&
git pull --prune &&
git stash pop &&

./build.sh &&
python manage.py migrate &&
systemctl restart payshare &&
systemctl restart nginx

echo "update finished"
