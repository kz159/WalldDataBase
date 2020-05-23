#!/bin/sh
set -ex

if [ -n "$DB_HOST" ]; then
  echo ok
else
  DB_HOST=localhost
fi
PGPASSWORD=$DB_PASSWORD

docker stop test_db || true
docker run -d --rm -p 5432:5432 -e POSTGRES_PASSWORD=$DB_PASSWORD --name test_db postgres

if [ $? -eq 0 ]
then
  sleep 3
  echo "Db ready, making migrations"
  alembic upgrade head
  echo "thats all, use psql with $DB_PASSWORD pass"
else
  echo "Something is wrong with db" >&2
fi