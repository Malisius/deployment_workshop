# 🚀 Deployment Workshop: Universal Flask & MySQL Multi-Target Guide

[![Python Version](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask%203.0-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-MySQL%208.0-orange.svg)](https://www.mysql.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready demonstration web application illustrating how to build and deploy a Python/Flask application coupled with a MySQL database across **every major cloud platform, PaaS, container environment, and self-hosted infrastructure with ZERO code changes**.

---

## 📑 Table of Contents

- [1. Architecture & Design Principles](#1-architecture--design-principles)
  - [The 12-Factor App in Practice](#the-12-factor-app-in-practice)
  - [Automatic Database Initialization & Seeding](#automatic-database-initialization--seeding)
  - [Zero-Code-Change Portability](#zero-code-change-portability)
- [2. Quickstart & Local Development](#2-quickstart--local-development)
  - [Option A: SQLite Fallback (Instant 30-Second Test)](#option-a-sqlite-fallback-instant-30-second-test)
  - [Option B: Local Virtualenv with MySQL](#option-b-local-virtualenv-with-mysql)
  - [Option C: Docker Compose (Recommended Local)](#option-c-docker-compose-recommended-local)
- [3. Cloud Platform Deployment Guides](#3-cloud-platform-deployment-guides)
  - [Railway](#1-railway)
  - [Render](#2-render)
  - [Heroku](#3-heroku)
  - [Fly.io](#4-flyio)
  - [Northflank](#5-northflank)
  - [Vercel (Serverless Python)](#6-vercel-serverless-python)
  - [DigitalOcean App Platform](#7-digitalocean-app-platform)
  - [AWS (App Runner & RDS MySQL)](#8-aws-app-runner--rds-mysql)
  - [Google Cloud Run & Cloud SQL](#9-google-cloud-run--cloud-sql)
  - [Self-Hosted PaaS (Coolify & Dokku)](#10-self-hosted-paas-coolify--dokku)
  - [Kubernetes (Manifests & K3s)](#11-kubernetes-manifests--k3s)
- [4. Self-Hosted & VPS Deployments](#4-self-hosted--vps-deployments)
  - [Systemd + Gunicorn + Nginx (Bare-Metal / Ubuntu VPS)](#1-systemd--gunicorn--nginx-bare-metal--ubuntu-vps)
  - [Automated VPS Setup Script](#automated-vps-bootstrap-script)
  - [Production Docker Compose + Nginx + Certbot](#2-production-docker-compose--nginx--certbot)
  - [Production Docker Compose + Caddy (Auto-HTTPS)](#3-production-docker-compose--caddy-auto-https)
- [5. Exposing Self-Hosted Services to the Internet](#5-exposing-self-hosted-services-to-the-internet)
  - [Direct Exposure (Port Forwarding & DDNS)](#1-direct-exposure-port-forwarding--ddns)
  - [Non-Direct 1: Cloudflare Tunnel (Zero Trust / CGNAT Bypass)](#2-non-direct-1-cloudflare-tunnel-zero-trust--cgnat-bypass)
  - [Non-Direct 2: Cloudflare Proxy (Orange Cloud) + Nginx](#3-non-direct-2-cloudflare-proxy-orange-cloud--nginx)
  - [Non-Direct 3: Tailscale Funnel (Public Auto-HTTPS)](#4-non-direct-3-tailscale-funnel-public-auto-https)
  - [Non-Direct 4: Tailscale Serve (Private Mesh Network)](#5-non-direct-4-tailscale-serve-private-mesh-network)
  - [Non-Direct 5: VPS Reverse SSH Tunnel / WireGuard Gateway](#6-non-direct-5-vps-reverse-ssh-tunnel--wireguard-gateway)
- [6. SSL / TLS Certificate Comprehensive Guide](#6-ssl--tls-certificate-comprehensive-guide)
  - [Let's Encrypt with Certbot (HTTP-01 vs DNS-01)](#lets-encrypt-with-certbot-http-01-vs-dns-01)
  - [Caddy & Traefik Automatic ACME](#caddy--traefik-automatic-acme)
  - [Cloudflare SSL Modes Explained (Avoid Flexible SSL Trap)](#cloudflare-ssl-modes-explained-avoid-the-flexible-ssl-trap)
  - [Cloudflare Origin CA Certificates (15-Year Validity)](#cloudflare-origin-ca-certificates-15-year-validity)
  - [Tailscale Automatic Let's Encrypt Certificates](#tailscale-automatic-lets-encrypt-certificates)
- [7. Production Readiness & Day-2 Operations](#7-production-readiness--day-2-operations)
  - [WSGI Production Tuning (Gunicorn Workers & Threads)](#wsgi-production-tuning-gunicorn-workers--threads)
  - [MySQL Connection Resilience & Pool Pre-Ping](#mysql-connection-resilience--pool-pre-ping)
  - [Database Automated Backups & Disaster Recovery](#database-automated-backups--disaster-recovery)
  - [Healthcheck Probes & Zero-Downtime Deployments](#healthcheck-probes--zero-downtime-deployments)
  - [Security Hardening Checklist](#security-hardening-checklist)
- [8. Troubleshooting & Diagnostics Matrix](#8-troubleshooting--diagnostics-matrix)
- [9. Repository Structure](#9-repository-structure)

---

## 1. Architecture & Design Principles

```
                              +-------------------------------------------------+
                              |                PUBLIC INTERNET                  |
                              +-------------------------------------------------+
                                      |                                |
                        (Direct / DDNS / Port Fwd)           (Tunnel / Edge Proxy)
                                      |                                |
                                      v                                v
                        +---------------------------+    +---------------------------+
                        |  Nginx / Caddy / Ingress  |    |  Cloudflare Tunnel /      |
                        |  (SSL / TLS Termination)  |    |  Tailscale Funnel Relay   |
                        +---------------------------+    +---------------------------+
                                      |                                |
                                      +---------------+----------------+
                                                      |
                                                      v
                                        +---------------------------+
                                        |      Gunicorn WSGI        |
                                        |    (Workers + Threads)    |
                                        +---------------------------+
                                                      |
                                                      v
                                        +---------------------------+
                                        |     Flask Application     |
                                        |   (12-Factor / Stateless) |
                                        +---------------------------+
                                                      |
                                           (SQLAlchemy + PyMySQL)
                                        (Pool Pre-Ping & Auto-Seed)
                                                      |
                                                      v
                                        +---------------------------+
                                        |       MySQL 8.0 DB        |
                                        |  (Persistent Data Volume) |
                                        +---------------------------+
```

### The 12-Factor App in Practice

1. **Config in Environment**: Database credentials, ports, secrets, and environment flags are read strictly from environment variables (`DATABASE_URL`, `MYSQL_*`, `PORT`, `SECRET_KEY`).
2. **Stateless Processes**: The web application process stores no persistent data on its local filesystem. Any container can be killed, scaled, or replaced without data loss.
3. **Port Binding**: The app binds to the port specified in `${PORT:-5000}`, adapting automatically to PaaS environments (Heroku, Railway, Render, Fly.io, Cloud Run) that assign dynamic runtime ports.
4. **Disposability**: Fast startup and graceful shutdown handling via Gunicorn (`SIGTERM` triggers clean worker termination and connection drain).
5. **Backing Services as Attached Resources**: MySQL is treated as an attached resource. Whether it is a local container, an AWS RDS instance, or a PlanetScale cluster, changing one connection string switches the target seamlessly.

### Automatic Database Initialization & Seeding

On startup (or upon initial HTTP request), the application:
1. Executes `db.create_all()` to ensure all required database tables (`items`, `deployment_logs`) exist.
2. Checks `Item.query.count()`.
3. If the table is empty (such as on first run after deploying an empty MySQL database), it automatically inserts demonstration records representing different deployment architectures and commits them to MySQL.
4. Logs an audit event to `deployment_logs`.

### Zero-Code-Change Portability

Different platforms provide database credentials in differing formats:
- **Heroku / Railway / Render**: Provide a single consolidated `DATABASE_URL` (often prefixed with `mysql://` or `mysql2://`).
- **Standard Docker / Kubernetes / VPS**: Typically provide separate variables: `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_PORT`.
- **Pure Local Dev**: Zero variables configured.

The application's `app/config.py` intelligently normalizes:
- Schemes: Automatically adapts `mysql://` and `mysql2://` into `mysql+pymysql://` for SQLAlchemy.
- PyMySQL: Uses the pure-Python `pymysql` driver, eliminating native C-extension compilation issues across Alpine Linux, Slim Debian, or serverless runtimes.
- SQLite Fallback: If no database credentials are provided at all, it automatically initializes a local SQLite database so the application can be previewed immediately.

---

## 2. Quickstart & Local Development

### Option A: SQLite Fallback (Instant 30-Second Test)

Run the application locally without installing or configuring MySQL:

```bash
# 1. Clone repository
git clone https://github.com/example/deployment_workshop.git
cd deployment_workshop

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Run application
python wsgi.py
```
Open [http://localhost:5000](http://localhost:5000). The app will run in SQLite fallback mode and display an amber banner indicating SQLite is active.

---

### Option B: Local Virtualenv with MySQL

If you have a local MySQL server installed:

```bash
# 1. Copy sample environment
cp .env.example .env

# 2. Edit .env with your local MySQL credentials:
# DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/deployment_workshop

# 3. Create the database in MySQL:
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS deployment_workshop;"

# 4. Start the application
python wsgi.py
```

---

### Option C: Docker Compose (Recommended Local)

The cleanest way to test the full Flask + MySQL 8.0 stack identically to production:

```bash
docker compose up --build
```

- Flask Web App: [http://localhost:5000](http://localhost:5000)
- Health Check: [http://localhost:5000/healthz](http://localhost:5000/healthz)
- MySQL: Available internally on `db:3306` and forwarded to `127.0.0.1:3306`.
- Data Persistence: Backed by the named volume `mysql_data`.

To stop:
```bash
docker compose down
```

To stop and wipe database data:
```bash
docker compose down -v
```

---

## 3. Cloud Platform Deployment Guides

The repository includes pre-built manifest and configuration files for all major cloud providers. No code modifications are required.

### 1. Railway

Railway detects either the `railway.json` or `Dockerfile` and can automatically provision a managed MySQL database.

#### Deployment Steps:
1. Fork or push this repository to GitHub.
2. Log into [Railway.app](https://railway.app) and create a **New Project**.
3. Select **Deploy from GitHub repo** and choose your repository.
4. Click **+ New** in the project canvas and select **Database** -> **Add MySQL**.
5. Select the Flask web service, go to the **Variables** tab, click **New Variable**, and set:
   ```
   DATABASE_URL = ${{MySQL.MYSQL_URL}}
   SECRET_KEY   = <generate-random-secret>
   ```
6. Railway automatically injects `$PORT`. The application builds using the `Dockerfile` and connects to the MySQL instance over Railway's private network.

#### SSL & Custom Domains:
- Railway provides an automatic `*.up.railway.app` HTTPS domain with zero configuration.
- To use a custom domain: Go to **Settings** -> **Domains** -> **Custom Domain**, add `workshop.yourdomain.com`, and add the displayed `CNAME` record in your DNS provider. Railway issues and renews Let's Encrypt certificates automatically.

---

### 2. Render

Render uses the included `render.yaml` Blueprint to automatically deploy both the web application and a managed MySQL database in one step.

#### Deployment Steps:
1. Push this repository to GitHub.
2. In the [Render Dashboard](https://dashboard.render.com), click **New +** -> **Blueprint**.
3. Connect your repository. Render parses `render.yaml` and displays:
   - Web Service: `deployment-workshop` (Python environment with `gunicorn wsgi:app`)
   - Database: `workshop-mysql`
4. Click **Apply**.
5. Render builds the service, binds the dynamic `$PORT`, links the `DATABASE_URL` environment variable directly from the database, and begins health checks on `/healthz`.

#### SSL & Custom Domains:
- Render issues automatic TLS certificates via Let's Encrypt for all `*.onrender.com` domains and any custom domains added under **Settings** -> **Custom Domains**.

---

### 3. Heroku

Heroku uses the included `Procfile` (`web: gunicorn wsgi:app`) and `runtime.txt`.

#### Deployment Steps:
```bash
# 1. Log in to Heroku CLI
heroku login

# 2. Create the application
heroku apps:create my-deployment-workshop

# 3. Attach a MySQL add-on (JawsDB or ClearDB)
heroku addons:create jawsdb:kite-fin

# 4. Set production secret key
heroku config:set SECRET_KEY=$(openssl rand -hex 32) APP_ENV=production

# 5. Heroku provides JAWSDB_URL. The application automatically normalizes this!
# (Optionally alias it to DATABASE_URL if preferred)
heroku config:set DATABASE_URL=$(heroku config:get JAWSDB_URL)

# 6. Deploy via Git
git push heroku main

# 7. Open the application
heroku open
```

#### SSL & Custom Domains:
- Default `my-deployment-workshop.herokuapp.com` is secured with Heroku's SSL.
- For custom domains:
  ```bash
  heroku domains:add workshop.yourdomain.com
  heroku certs:auto:enable
  ```
  Heroku's Automated Certificate Management (ACM) provisions a free Let's Encrypt certificate once the DNS CNAME record resolves.

---

### 4. Fly.io

Fly.io runs applications as MicroVMs worldwide using the included `fly.toml` and `Dockerfile`.

#### Deployment Steps:
```bash
# 1. Install flyctl and authenticate
curl -L https://fly.io/install.sh | sh
fly auth login

# 2. Launch application (creates app without immediately deploying)
fly launch --no-deploy

# 3. Create a MySQL database (or attach external MySQL / PlanetScale / Fly MySQL)
# Example using Fly Secrets with an external or managed MySQL URL:
fly secrets set DATABASE_URL="mysql+pymysql://user:pass@host:3306/deployment_workshop" SECRET_KEY=$(openssl rand -hex 32)

# 4. Deploy to Fly.io
fly deploy

# 5. View your deployed app
fly status
fly open
```

#### SSL & Custom Domains:
- Fly.io terminates TLS at its global edge for `https://<app-name>.fly.dev`.
- Custom domains:
  ```bash
  fly certs add workshop.yourdomain.com
  ```
  Add the `CNAME` or `A`/`AAAA` records provided by `fly certs check workshop.yourdomain.com`. Certificates are issued automatically via Let's Encrypt.

---

### 5. Northflank

Northflank supports microservices and stateful database addons with built-in networking.

#### Deployment Steps:
1. In Northflank, create a **Project**.
2. Click **Create New** -> **Addon** -> **MySQL**. Select version `8.0` and click **Create Addon**.
3. Click **Create New** -> **Service** -> **Combined Service**.
4. Select your Git repository.
5. In **Build Settings**, select **Dockerfile** (or **Buildpack**).
6. Under **Environment Variables**, click **Link Addon** and select your MySQL addon. Map the connection details to `DATABASE_URL`.
7. Set port to `5000` (HTTP) with public exposure.
8. Click **Deploy**.

#### SSL & Custom Domains:
- Northflank provides automatic TLS for `.northflank.app` subdomains.
- Custom domains can be bound with automatic Let's Encrypt certificates under **Networking** -> **Custom Domains**.

---

### 6. Vercel (Serverless Python)

Vercel deploys Python applications as serverless functions using the included `vercel.json` and `api/index.py`.

> [!NOTE]
> Serverless functions are stateless and ephemeral. You **must** connect to a publicly reachable MySQL database (e.g., PlanetScale, Aiven, AWS RDS with public access, or a VPS MySQL instance) with SSL enabled.

#### Deployment Steps:
1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   vercel login
   ```
2. Set your environment variables in the Vercel dashboard:
   - `DATABASE_URL`: `mysql+pymysql://user:pass@remote-db-host:3306/dbname`
   - `SECRET_KEY`: `<secure-key>`
3. Deploy:
   ```bash
   vercel --prod
   ```

#### SSL:
- Vercel automatically manages SSL certificates for all Vercel domains and custom domains connected to its global CDN edge.

---

### 7. DigitalOcean App Platform

DigitalOcean App Platform reads the included `app.json` specification or configures via UI.

#### Deployment Steps:
1. Go to **Apps** in DigitalOcean Cloud Console and click **Create App**.
2. Choose **GitHub** and select this repository.
3. Add a **Database**: Select **Managed Database** -> **MySQL 8.0**.
4. DigitalOcean App Platform injects `${db.DATABASE_URL}` into your app environment.
5. Set `SECRET_KEY` under Environment Variables.
6. Click **Next** and **Launch App**.

#### SSL:
- Automated SSL is enabled by default for `*.ondigitalocean.app` and any custom domains added in App Settings.

---

### 8. AWS (App Runner & RDS MySQL)

AWS App Runner provides containerized execution with managed load balancing and TLS.

#### Deployment Steps:
1. **Create RDS MySQL**:
   - In AWS Console -> RDS -> Create Database -> MySQL 8.0.
   - Note the endpoint address (e.g., `mydb.c123.us-east-1.rds.amazonaws.com`).
2. **Push Docker Image to Amazon ECR**:
   ```bash
   aws ecr create-repository --repository-name deployment-workshop
   docker build -t deployment-workshop .
   docker tag deployment-workshop:latest <account-id>.dkr.ecr.<region>.amazonaws.com/deployment-workshop:latest
   aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/deployment-workshop:latest
   ```
3. **Deploy with App Runner**:
   - Go to App Runner -> Create Service.
   - Choose ECR container image.
   - Under Environment Variables, set:
     ```
     DATABASE_URL=mysql+pymysql://admin:password@mydb.c123.us-east-1.rds.amazonaws.com:3306/deployment_workshop
     SECRET_KEY=<secret>
     PORT=5000
     ```
   - Port: `5000`.
   - Health check path: `/healthz`.

#### SSL:
- AWS App Runner provides default HTTPS on `*.awsapprunner.com`. For custom domains, App Runner issues an AWS Certificate Manager (ACM) certificate after DNS validation.

---

### 9. Google Cloud Run & Cloud SQL

Cloud Run runs stateless containers that scale to zero, connecting to Google Cloud SQL.

#### Deployment Steps:
```bash
# 1. Build and push container to Google Artifact Registry
gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/deployment-workshop

# 2. Deploy to Cloud Run
gcloud run deploy deployment-workshop \
    --image gcr.io/$GOOGLE_CLOUD_PROJECT/deployment-workshop \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 5000 \
    --set-env-vars "DATABASE_URL=mysql+pymysql://user:pass@127.0.0.1:3306/deployment_workshop,SECRET_KEY=$(openssl rand -hex 32)" \
    --add-cloudsql-instances "$GOOGLE_CLOUD_PROJECT:us-central1:my-mysql-instance"
```

#### SSL:
- Google Cloud Run automatically provisions managed SSL certificates for `*.run.app` and any custom domains mapped under Cloud Run Domain Mappings.

---

### 10. Self-Hosted PaaS (Coolify & Dokku)

#### Coolify
[Coolify](https://coolify.io) is a modern open-source, self-hosted alternative to Heroku and Netlify.
1. Connect your server to Coolify.
2. Create a new **Project** -> **New Resource** -> **MySQL Database**.
3. Create a **New Resource** -> **Application** -> **Public/Private Git Repository**.
4. Coolify detects `Dockerfile` or `nixpacks.toml`.
5. Under Environment Variables, link the MySQL resource's connection string to `DATABASE_URL`.
6. Coolify's integrated Traefik proxy handles automatic Let's Encrypt HTTPS certificates for any domain you assign.

#### Dokku
[Dokku](https://dokku.com) is the smallest PaaS implementation powered by Docker.
```bash
# On your Dokku VPS:
dokku apps:create workshop

# Install MySQL plugin and create database
sudo dokku plugin:install https://github.com/dokku/dokku-mysql.git mysql
dokku mysql:create workshop-db
dokku mysql:link workshop-db workshop

# Set secret key
dokku config:set workshop SECRET_KEY=$(openssl rand -hex 32)

# Deploy from your workstation:
git remote add dokku dokku@your-vps-ip:workshop
git push dokku main

# Enable SSL with Let's Encrypt plugin
sudo dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git
dokku config:set --no-restart workshop DOKKU_LETSENCRYPT_EMAIL=admin@yourdomain.com
dokku letsencrypt:enable workshop
```

---

### 11. Kubernetes (Manifests & K3s)

Production-ready declarative manifests are provided in `deploy/kubernetes/`:

```bash
# 1. Create namespace
kubectl apply -f deploy/kubernetes/01-namespace.yaml

# 2. Create Persistent Volume Claim for MySQL
kubectl apply -f deploy/kubernetes/02-mysql-pvc.yaml

# 3. Deploy MySQL 8.0 with health checks
kubectl apply -f deploy/kubernetes/03-mysql-deployment.yaml

# 4. Deploy ConfigMap and Secrets
kubectl apply -f deploy/kubernetes/04-app-config-secret.yaml

# 5. Deploy Flask Web App (2 replicas, rolling updates, health checks)
kubectl apply -f deploy/kubernetes/05-app-deployment.yaml

# 6. Apply Ingress with cert-manager Let's Encrypt TLS annotations
kubectl apply -f deploy/kubernetes/06-ingress.yaml
```

Check pod and service status:
```bash
kubectl get pods,svc,ingress -n deployment-workshop
```

---

## 4. Self-Hosted & VPS Deployments

### 1. Systemd + Gunicorn + Nginx (Bare-Metal / Ubuntu VPS)

This is the standard bare-metal production setup on Linux (Ubuntu 22.04 / 24.04 LTS).

```
   [ Client Browser ]
           | (HTTPS: Port 443)
           v
   [ Nginx Web Server ] (Terminates SSL, serves static, handles buffering)
           | (HTTP: http://127.0.0.1:5000)
           v
   [ Gunicorn WSGI ]    (Multi-worker Python WSGI server managed by Systemd)
           |
           v
   [ Flask Application ]
           | (TCP: 127.0.0.1:3306)
           v
   [ MySQL 8.0 Server ] (Systemd service)
```

#### Step-by-Step Manual Setup:

#### Step 1: Install System Dependencies
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip mysql-server nginx certbot python3-certbot-nginx
```

#### Step 2: Configure MySQL
```bash
sudo systemctl enable --now mysql

# Open MySQL prompt
sudo mysql
```
```sql
CREATE DATABASE deployment_workshop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'workshop_user'@'localhost' IDENTIFIED BY 'YourStrongPassword123!';
GRANT ALL PRIVILEGES ON deployment_workshop.* TO 'workshop_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### Step 3: Deploy Application Code
```bash
sudo mkdir -p /opt/deployment_workshop
sudo chown -R $USER:www-data /opt/deployment_workshop
git clone https://github.com/example/deployment_workshop.git /opt/deployment_workshop
cd /opt/deployment_workshop

# Create virtual environment
python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt
```

#### Step 4: Configure Environment File
Create `/opt/deployment_workshop/.env`:
```bash
sudo tee /opt/deployment_workshop/.env <<EOF
PORT=5000
HOST=127.0.0.1
SECRET_KEY=$(openssl rand -hex 32)
APP_ENV=production
DATABASE_URL=mysql+pymysql://workshop_user:YourStrongPassword123!@127.0.0.1:3306/deployment_workshop
EOF

sudo chmod 600 /opt/deployment_workshop/.env
sudo chown -R www-data:www-data /opt/deployment_workshop
```

#### Step 5: Install & Start Systemd Service
The repository includes a pre-configured unit file:
```bash
sudo cp deploy/systemd/deployment-workshop.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now deployment-workshop

# Check service status
sudo systemctl status deployment-workshop
```

#### Step 6: Configure Nginx Reverse Proxy
```bash
sudo cp deploy/nginx/flask_app.conf /etc/nginx/sites-available/deployment_workshop.conf

# Edit server_name with your actual domain
sudo nano /etc/nginx/sites-available/deployment_workshop.conf

# Enable site and remove default
sudo ln -sf /etc/nginx/sites-available/deployment_workshop.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and reload Nginx
sudo nginx -t
sudo systemctl reload nginx
```

#### Step 7: Obtain Let's Encrypt SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```
Certbot automatically edits your Nginx configuration, installs the SSL certificates, sets up a 301 HTTP-to-HTTPS redirect, and configures a systemd timer for automatic renewal.

---

### Automated VPS Bootstrap Script

To automate the entire manual process above in a single command on a clean Ubuntu VPS:

```bash
git clone https://github.com/example/deployment_workshop.git
cd deployment_workshop
chmod +x deploy/scripts/setup_vps.sh
sudo ./deploy/scripts/setup_vps.sh
```

---

### 2. Production Docker Compose + Nginx + Certbot

For containerized self-hosting with automated Let's Encrypt certificates:

1. Edit `deploy/nginx/docker_nginx.conf` and set your domain name.
2. Launch the stack:
   ```bash
   docker compose -f docker-compose.prod.yml up -d
   ```
3. Issue the initial certificate using certbot:
   ```bash
   docker compose -f docker-compose.prod.yml run --rm certbot certonly \
       --webroot --webroot-path=/var/www/certbot \
       -d your-domain.com -d www.your-domain.com \
       --email admin@your-domain.com --agree-tos --no-eff-email
   ```
4. Update `deploy/nginx/docker_nginx.conf` to enable the SSL server block pointing to `/etc/letsencrypt/live/your-domain.com/fullchain.pem` and reload Nginx:
   ```bash
   docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
   ```
The certbot container runs a background loop checking for renewal every 12 hours.

---

### 3. Production Docker Compose + Caddy (Auto-HTTPS)

If you prefer **zero certbot configuration**, Caddy handles certificate generation, verification, and renewals automatically:

1. Launch with your domain:
   ```bash
   DOMAIN=workshop.yourdomain.com docker compose -f docker-compose.caddy.yml up -d
   ```
2. Point your domain's DNS `A` record to your server's public IP.
3. Caddy automatically contacts Let's Encrypt / ZeroSSL, solves the ACME challenge, provisions TLS certificates, and begins proxying to Flask. Done!

---

## 5. Exposing Self-Hosted Services to the Internet

When self-hosting at home, in an office, or on a private server, you need to expose your application to the public internet. There are two primary routing philosophies:

| Routing Method | Needs Public IP? | Needs Port Forwarding? | Works Behind CGNAT? | DDoS Protected? |
| :--- | :---: | :---: | :---: | :---: |
| **Direct Port Forwarding** | Yes | Yes (80, 443) | No | No |
| **Cloudflare Tunnel** | **No** | **No** | **Yes** | **Yes** |
| **Cloudflare Proxy + DDNS**| Yes | Yes (80, 443) | No | **Yes** |
| **Tailscale Funnel** | **No** | **No** | **Yes** | Yes (via Tailscale) |
| **Tailscale Serve** | **No** | **No** | **Yes** | Private to Tailnet |
| **Reverse SSH to VPS** | VPS needs IP | No router ports | **Yes** | Depends on VPS |

---

### 1. Direct Exposure (Port Forwarding & DDNS)

Direct exposure maps public requests straight through your router to your server.

#### Prerequisites:
1. A **Public IPv4 address** from your ISP (ensure your WAN IP in your router matches what `curl ifconfig.me` reports; if it begins with `100.64.x.x` - `100.127.x.x`, you are behind Carrier-Grade NAT and must use Cloudflare Tunnel or Tailscale Funnel instead).
2. Access to your router's admin interface (`192.168.1.1` or `192.168.0.1`).

#### Step 1: Assign a Static Local IP to your Server
In your router's DHCP reservation table, assign a static local IP to your server (e.g., `192.168.1.100`).

#### Step 2: Configure Port Forwarding
In your router settings under **Port Forwarding / Virtual Server**:
- External Port `80`  -> Internal IP `192.168.1.100`, Port `80` (TCP)
- External Port `443` -> Internal IP `192.168.1.100`, Port `443` (TCP)

#### Step 3: Configure Host Firewall (UFW)
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow OpenSSH
sudo ufw enable
```

#### Step 4: Setup Dynamic DNS (DDNS)
If your ISP assigns a dynamic IP that changes periodically:
- Use a DDNS service such as [DuckDNS](https://www.duckdns.org), [No-IP](https://www.noip.com), or Cloudflare DDNS.
- Example Cloudflare DDNS updater cron:
  ```bash
  # Automatically updates DNS A record when home IP changes
  curl -X PUT "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/dns_records/<RECORD_ID>" \
       -H "Authorization: Bearer <API_TOKEN>" \
       -H "Content-Type: application/json" \
       --data "{\"type\":\"A\",\"name\":\"workshop.yourdomain.com\",\"content\":\"$(curl -s https://api.ipify.org)\",\"ttl\":1,\"proxied\":false}"
  ```

---

### 2. Non-Direct 1: Cloudflare Tunnel (Zero Trust / CGNAT Bypass)

**The most secure and robust way to expose self-hosted servers.**
- **No router port forwarding required** (no open inbound ports).
- **Works behind CGNAT**, 4G/5G mobile hotspots, and hotel/campus networks.
- Outbound-only encrypted connection to Cloudflare's nearest edge data center.
- Free automatic SSL certificate managed by Cloudflare.
- Can be gated with Cloudflare Access (Single Sign-On with Google, GitHub, or Email OTP).

```
   [ Public Visitor ]
           |
           v
   [ Cloudflare Edge ] (DDoS Protection, WAF, SSL Termination)
           |
           | (Outbound Encrypted QUIC/HTTP2 Tunnel)
           v
   [ cloudflared Daemon ] (Running locally on your server)
           |
           v
   [ Flask App / Gunicorn ] (http://localhost:5000)
```

#### Setup Steps:

1. **Install cloudflared**:
   ```bash
   # Debian / Ubuntu
   curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
   echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/cloudflared.list
   sudo apt-get update && sudo apt-get install -y cloudflared
   ```

2. **Authenticate with Cloudflare**:
   ```bash
   cloudflared tunnel login
   ```
   Follow the URL in your browser to authorize your Cloudflare domain.

3. **Create the Tunnel**:
   ```bash
   cloudflared tunnel create workshop-tunnel
   # Note the Tunnel UUID returned (e.g. 12345678-abcd-1234-abcd-1234567890ab)
   ```

4. **Configure Routing**:
   ```bash
   cloudflared tunnel route dns workshop-tunnel workshop.yourdomain.com
   ```

5. **Deploy the Configuration**:
   Copy the sample configuration from `deploy/cloudflared/config.yml` to `~/.cloudflared/config.yml`:
   ```yaml
   tunnel: YOUR_TUNNEL_UUID_HERE
   credentials-file: /root/.cloudflared/YOUR_TUNNEL_UUID_HERE.json

   ingress:
     - hostname: workshop.yourdomain.com
       service: http://localhost:5000
     - service: http_status:404
   ```

6. **Install and Run as Systemd Service**:
   ```bash
   sudo cloudflared service install
   sudo systemctl enable --now cloudflared
   ```
Your app is now instantly accessible at `https://workshop.yourdomain.com` without a single inbound port opened on your firewall!

---

### 3. Non-Direct 2: Cloudflare Proxy (Orange Cloud) + Nginx

If you have a public IP and open ports 80/443, you can place Cloudflare's reverse proxy in front of your server:
1. In Cloudflare DNS, set your domain's `A` record to your public IP and toggle the cloud icon to **Proxied** (Orange Cloud).
2. In Cloudflare Dashboard -> **SSL/TLS**, set encryption mode to **Full (Strict)**.
3. In Cloudflare Dashboard -> **SSL/TLS** -> **Origin Server**, click **Create Certificate**.
   - Copy the Origin Certificate to `/etc/ssl/certs/cloudflare_origin.pem`.
   - Copy the Private Key to `/etc/ssl/private/cloudflare_origin.key`.
4. Install the pre-configured Nginx config:
   ```bash
   sudo cp deploy/nginx/cloudflare_reverse_proxy.conf /etc/nginx/sites-available/
   ```
5. This configuration automatically:
   - Restores real visitor IP addresses from `CF-Connecting-IP`.
   - Uses the 15-year Cloudflare Origin CA certificate.
   - Blocks non-Cloudflare traffic when Authenticated Origin Pulls (AOP) is enabled.

---

### 4. Non-Direct 3: Tailscale Funnel (Public Auto-HTTPS)

Tailscale Funnel exposes your local application node to the **entire public internet** through Tailscale's global relay network, complete with a valid Let's Encrypt certificate:

```bash
# 1. Install Tailscale and connect
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# 2. Expose port 5000 publicly over HTTPS
sudo tailscale funnel --bg 5000
```

- Your app is now live at: `https://<node-name>.<tailnet-name>.ts.net`
- SSL certificates are generated and renewed automatically by Tailscale using MagicDNS.
- No open router ports or DDNS required.

---

### 5. Non-Direct 4: Tailscale Serve (Private Mesh Network)

If your application is an internal tool or dashboard and should **never be exposed to the public**:

```bash
# Expose port 5000 privately within your Tailnet only
sudo tailscale serve --bg 5000
```
Only devices authenticated with your Tailscale account can access `https://<node-name>.<tailnet-name>.ts.net`. Public visitors receive connection refused.

---

### 6. Non-Direct 5: VPS Reverse SSH Tunnel / WireGuard Gateway

If you have a cheap cloud VPS (e.g. \$3.50/mo on Hetzner, DigitalOcean, or Linode) with a public IP, you can use it as a reverse proxy gateway into your home server.

#### Method: Persistent Reverse SSH Tunnel (autossh)
1. On your home server, install `autossh`:
   ```bash
   sudo apt-get install -y autossh
   ```
2. Run a background reverse tunnel forwarding port 5000 on the VPS to local port 5000:
   ```bash
   autossh -M 0 -f -N -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" \
       -R 127.0.0.1:5000:127.0.0.1:5000 user@vps-ip -i ~/.ssh/id_rsa
   ```
3. On the VPS, configure Nginx to proxy incoming traffic to `http://127.0.0.1:5000` and issue a Certbot certificate. Public visitors connect to the VPS, which secretly forwards requests through the encrypted SSH tunnel to your home server!

---

## 6. SSL / TLS Certificate Comprehensive Guide

### Let's Encrypt with Certbot (HTTP-01 vs DNS-01)

#### HTTP-01 Challenge (Standard)
Certbot places a random verification token in `/var/www/certbot/.well-known/acme-challenge/<TOKEN>`. The Let's Encrypt ACME server fetches `http://your-domain.com/.well-known/acme-challenge/<TOKEN>`. If it matches, the certificate is issued.
- **Requirement**: Port 80 must be open and accessible from the public internet.
- **Command**:
  ```bash
  sudo certbot --nginx -d yourdomain.com
  ```

#### DNS-01 Challenge (For Wildcard Certs or Closed Ports)
Let's Encrypt validates ownership by querying a `_acme-challenge.yourdomain.com` `TXT` record on your DNS provider.
- **Requirement**: API access to your DNS provider (Cloudflare, Route53, DigitalOcean, etc.).
- **Benefit**: Works **without opening any inbound firewall ports**, and supports wildcard certificates (`*.yourdomain.com`).
- **Command with Cloudflare DNS**:
  ```bash
  sudo apt-get install python3-certbot-dns-cloudflare
  # In /etc/letsencrypt/cloudflare.ini:
  # dns_cloudflare_api_token = <your-token>
  sudo certbot certonly --dns-cloudflare \
      --dns-cloudflare-credentials /etc/letsencrypt/cloudflare.ini \
      -d yourdomain.com -d *.yourdomain.com
  ```

---

### Caddy & Traefik Automatic ACME

Modern web servers like Caddy and Traefik eliminate the need for Certbot entirely.
- They act as their own ACME client.
- When an incoming request arrives for a new domain name, they automatically contact Let's Encrypt or ZeroSSL, complete the HTTP-01 or TLS-ALPN-01 challenge, obtain the certificate in memory, and begin serving HTTPS.
- Automatic renewal occurs 30 days before expiration.

---

### Cloudflare SSL Modes Explained (Avoid the Flexible SSL Trap)

In Cloudflare Dashboard -> **SSL/TLS**:

| Mode | Visitor to Cloudflare | Cloudflare to Origin Server | Security Assessment |
| :--- | :---: | :---: | :--- |
| **Off** | HTTP | HTTP | ❌ Insecure |
| **Flexible** | HTTPS | **HTTP (Unencrypted)** | ⚠️ **DANGEROUS**: Traffic over the public internet between CF and your server is in plaintext. Also triggers infinite 301 redirect loops if your app forces HTTPS! |
| **Full** | HTTPS | HTTPS (Self-signed allowed) | 🟡 Encrypted, but vulnerable to origin spoofing. |
| **Full (Strict)** | HTTPS | HTTPS (Valid CA or Origin CA) | ✅ **RECOMMENDED**: Fully encrypted, verified identity. |

---

### Cloudflare Origin CA Certificates (15-Year Validity)

When using Cloudflare Proxy in **Full (Strict)** mode:
1. You do not need Certbot on your origin server.
2. Generate an **Origin Certificate** in Cloudflare Dashboard -> SSL/TLS -> Origin Server.
3. Select 15-year validity.
4. Save the certificate and private key in `/etc/ssl/certs/cloudflare_origin.pem` and `/etc/ssl/private/cloudflare_origin.key`.
5. Point Nginx to these files. You will never have to renew certificates every 90 days again!

---

### Tailscale Automatic Let's Encrypt Certificates

Tailscale nodes with MagicDNS can provision Let's Encrypt certificates using the CLI directly:
```bash
sudo tailscale cert <node-name>.<tailnet-name>.ts.net
```
This generates `<node-name>.crt` and `<node-name>.key` signed by Let's Encrypt without exposing port 80!

---

## 7. Production Readiness & Day-2 Operations

### WSGI Production Tuning (Gunicorn Workers & Threads)

Never run `flask run` in production. Development servers are single-threaded and vulnerable to denial-of-service attacks.

#### Gunicorn Worker Formula:
```
Workers = (2 x Number of CPU Cores) + 1
```
For I/O-bound web applications querying databases:
```bash
gunicorn --workers 3 --threads 2 --timeout 60 --bind 0.0.0.0:5000 wsgi:app
```
- `--workers 3`: Multi-process execution isolates memory leaks and utilizes multi-core CPUs.
- `--threads 2`: Enables concurrent request handling within each worker during database latency.
- `--timeout 60`: Prevents hung database queries from freezing worker processes indefinitely.

---

### MySQL Connection Resilience & Pool Pre-Ping

In cloud environments (Heroku, AWS, Kubernetes, Docker networks), stateful firewalls aggressively terminate idle TCP connections after 5 to 10 minutes.

This application protects against `MySQL server has gone away` errors via `app/config.py`:
```python
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,       # Tests connection with 'SELECT 1' before executing queries
    "pool_recycle": 280,         # Recycles connections every 280s before cloud timeouts hit
}
```

---

### Database Automated Backups & Disaster Recovery

Create `/usr/local/bin/backup_workshop_db.sh`:
```bash
#!/usr/bin/env bash
set -eo pipefail

BACKUP_DIR="/var/backups/mysql"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="deployment_workshop"

mkdir -p "${BACKUP_DIR}"

# Dump and compress
mysqldump --single-transaction --quick --lock-tables=false \
    -u workshop_user -p'workshop_secret_pass' "${DB_NAME}" | gzip > "${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"

# Retain only last 7 days of backups
find "${BACKUP_DIR}" -type f -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"
```

Add to crontab to run daily at 2:00 AM:
```bash
0 2 * * * /usr/local/bin/backup_workshop_db.sh >/dev/null 2>&1
```

#### Restoring from Backup:
```bash
gunzip < /var/backups/mysql/deployment_workshop_20261117_020000.sql.gz | mysql -u workshop_user -p deployment_workshop
```

---

### Healthcheck Probes & Zero-Downtime Deployments

The application provides a dedicated health check endpoint at `/healthz`:
```json
GET /healthz
{
  "database": {
    "connected": true,
    "dialect": "mysql",
    "latency_ms": 1.45,
    "version": "8.0.36"
  },
  "diagnostics": {
    "hostname": "workshop-web-6d9b5c77b-k2x9q",
    "platform": "Railway",
    "port": 5000,
    "python_version": "3.11.10"
  },
  "status": "healthy"
}
```

- When the database is healthy: returns **HTTP 200**.
- When the database fails: returns **HTTP 503**.
- For orchestrators that need graceful container startup before the database is ready, pass `?graceful=true` to return HTTP 200 with degraded state metadata.

---

### Security Hardening Checklist

- [x] **Non-Root Docker Execution**: Container runs under dedicated `appuser` (UID 10001).
- [x] **Least Privilege Database Grants**: Database user granted privileges only on `deployment_workshop.*`, never global `*.*`.
- [x] **Parameterized Queries**: All database queries are executed via SQLAlchemy ORM (100% defense against SQL injection).
- [x] **No Hardcoded Secrets**: Secrets and keys loaded strictly via environment variables.
- [x] **Security Headers**: HSTS, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff` enabled in Nginx and Caddy.
- [x] **Systemd Sandboxing**: `PrivateTmp=true`, `ProtectSystem=full`, `NoNewPrivileges=true`.

---

## 8. Troubleshooting & Diagnostics Matrix

| Symptom / Error | Root Cause | Solution |
| :--- | :--- | :--- |
| **502 Bad Gateway** in Nginx | Gunicorn process is stopped, crashed, or listening on wrong port. | Run `sudo systemctl status deployment-workshop`. Check Gunicorn logs with `journalctl -u deployment-workshop -e`. Ensure `proxy_pass` in Nginx matches Gunicorn's bind address. |
| **Can't connect to MySQL server on '127.0.0.1'** | MySQL service is not running or listening only on a socket. | Run `sudo systemctl status mysql`. In Docker Compose, verify `depends_on: { db: { condition: service_healthy } }`. |
| **Access denied for user 'workshop_user'@'localhost'** | Password mismatch or user lacks host permission. | Test with `mysql -u workshop_user -p`. In MySQL 8, ensure user host is `'workshop_user'@'%'` if connecting across Docker containers. |
| **MySQL server has gone away** | Cloud firewall dropped idle connection after inactivity. | Ensure `pool_pre_ping=True` and `pool_recycle=280` are active in `app/config.py`. |
| **ERR_TOO_MANY_REDIRECTS** in browser | Cloudflare SSL mode set to **Flexible** while Nginx/Flask forces HTTPS. | In Cloudflare dashboard, change SSL mode from **Flexible** to **Full** or **Full (Strict)**. |
| **Address already in use: 5000** | Another process is already bound to port 5000 (often Apple AirPlay on macOS or an old Gunicorn process). | Run `sudo lsof -i :5000` or `sudo ss -tulpn \| grep 5000` to find the PID, then `kill -9 <PID>`. |
| **Database changes lost after Docker restart** | MySQL container was started without a persistent volume. | Verify `docker-compose.yml` mounts `mysql_data:/var/lib/mysql`. Never delete the volume unless intentionally wiping state. |

---

## 9. Repository Structure

```
deployment_workshop/
├── app/
│   ├── __init__.py                 # Application factory, error handlers, route registration
│   ├── config.py                   # Environment variable normalization, platform detection
│   ├── database.py                 # Health check ping, auto-seeding logic, table creation
│   ├── models.py                   # SQLAlchemy models (Item, DeploymentLog)
│   ├── routes.py                   # Web dashboard, /healthz, /api/items, /api/info
│   ├── static/
│   │   ├── css/style.css           # Custom styles
│   │   └── favicon.svg             # SVG Favicon
│   └── templates/
│       ├── base.html               # Tailwind CSS base layout, navigation, flash banners
│       ├── index.html              # Main dashboard: status cards, DB list, add form
│       └── 404.html                # 404 Error page
│
├── wsgi.py                         # Production WSGI entry point for Gunicorn / uWSGI
├── requirements.txt                # Production Python dependencies
├── runtime.txt                     # Python runtime version for Heroku & Render buildpacks
├── .env.example                    # Comprehensive environment configuration template
├── .gitignore                      # Git exclusion rules
├── .dockerignore                   # Docker build context exclusions
│
├── Dockerfile                      # Hardened non-root production container
├── docker-compose.yml              # Local / VPS development stack (App + MySQL 8.0)
├── docker-compose.prod.yml         # Production stack (App + MySQL + Nginx + Certbot)
├── docker-compose.caddy.yml        # Production stack with automatic Caddy HTTPS
│
├── Procfile                        # Heroku, Render, Dokku, Scalingo process definition
├── fly.toml                        # Fly.io MicroVM configuration
├── railway.json                    # Railway deployment manifest
├── render.yaml                     # Render Blueprint specification (Web + Database)
├── app.json                        # Heroku / DigitalOcean App Platform specification
├── vercel.json                     # Vercel serverless function routing
├── api/
│   └── index.py                    # Vercel serverless Python entry point
├── nixpacks.toml                   # Nixpacks build definition
│
├── deploy/
│   ├── systemd/
│   │   └── deployment-workshop.service  # Hardened Linux systemd service unit
│   ├── nginx/
│   │   ├── flask_app.conf               # Standard Nginx reverse proxy
│   │   ├── flask_app_ssl_certbot.conf   # Production Nginx with Let's Encrypt SSL
│   │   ├── docker_nginx.conf            # Nginx config for Docker Compose stack
│   │   └── cloudflare_reverse_proxy.conf# Nginx with Cloudflare Real IP & AOP
│   ├── caddy/
│   │   └── Caddyfile                    # Automatic HTTPS Caddy reverse proxy
│   ├── cloudflared/
│   │   └── config.yml                   # Cloudflare Zero Trust Tunnel configuration
│   ├── tailscale/
│   │   └── tailscale-serve.md           # Tailscale Serve & Funnel guide
│   ├── kubernetes/
│   │   ├── 01-namespace.yaml
│   │   ├── 02-mysql-pvc.yaml
│   │   ├── 03-mysql-deployment.yaml
│   │   ├── 04-app-config-secret.yaml
│   │   ├── 05-app-deployment.yaml
│   │   └── 06-ingress.yaml
│   └── scripts/
│       ├── setup_vps.sh                 # One-click Ubuntu VPS provisioning script
│       └── wait_for_db.py               # Pre-flight database readiness polling script
│
├── tests/
│   └── test_app.py                      # Integration and unit tests
└── README.md                            # Comprehensive Deployment & Operations Guide
```

---

## 📄 License

This project is licensed under the MIT License - feel free to use it as a foundation for your own production deployments!
