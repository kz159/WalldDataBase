FROM postgres:12-alpine

RUN apk add gcc python3-dev musl-dev py3-pip

COPY . .

RUN pip3 install -r requirements.txt

RUN rm -rf alembic/versions/*

ARG DB_USER=postgres
ARG DB_PASSWORD=1234
ARG DB_NAME=postgres
ARG POSTGRES_PASSWORD=1234
RUN ln -s usr/local/bin/docker-entrypoint.sh /
USER postgres

RUN docker-entrypoint.sh & postgres & sleep 5 && alembic revision --autogenerate -m "fistssas" && alembic upgrade head
