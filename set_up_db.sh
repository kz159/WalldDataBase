#!/bin/sh
set -ex

if [ -n "$DB_HOST" ]; then
  echo ok
else
  export DB_HOST=localhost
fi
export DB_PASSWORD=1234
PGPASSWORD=$DB_PASSWORD
export DB_USER=postgres
export DB_NAME=postgres

docker stop test_db || true
docker stop rmq || true
docker run -d --rm -p 5432:5432 -e POSTGRES_PASSWORD=$DB_PASSWORD --name test_db postgres
docker run -d --rm -p 5672:5672 -p 15672:15672 --name rmq  rabbitmq:management-alpine

if [ $? -eq 0 ]
then
  sleep 3
  echo "Db and RMQ ready, making migrations"
  rm -rf alembic/versions/*
  alembic revision --autogenerate -m "fistssas"
  alembic upgrade head
  echo "thats all, use psql -h localhost $DB_PASSWORD"
else
  echo "Something is wrong with db" >&2
fi
