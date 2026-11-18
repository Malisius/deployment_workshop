#!/usr/bin/env bash
# ==============================================================================
# VPS Bootstrap Script for Ubuntu 22.04 / 24.04 LTS
# Provisions Python 3, MySQL Server, Nginx, Certbot, and Systemd Service
# ==============================================================================

set -euo pipefail

# Configuration Defaults
APP_DIR="/opt/deployment_workshop"
APP_USER="www-data"
DB_NAME="deployment_workshop"
DB_USER="workshop_user"
DB_PASS="$(openssl rand -base64 16 | tr -dc 'a-zA-Z0-9')"
SECRET_KEY="$(openssl rand -hex 32)"

echo "=== [1/6] Updating system packages ==="
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
    python3 \
    python3-venv \
    python3-pip \
    python3-dev \
    build-essential \
    mysql-server \
    nginx \
    certbot \
    python3-certbot-nginx \
    curl \
    git \
    ufw

echo "=== [2/6] Configuring MySQL Server ==="
sudo systemctl enable --now mysql

# Create database and grant user privileges
sudo mysql -e "CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
sudo mysql -e "CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';"
sudo mysql -e "GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

echo "MySQL Database '${DB_NAME}' and user '${DB_USER}' configured."

echo "=== [3/6] Setting up Application Directory and Virtualenv ==="
sudo mkdir -p "${APP_DIR}"
# Copy current workspace files to /opt/deployment_workshop if running from repo
if [ -f "wsgi.py" ]; then
    echo "Copying local repository files to ${APP_DIR}..."
    sudo cp -r . "${APP_DIR}/"
fi

cd "${APP_DIR}"
sudo python3 -m venv venv
sudo "${APP_DIR}/venv/bin/pip" install --upgrade pip
sudo "${APP_DIR}/venv/bin/pip" install -r requirements.txt

# Create .env configuration
sudo tee "${APP_DIR}/.env" > /dev/null <<EOF
PORT=5000
HOST=127.0.0.1
SECRET_KEY=${SECRET_KEY}
APP_ENV=production
DATABASE_URL=mysql+pymysql://${DB_USER}:${DB_PASS}@127.0.0.1:3306/${DB_NAME}
EOF

sudo chown -R "${APP_USER}:${APP_USER}" "${APP_DIR}"
sudo chmod 600 "${APP_DIR}/.env"

echo "=== [4/6] Installing Systemd Service ==="
sudo cp "${APP_DIR}/deploy/systemd/deployment-workshop.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now deployment-workshop.service

echo "=== [5/6] Configuring Nginx Reverse Proxy ==="
sudo cp "${APP_DIR}/deploy/nginx/flask_app.conf" /etc/nginx/sites-available/deployment_workshop.conf
sudo ln -sf /etc/nginx/sites-available/deployment_workshop.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo "=== [6/6] Configuring UFW Firewall ==="
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

echo "========================================================================"
echo " Deployment Complete!"
echo " Web App Service : sudo systemctl status deployment-workshop"
echo " MySQL Database  : ${DB_NAME} (User: ${DB_USER})"
echo " Database Password: ${DB_PASS}"
echo ""
echo " To obtain a free SSL certificate with Let's Encrypt, run:"
echo "   sudo certbot --nginx -d your-domain.com -d www.your-domain.com"
echo "========================================================================"
