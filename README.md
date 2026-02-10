# KM/H 120 - Tire & Wheel Shop

Django-based e-commerce platform for a tire and wheel shop. Features product catalog with search and filtering, supplier management with automated markup pricing, Excel price import, and XML feeds for price aggregators.

## Features

- **Product Catalog** — Tires and wheels with detailed specifications, filtering by size/brand/season/type
- **Supplier Management** — Multiple suppliers with configurable markup percentages and preorder detection
- **Excel Price Import** — Upload `.xls` price lists to bulk create/update products via admin panel
- **XML Feeds** — YML feed generation for price aggregators (E-Katalog, Hotline) with supplier filtering
- **Car Fitment Calculator** — OEM and replacement tire/wheel sizes by car make/model/year
- **Error Logging** — Built-in error log viewer in admin panel
- **Deployment Ready** — Includes deploy script for Gunicorn + Nginx on Linux (tested on Raspberry Pi 5)

## Tech Stack

- Python 3.11+
- Django 5.1 / 6.0
- SQLite
- Pandas (Excel import)
- Pillow (image handling)
- Gunicorn + Nginx (production)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/tire-shop-django.git
cd tire-shop-django

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your SECRET_KEY

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## Project Structure

```
tire-shop-django/
├── catalog/               # Main app
│   ├── models.py          # Tire, Disk, Brand, Supplier, CarFitment
│   ├── views.py           # Product listing and detail views
│   ├── admin.py           # Custom admin with import/export tools
│   ├── feeds.py           # XML/YML feed generator
│   ├── import_service.py  # Excel price import logic
│   └── urls.py            # URL routing
├── config/                # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── templates/             # HTML templates
│   ├── base.html
│   ├── admin/             # Custom admin templates
│   └── catalog/           # Product templates
├── static/                # Static files (CSS, JS, images)
├── deploy.sh              # Production deployment script
├── manage.py
└── requirements.txt
```

## Admin Panel

Access at `/admin/` with the following custom tools:

- **Import Prices** — Upload Excel files to import/update tire and disk prices
- **XML Feeds** — Generate XML feeds with supplier selection for price aggregators
- **Error Logs** — View and manage application error logs
- **Supplier Management** — Configure supplier markup percentages and delivery terms

## Deployment

For production deployment on a Linux server (e.g., Raspberry Pi):

```bash
chmod +x deploy.sh
./deploy.sh
```

This will set up Gunicorn as a systemd service and configure Nginx as a reverse proxy.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | — |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `*` |
| `EMAIL_HOST` | SMTP server | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_HOST_USER` | Email address | — |
| `EMAIL_HOST_PASSWORD` | Email password | — |

## License

MIT
