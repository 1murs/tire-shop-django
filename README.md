# KM/H 120 - Tire & Wheel Shop

Django-based e-commerce platform for a tire and wheel shop. Features product catalog with search and filtering, supplier management with automated markup pricing, Excel price import, and XML feeds for price aggregators.

## Features

- **Product Catalog** — Tires and wheels with detailed specifications, filtering by size/brand/season/type
- **Supplier Management** — Multiple suppliers with configurable markup percentages and preorder detection
- **Excel Price Import** — Upload `.xls` price lists to bulk create/update products via admin panel
- **XML Feeds** — YML feed generation for price aggregators (E-Katalog, Hotline) with supplier filtering
- **Car Fitment Calculator** — OEM and replacement tire/wheel sizes by car make/model/year
- **Live Chat** — Customer chat widget with Telegram bot integration
- **Error Logging** — Built-in error log viewer in admin panel
- **Deployment Ready** — Includes deploy script for Gunicorn + Nginx + PostgreSQL on Linux

## Tech Stack

- Python 3.11+
- Django 5.1
- PostgreSQL
- Pandas (Excel import)
- Pillow (image handling)
- Gunicorn + Nginx (production)

## Quick Start (development)

```bash
git clone https://github.com/1murs/tire-shop-django.git
cd tire-shop-django

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env — set SECRET_KEY and DB credentials

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Deployment on VPS / Raspberry Pi

### Automatic (one command)

```bash
git clone https://github.com/1murs/tire-shop-django.git
cd tire-shop-django
chmod +x deploy.sh
./deploy.sh
```

The script installs PostgreSQL, Nginx, creates the database, configures Gunicorn as a systemd service, and starts everything.

After running, edit `.env` to add email and Telegram settings if needed.

### Manual (step by step)

#### 1. System packages

```bash
sudo apt update
sudo apt install -y nginx postgresql postgresql-contrib python3-venv
```

#### 2. PostgreSQL database

```bash
sudo -u postgres psql
```
```sql
CREATE DATABASE tire_shop;
CREATE USER tire_shop_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE tire_shop TO tire_shop_user;
ALTER DATABASE tire_shop OWNER TO tire_shop_user;
\q
```

#### 3. Project setup

```bash
git clone https://github.com/1murs/tire-shop-django.git
cd tire-shop-django

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 4. Environment configuration

```bash
cp .env.example .env
nano .env
```

Set at minimum:
- `SECRET_KEY` — generate with `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`
- `DEBUG=False`
- `DB_PASSWORD` — the password you set in step 2

#### 5. Database migration and static files

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### 6. Gunicorn systemd service

Create `/etc/systemd/system/tireshop.service`:

```ini
[Unit]
Description=KM/H 120 Tire Shop
After=network.target postgresql.service

[Service]
User=your-username
Group=your-username
WorkingDirectory=/home/your-username/tire-shop-django
Environment="PATH=/home/your-username/tire-shop-django/.venv/bin"
ExecStart=/home/your-username/tire-shop-django/.venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 120

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable tireshop
sudo systemctl start tireshop
```

#### 7. Nginx reverse proxy

Create `/etc/nginx/sites-available/tireshop`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 50M;

    location /static/ {
        alias /home/your-username/tire-shop-django/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /home/your-username/tire-shop-django/media/;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

```bash
sudo ln -sf /etc/nginx/sites-available/tireshop /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

#### 8. (Optional) Cloudflare Tunnel

If the server is behind NAT (e.g. Raspberry Pi at home):

```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
sudo dpkg -i cloudflared-linux-arm64.deb

# Run tunnel (quick way — gives *.trycloudflare.com URL)
cloudflared tunnel --url http://localhost:80
```

Add the tunnel URL to `CSRF_TRUSTED_ORIGINS` in `.env` if using a custom domain.

### Useful commands

```bash
sudo systemctl status tireshop      # service status
sudo systemctl restart tireshop     # restart app
journalctl -u tireshop -f           # live logs
sudo -u postgres psql -d tire_shop  # database shell
```

## Project Structure

```
tire-shop-django/
├── catalog/               # Main app
│   ├── models.py          # Tire, Disk, Brand, Supplier, CarFitment
│   ├── views/             # Views package (pages, catalog, cart, orders, chat)
│   ├── admin.py           # Custom admin with import/export tools
│   ├── feeds.py           # XML/YML feed generator
│   ├── import_service.py  # Excel price import logic
│   ├── telegram_bot.py    # Telegram chat integration
│   └── urls.py            # URL routing
├── config/                # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── templates/             # HTML templates
├── static/                # Static files (CSS, JS, images)
├── deploy.sh              # Production deployment script
├── manage.py
└── requirements.txt
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | — |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `*` |
| `DB_NAME` | PostgreSQL database name | `tire_shop` |
| `DB_USER` | PostgreSQL user | `tire_shop_user` |
| `DB_PASSWORD` | PostgreSQL password | — |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `EMAIL_HOST_USER` | Email address for notifications | — |
| `EMAIL_HOST_PASSWORD` | Email password (app password) | — |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token for live chat | — |
| `TELEGRAM_CHAT_ID` | Telegram chat ID for messages | — |

## Admin Panel

Access at `/admin/` with the following custom tools:

- **Import Prices** — Upload Excel files to import/update tire and disk prices
- **XML Feeds** — Generate XML feeds with supplier selection for price aggregators
- **Error Logs** — View and manage application error logs
- **Supplier Management** — Configure supplier markup percentages and delivery terms

## License

MIT
