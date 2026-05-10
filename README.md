# Travel Map

A personal travel tracking app. Log your relationship to each location — whether you've lived there, stayed overnight, walked around, or just passed through — and see it all on an interactive color-coded map.

Available in English and Japanese.

## Setup

**Requirements:** Python 3.14+

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open http://localhost:8000 and log in.

## Usage

- The homepage shows a map with your logged locations color-coded by status.
- Click any location to update your status for it: **Lived**, **Stayed**, **Walked**, or **Passed Through**.
- Use the language switcher in the top right to toggle between English and Japanese.
- Add or manage locations and regions via the Django admin at `/admin/`.

## Status types

| Status | Meaning |
|---|---|
| Lived | You've lived there |
| Stayed | You've stayed at least one night |
| Walked | You've walked around |
| Passed Through | You've been through but didn't stop |

## Deployment

### Prerequisites

Install Docker and Docker Compose on your server. On Ubuntu/Debian:

```bash
curl -fsSL https://get.docker.com | sh
sudo apt install -y docker-compose
```

### Dedicated user

Run the app as a dedicated user rather than root:

```bash
sudo useradd -m -s /bin/bash tabicat
sudo usermod -aG docker tabicat
sudo -u tabicat -i
```

Then run all the steps below as this user. The app files and `.env` will live in `/home/tabicat/` and won't be readable 
by other non-root users.

### First deploy

```bash
# on your server
git clone https://github.com/kayleema/travel-map.git
cd travel-map

cp .env.example .env
```

Edit `.env` with real values:

```
SECRET_KEY=<long random string>
DATABASE_USER=travelmap
DATABASE_PASS=<strong password>
```

Generate values for `SECRET_KEY` and `DATABASE_PASS` with:
```bash
# SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# DATABASE_PASS (shorter is fine since it never leaves the server)
python3 -c "import secrets; print(secrets.token_urlsafe(16))"
```

Avoid passwords with special shell characters (`$`, `!`, `"`) as they can cause issues in `.env` files.

**On your local machine,** build and push the image to Docker Hub:

```bash
docker login
docker-compose build
docker-compose push
```

**On the server,** pull and start:

```bash
docker-compose pull
docker-compose up -d
```

Create your admin account (one time only):

```bash
docker-compose exec web python manage.py createsuperuser
```

The app is now running on port 8000. Point your reverse proxy (nginx, Caddy, etc.) there.

### Updates

On your local machine, rebuild and push:

```bash
docker-compose build
docker-compose push
```

On the server:

```bash
docker-compose pull
docker-compose up -d
```

Migrations run automatically on startup.

### Reverse proxy

If you're using Caddy, a minimal `Caddyfile`:

```
tabicat.kaylee.jp {
    reverse_proxy localhost:8000
}
```

For nginx, create a config file at `/etc/nginx/sites-available/tabicat`:

```nginx
server {
    listen 80;
    server_name tabicat.kaylee.jp;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Then enable it and reload:

```bash
sudo ln -s /etc/nginx/sites-available/tabicat /etc/nginx/sites-enabled/tabicat
sudo nginx -t          # check for syntax errors
sudo systemctl reload nginx
```
