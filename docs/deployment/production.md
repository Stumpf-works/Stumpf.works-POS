# Production Deployment Guide

Comprehensive guide for deploying Stumpf.works POS to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Database Setup](#database-setup)
4. [Application Deployment](#application-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Reverse Proxy (Nginx)](#reverse-proxy-nginx)
7. [SSL/TLS Setup](#ssltls-setup)
8. [Monitoring & Logging](#monitoring--logging)
9. [Backup Strategy](#backup-strategy)
10. [Security Checklist](#security-checklist)

---

## Prerequisites

### Hardware Requirements

**Minimum:**
- 2 CPU cores
- 4 GB RAM
- 50 GB SSD storage
- Stable internet connection

**Recommended:**
- 4 CPU cores
- 8 GB RAM
- 100 GB SSD storage
- 100 Mbps internet
- Redundant power supply

### Software Requirements

- Ubuntu 22.04 LTS (or similar Linux distribution)
- Python 3.10+
- PostgreSQL 14+
- Redis 6+
- Nginx 1.18+
- Docker & Docker Compose (optional)
- Node.js 18+ (for frontend build)

---

## Server Setup

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Dependencies

```bash
# PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Redis
sudo apt install -y redis-server

# Nginx
sudo apt install -y nginx

# Python
sudo apt install -y python3.10 python3.10-venv python3-pip

# Node.js (for frontend)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Git
sudo apt install -y git

# Certbot (for SSL)
sudo apt install -y certbot python3-certbot-nginx
```

### 3. Create Application User

```bash
sudo useradd -m -s /bin/bash posapp
sudo usermod -aG sudo posapp
sudo su - posapp
```

---

## Database Setup

### 1. Configure PostgreSQL

```bash
# Switch to postgres user
sudo -u postgres psql

-- Create database and user
CREATE DATABASE pos_production;
CREATE USER posuser WITH ENCRYPTED PASSWORD 'STRONG_PASSWORD_HERE';
GRANT ALL PRIVILEGES ON DATABASE pos_production TO posuser;

-- Enable required extensions
\c pos_production
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
\q
```

### 2. Configure PostgreSQL for Production

Edit `/etc/postgresql/14/main/postgresql.conf`:

```conf
# Performance tuning
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 2621kB
min_wal_size = 1GB
max_wal_size = 4GB

# Connections
max_connections = 100

# Logging
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_duration = off
log_lock_waits = on
```

Edit `/etc/postgresql/14/main/pg_hba.conf`:

```conf
# Local connections
local   all             all                                     peer
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256
```

Restart PostgreSQL:

```bash
sudo systemctl restart postgresql
```

### 3. Configure Redis

Edit `/etc/redis/redis.conf`:

```conf
# Security
requirepass YOUR_REDIS_PASSWORD
bind 127.0.0.1 ::1

# Persistence
save 900 1
save 300 10
save 60 10000

# Memory
maxmemory 256mb
maxmemory-policy allkeys-lru

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log
```

Restart Redis:

```bash
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

---

## Application Deployment

### 1. Clone Repository

```bash
cd /home/posapp
git clone https://github.com/yourorg/Stumpf.works-POS.git pos
cd pos
git checkout main  # or your production branch
```

### 2. Set Up Python Environment

```bash
cd backend
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create `/home/posapp/pos/backend/.env`:

```bash
# Application
APP_NAME="Stumpf.works POS"
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=postgresql+asyncpg://posuser:STRONG_PASSWORD@localhost:5432/pos_production

# Redis
REDIS_URL=redis://:YOUR_REDIS_PASSWORD@localhost:6379/0

# Security
SECRET_KEY=GENERATE_STRONG_SECRET_KEY_HERE
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=https://pos.yourdomain.com,https://app.yourdomain.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# Sentry (Error Tracking)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

# TSE (Fiskaly)
TSE_ENABLED=true
FISKALY_API_KEY=your_fiskaly_api_key
FISKALY_API_SECRET=your_fiskaly_api_secret

# SumUp
SUMUP_ENABLED=true
SUMUP_API_KEY=your_sumup_api_key
SUMUP_MERCHANT_CODE=your_merchant_code
```

**Generate SECRET_KEY:**

```python
import secrets
print(secrets.token_urlsafe(32))
```

### 4. Run Database Migrations

```bash
cd backend
source venv/bin/activate

# Run Alembic migrations
alembic upgrade head

# Initialize first tenant
python scripts/init_db.py
```

### 5. Set Up Systemd Service

Create `/etc/systemd/system/pos-api.service`:

```ini
[Unit]
Description=Stumpf.works POS API
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=posapp
Group=posapp
WorkingDirectory=/home/posapp/pos/backend
Environment="PATH=/home/posapp/pos/backend/venv/bin"
ExecStart=/home/posapp/pos/backend/venv/bin/uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-config logging.conf
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/posapp/pos/backend/logs /home/posapp/pos/backend/exports

[Install]
WantedBy=multi-user.target
```

### 6. Set Up Celery Workers

Create `/etc/systemd/system/pos-celery.service`:

```ini
[Unit]
Description=Stumpf.works POS Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=posapp
Group=posapp
WorkingDirectory=/home/posapp/pos/backend
Environment="PATH=/home/posapp/pos/backend/venv/bin"
ExecStart=/home/posapp/pos/backend/venv/bin/celery -A app.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --pidfile=/tmp/celery-worker.pid
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/pos-celery-beat.service`:

```ini
[Unit]
Description=Stumpf.works POS Celery Beat
After=network.target redis.service

[Service]
Type=simple
User=posapp
Group=posapp
WorkingDirectory=/home/posapp/pos/backend
Environment="PATH=/home/posapp/pos/backend/venv/bin"
ExecStart=/home/posapp/pos/backend/venv/bin/celery -A app.celery_app beat \
    --loglevel=info \
    --pidfile=/tmp/celery-beat.pid
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 7. Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable pos-api
sudo systemctl enable pos-celery
sudo systemctl enable pos-celery-beat

# Start services
sudo systemctl start pos-api
sudo systemctl start pos-celery
sudo systemctl start pos-celery-beat

# Check status
sudo systemctl status pos-api
sudo systemctl status pos-celery
```

---

## Frontend Deployment

### 1. Build Frontend

```bash
cd /home/posapp/pos/frontend

# Install dependencies
npm ci --production

# Build for production
npm run build
```

This creates an optimized build in `frontend/dist/`.

### 2. Copy to Web Root

```bash
sudo mkdir -p /var/www/pos
sudo cp -r dist/* /var/www/pos/
sudo chown -R www-data:www-data /var/www/pos
```

---

## Reverse Proxy (Nginx)

### Configuration

Create `/etc/nginx/sites-available/pos`:

```nginx
# Upstream for API
upstream pos_api {
    server 127.0.0.1:8000 fail_timeout=0;
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=3r/s;

# Frontend
server {
    listen 80;
    listen [::]:80;
    server_name pos.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name pos.yourdomain.com;

    # SSL Configuration (will be added by Certbot)
    # ssl_certificate /etc/letsencrypt/live/pos.yourdomain.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/pos.yourdomain.com/privkey.pem;

    # Security Headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Frontend
    root /var/www/pos;
    index index.html;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/javascript application/xml+rss application/json;

    # Frontend routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;

        proxy_pass http://pos_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }

    # Auth endpoints with stricter rate limiting
    location /api/v1/auth/ {
        limit_req zone=auth_limit burst=5 nodelay;

        proxy_pass http://pos_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health checks (no rate limiting)
    location /health {
        access_log off;
        proxy_pass http://pos_api;
    }

    # Static assets with long cache
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/pos /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## SSL/TLS Setup

### 1. Obtain SSL Certificate

```bash
# Let's Encrypt (Free)
sudo certbot --nginx -d pos.yourdomain.com

# Follow prompts
# Choose: Redirect HTTP to HTTPS
```

### 2. Auto-Renewal

Certbot auto-renewal is enabled by default. Test it:

```bash
sudo certbot renew --dry-run
```

---

## Monitoring & Logging

### 1. Application Logs

```bash
# View API logs
sudo journalctl -u pos-api -f

# View Celery logs
sudo journalctl -u pos-celery -f

# Application-specific logs
tail -f /home/posapp/pos/backend/logs/app.log
```

### 2. Sentry Setup

Already configured in `.env`. Monitor at: https://sentry.io

### 3. System Monitoring

Install monitoring tools:

```bash
# Prometheus Node Exporter
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar xvfz node_exporter-1.6.1.linux-amd64.tar.gz
sudo cp node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/
```

Create systemd service for Node Exporter:

```ini
[Unit]
Description=Prometheus Node Exporter
After=network.target

[Service]
Type=simple
User=nobody
ExecStart=/usr/local/bin/node_exporter
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Backup Strategy

### 1. Database Backups

Create `/home/posapp/backup_db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="pos_backup_$DATE.sql.gz"

mkdir -p $BACKUP_DIR

# Backup
pg_dump -U posuser pos_production | gzip > "$BACKUP_DIR/$FILENAME"

# Keep only last 30 days
find $BACKUP_DIR -name "pos_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $FILENAME"
```

Add to crontab:

```bash
# Daily backup at 2 AM
0 2 * * * /home/posapp/backup_db.sh >> /var/log/backup.log 2>&1
```

### 2. File Backups

Backup uploads, exports, and configuration:

```bash
# Use rsync or rclone to backup to external storage
rsync -avz /home/posapp/pos/backend/uploads/ /backups/uploads/
rsync -avz /home/posapp/pos/backend/exports/ /backups/exports/
```

---

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable firewall (UFW)
- [ ] Configure fail2ban
- [ ] SSL/TLS enabled
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Sentry error tracking configured
- [ ] Regular backups scheduled
- [ ] Database credentials secured
- [ ] Redis password set
- [ ] File permissions correct (`chmod 600 .env`)
- [ ] Disable unnecessary services
- [ ] Keep system updated
- [ ] Monitor logs regularly

### Firewall Setup

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### Fail2Ban

```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## Maintenance

### Updates

```bash
# Update code
cd /home/posapp/pos
git pull origin main

# Update dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Run migrations
alembic upgrade head

# Restart services
sudo systemctl restart pos-api
sudo systemctl restart pos-celery

# Rebuild frontend if needed
cd ../frontend
npm ci
npm run build
sudo cp -r dist/* /var/www/pos/
```

### Health Checks

```bash
# API health
curl https://pos.yourdomain.com/health

# Database
sudo -u postgres psql -c "SELECT version();"

# Redis
redis-cli -a YOUR_REDIS_PASSWORD ping
```

---

## Troubleshooting

See [Troubleshooting Guide](./troubleshooting.md) for common issues and solutions.

---

## Next Steps

1. Configure TSE settings in admin dashboard
2. Set up SumUp integration
3. Train staff on system usage
4. Set up monitoring alerts
5. Test backup restoration procedure
6. Plan for scaling if needed

---

**For support, contact:** support@stumpf.works
