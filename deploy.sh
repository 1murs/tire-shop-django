#!/bin/bash
# Скрипт розгортання Django на Raspberry Pi
# Запускати на Raspberry Pi: bash deploy.sh

set -e

echo "=== Розгортання КМ/Ч 120 на Raspberry Pi ==="

# 1. Оновити систему та встановити залежності
echo ""
echo ">>> Встановлення системних залежностей..."
sudo apt update
sudo apt install -y nginx

# 2. Створити віртуальне середовище
echo ""
echo ">>> Налаштування Python..."
cd ~/tire-shop-django
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# 3. Зібрати статичні файли
echo ""
echo ">>> Збір статичних файлів..."
python manage.py collectstatic --noinput

# 4. Міграції
echo ""
echo ">>> Міграція бази даних..."
python manage.py migrate

# 5. Створити .env якщо не існує
if [ ! -f .env ]; then
    echo ""
    echo ">>> Створення .env файлу..."
    SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    cat > .env << EOF
SECRET_KEY=$SECRET
DEBUG=False
ALLOWED_HOSTS=*
EOF
    echo "   .env створено"
fi

# 6. Налаштувати Gunicorn сервіс
echo ""
echo ">>> Налаштування Gunicorn сервісу..."
USER=$(whoami)
DIR=$(pwd)

sudo tee /etc/systemd/system/tireshop.service > /dev/null << EOF
[Unit]
Description=KM/H 120 Tire Shop
After=network.target

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

# Активувати сайт
sudo ln -sf /etc/nginx/sites-available/tireshop /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Перевірити конфіг Nginx
sudo nginx -t

# 8. Запустити все
echo ""
echo ">>> Запуск сервісів..."
sudo systemctl daemon-reload
sudo systemctl enable tireshop
sudo systemctl restart tireshop
sudo systemctl restart nginx

echo ""
echo "========================================="
echo "  Готово! Сайт працює!"
echo "========================================="
echo ""
echo "  Локально:  http://192.168.0.114"
echo "  Зовні:     http://81.197.252.206"
echo ""
echo "  Корисні команди:"
echo "  sudo systemctl status tireshop   - статус сайту"
echo "  sudo systemctl restart tireshop  - перезапустити сайт"
echo "  sudo systemctl stop tireshop     - зупинити сайт"
echo "  journalctl -u tireshop -f        - логи в реальному часі"
echo "========================================="
