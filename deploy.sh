#!/bin/bash
# Скрипт розгортання Django на VPS / Raspberry Pi
# Запускати: bash deploy.sh

set -e

echo "=== Розгортання КМ/Ч 120 ==="

# 1. Оновити систему та встановити залежності
echo ""
echo ">>> Встановлення системних залежностей..."
sudo apt update
sudo apt install -y nginx postgresql postgresql-contrib python3-venv

# 2. Створити базу PostgreSQL
echo ""
echo ">>> Налаштування PostgreSQL..."
DB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")

sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='tire_shop_user'" | grep -q 1 || {
    sudo -u postgres psql -c "CREATE USER tire_shop_user WITH PASSWORD '$DB_PASSWORD';"
    echo "   Користувач tire_shop_user створений"
}

sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='tire_shop'" | grep -q 1 || {
    sudo -u postgres psql -c "CREATE DATABASE tire_shop OWNER tire_shop_user;"
    echo "   База tire_shop створена"
}

sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE tire_shop TO tire_shop_user;"

# 3. Створити віртуальне середовище
echo ""
echo ">>> Налаштування Python..."
cd ~/tire-shop-django
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Створити .env якщо не існує
if [ ! -f .env ]; then
    echo ""
    echo ">>> Створення .env файлу..."
    SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    cat > .env << EOF
SECRET_KEY=$SECRET
DEBUG=False
ALLOWED_HOSTS=*

# Database (PostgreSQL)
DB_NAME=tire_shop
DB_USER=tire_shop_user
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432

# Email (необов'язково)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=True

# Telegram Bot (необов'язково)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
EOF
    echo "   .env створено — відредагуй його перед запуском!"
else
    echo "   .env вже існує, пропускаю"
fi

# 5. Міграції та статика
echo ""
echo ">>> Міграція бази даних..."
python manage.py migrate

echo ""
echo ">>> Збір статичних файлів..."
python manage.py collectstatic --noinput

# 6. Налаштувати Gunicorn сервіс
echo ""
echo ">>> Налаштування Gunicorn сервісу..."
USER=$(whoami)
DIR=$(pwd)

sudo tee /etc/systemd/system/tireshop.service > /dev/null << EOF
[Unit]
Description=KM/H 120 Tire Shop
After=network.target postgresql.service

[Service]
User=$USER
Group=$USER
WorkingDirectory=$DIR
Environment="PATH=$DIR/.venv/bin"
ExecStart=$DIR/.venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 120

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 7. Налаштувати Nginx
echo ""
echo ">>> Налаштування Nginx..."
sudo tee /etc/nginx/sites-available/tireshop > /dev/null << EOF
server {
    listen 80;
    server_name _;

    client_max_body_size 50M;

    location /static/ {
        alias $DIR/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias $DIR/media/;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 120s;
        proxy_read_timeout 120s;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/tireshop /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

# 8. Запустити все
echo ""
echo ">>> Запуск сервісів..."
sudo systemctl daemon-reload
sudo systemctl enable postgresql
sudo systemctl enable tireshop
sudo systemctl enable nginx
sudo systemctl restart tireshop
sudo systemctl restart nginx

echo ""
echo "========================================="
echo "  Готово! Сайт працює на порті 80"
echo "========================================="
echo ""
echo "  Корисні команди:"
echo "  sudo systemctl status tireshop   - статус сайту"
echo "  sudo systemctl restart tireshop  - перезапустити"
echo "  journalctl -u tireshop -f        - логи"
echo "========================================="
