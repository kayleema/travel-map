FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN DJANGO_SETTINGS_MODULE=travelmap.settings_prod \
    SECRET_KEY=build-placeholder \
    DATABASE_USER=x DATABASE_PASS=x DATABASE_HOST=x \
    python manage.py collectstatic --noinput

EXPOSE 8000

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
