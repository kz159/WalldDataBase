FROM postgres:12.2-alpine

RUN apk update && apk add --no-cache postgresql-dev gcc python3 python3-dev musl-dev

COPY requirements.txt .

RUN pip3 install -r requirements.txt

WORKDIR /app

COPY . .

RUN alembic upgrade head

HEALTHCHECK --interval=30s --timeout=3s --retries=10 \
     CMD ["psql", "-U", "postgres", "-c", "select version()"]
