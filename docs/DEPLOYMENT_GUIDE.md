# Digital Labor Backend - Deployment Guide

## Table of Contents

- [Development Environment](#development-environment)
- [Production Deployment](#production-deployment)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Web Server Configuration](#web-server-configuration)
- [Security Configuration](#security-configuration)
- [Monitoring and Logging](#monitoring-and-logging)
- [Backup and Recovery](#backup-and-recovery)
- [Troubleshooting](#troubleshooting)

## Development Environment

### Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd Digital-Labor-Backend/backend
   python -m venv env
   env\Scripts\activate  # Windows
   # source env/bin/activate  # Linux/Mac
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   Create `.env` file:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   EMAIL_HOST_USER=your-email@example.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

4. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

## Production Deployment

### Prerequisites

- Python 3.8+
- PostgreSQL 12+ (recommended) or MySQL 8.0+
- Nginx or Apache web server
- SSL certificate
- Domain name

### Deployment Options

#### Option 1: Traditional VPS/Server Deployment

1. **Server Setup**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install dependencies
   sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib
   ```

2. **Database Setup**
   ```bash
   # Create database and user
   sudo -u postgres psql
   CREATE DATABASE digitallabor;
   CREATE USER digitallabor_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE digitallabor TO digitallabor_user;
   \q
   ```

3. **Application Setup**
   ```bash
   # Create application directory
   sudo mkdir -p /var/www/digitallabor
   cd /var/www/digitallabor
   
   # Clone repository
   sudo git clone <repository-url> .
   
   # Setup virtual environment
   sudo python3 -m venv env
   sudo chown -R www-data:www-data /var/www/digitallabor
   sudo -u www-data env/bin/pip install -r requirements.txt
   ```

#### Option 2: Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   RUN python manage.py collectstatic --noinput
   
   EXPOSE 8000
   
   CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.wsgi:application"]
   ```

2. **Create docker-compose.yml**
   ```yaml
   version: '3.8'
   
   services:
     web:
       build: .
       ports:
         - "8000:8000"
       volumes:
         - .:/app
       depends_on:
         - db
       environment:
         - DEBUG=False
         - DATABASE_URL=postgresql://user:password@db:5432/digitallabor
   
     db:
       image: postgres:13
       volumes:
         - postgres_data:/var/lib/postgresql/data/
       environment:
         - POSTGRES_DB=digitallabor
         - POSTGRES_USER=user
         - POSTGRES_PASSWORD=password
   
     nginx:
       image: nginx:alpine
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf
         - ./ssl:/etc/nginx/ssl
       depends_on:
         - web
   
   volumes:
     postgres_data:
   ```

#### Option 3: Cloud Platform Deployment

**Heroku Deployment**

1. **Prepare for Heroku**
   ```bash
   # Install Heroku CLI
   # Create Procfile
   echo "web: gunicorn backend.wsgi:application" > Procfile
   
   # Create runtime.txt
   echo "python-3.11.0" > runtime.txt
   ```

2. **Deploy to Heroku**
   ```bash
   heroku create your-app-name
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   heroku addons:create heroku-postgresql:hobby-dev
   git push heroku main
   heroku run python manage.py migrate
   ```

## Environment Configuration

### Production Settings

Create `backend/settings/production.py`:

```python
from .base import *
import os
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# Database
DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
}

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (for production, use cloud storage)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/digitallabor/django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### Environment Variables

Set these environment variables for production:

```bash
# Core Django settings
export SECRET_KEY="your-very-secure-secret-key"
export DEBUG=False
export ALLOWED_HOSTS="your-domain.com,www.your-domain.com"

# Database
export DATABASE_URL="postgresql://user:password@localhost:5432/digitallabor"

# Email
export EMAIL_HOST_USER="your-email@example.com"
export EMAIL_HOST_PASSWORD="your-app-password"

# AWS S3 (if using)
export AWS_ACCESS_KEY_ID="your-aws-access-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
export AWS_STORAGE_BUCKET_NAME="your-bucket-name"
export AWS_S3_REGION_NAME="us-east-1"

# JWT Settings
export JWT_SECRET_KEY="your-jwt-secret-key"
```

## Database Setup

### PostgreSQL Production Setup

1. **Install PostgreSQL**
   ```bash
   sudo apt install postgresql postgresql-contrib
   ```

2. **Create Database**
   ```bash
   sudo -u postgres createdb digitallabor
   sudo -u postgres createuser digitallabor_user
   sudo -u postgres psql
   ```
   ```sql
   ALTER USER digitallabor_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE digitallabor TO digitallabor_user;
   ```

3. **Configure Django**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'digitallabor',
           'USER': 'digitallabor_user',
           'PASSWORD': 'secure_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

### Database Migrations

```bash
# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

## Web Server Configuration

### Nginx Configuration

Create `/etc/nginx/sites-available/digitallabor`:

```nginx
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /path/to/your/ssl/certificate.crt;
    ssl_certificate_key /path/to/your/ssl/private.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    client_max_body_size 50M;

    location /static/ {
        alias /var/www/digitallabor/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/digitallabor/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

### Gunicorn Configuration

Create `gunicorn.conf.py`:

```python
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 300
keepalive = 2
preload_app = True
user = "www-data"
group = "www-data"
tmp_upload_dir = None
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}
```

### Systemd Service

Create `/etc/systemd/system/digitallabor.service`:

```ini
[Unit]
Description=Digital Labor Backend
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/digitallabor
Environment=DJANGO_SETTINGS_MODULE=backend.settings.production
ExecStart=/var/www/digitallabor/env/bin/gunicorn --config gunicorn.conf.py backend.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable digitallabor
sudo systemctl start digitallabor
```

## Security Configuration

### SSL/TLS Setup

1. **Obtain SSL Certificate**
   ```bash
   # Using Let's Encrypt
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com -d www.your-domain.com
   ```

2. **Configure Auto-renewal**
   ```bash
   sudo crontab -e
   # Add this line:
   0 12 * * * /usr/bin/certbot renew --quiet
   ```

### Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22

# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow PostgreSQL (if external access needed)
sudo ufw allow 5432
```

### Django Security Settings

```python
# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CORS settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",
]
```

## Monitoring and Logging

### Application Monitoring

1. **Install Sentry** (Error tracking)
   ```bash
   pip install sentry-sdk[django]
   ```
   
   ```python
   import sentry_sdk
   from sentry_sdk.integrations.django import DjangoIntegration
   
   sentry_sdk.init(
       dsn="your-sentry-dsn",
       integrations=[DjangoIntegration()],
       traces_sample_rate=1.0,
       send_default_pii=True
   )
   ```

2. **Setup Health Check Endpoint**
   ```python
   # In views.py
   from django.http import JsonResponse
   from django.db import connection
   
   def health_check(request):
       try:
           connection.ensure_connection()
           return JsonResponse({"status": "healthy"})
       except Exception as e:
           return JsonResponse({"status": "unhealthy", "error": str(e)}, status=500)
   ```

### System Monitoring

1. **Install Prometheus and Grafana**
   ```bash
   # Add monitoring stack
   docker-compose -f monitoring-stack.yml up -d
   ```

2. **Log Rotation**
   ```bash
   # Create logrotate configuration
   sudo nano /etc/logrotate.d/digitallabor
   ```
   
   ```
   /var/log/digitallabor/*.log {
       daily
       missingok
       rotate 52
       compress
       delaycompress
       notifempty
       create 644 www-data www-data
       postrotate
           systemctl reload digitallabor
       endscript
   }
   ```

## Backup and Recovery

### Database Backup

1. **Automated Backup Script**
   ```bash
   #!/bin/bash
   # /etc/cron.daily/backup-digitallabor
   
   DATE=$(date +%Y%m%d_%H%M%S)
   BACKUP_DIR="/var/backups/digitallabor"
   
   mkdir -p $BACKUP_DIR
   
   # Database backup
   pg_dump -h localhost -U digitallabor_user digitallabor | gzip > $BACKUP_DIR/db_$DATE.sql.gz
   
   # Media files backup
   tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/digitallabor/media/
   
   # Keep only last 30 days
   find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
   ```

2. **Restore Procedure**
   ```bash
   # Restore database
   gunzip -c /var/backups/digitallabor/db_YYYYMMDD_HHMMSS.sql.gz | psql -h localhost -U digitallabor_user digitallabor
   
   # Restore media files
   tar -xzf /var/backups/digitallabor/media_YYYYMMDD_HHMMSS.tar.gz -C /
   ```

## Troubleshooting

### Common Issues

1. **Static Files Not Loading**
   ```bash
   python manage.py collectstatic --noinput
   sudo systemctl restart nginx
   ```

2. **Database Connection Issues**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   
   # Check Django database connectivity
   python manage.py dbshell
   ```

3. **Permission Issues**
   ```bash
   sudo chown -R www-data:www-data /var/www/digitallabor
   sudo chmod -R 755 /var/www/digitallabor
   ```

4. **Memory Issues**
   ```bash
   # Check memory usage
   free -m
   
   # Adjust Gunicorn workers
   # Edit gunicorn.conf.py and reduce workers if needed
   ```

### Log Files Locations

- Application logs: `/var/log/digitallabor/django.log`
- Nginx access logs: `/var/log/nginx/access.log`
- Nginx error logs: `/var/log/nginx/error.log`
- System logs: `journalctl -u digitallabor`

### Performance Optimization

1. **Database Optimization**
   ```sql
   -- Analyze database performance
   EXPLAIN ANALYZE SELECT * FROM api_job WHERE status = 'open';
   
   -- Add indexes for frequently queried fields
   CREATE INDEX idx_job_status ON api_job(status);
   ```

2. **Caching**
   ```python
   # Install Redis
   pip install redis django-redis
   
   # Configure caching in settings.py
   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
           'OPTIONS': {
               'CLIENT_CLASS': 'django_redis.client.DefaultClient',
           }
       }
   }
   ```

3. **CDN Setup**
   - Use AWS CloudFront or similar CDN for static files
   - Configure proper cache headers
   - Optimize images and media files

This deployment guide provides comprehensive instructions for deploying the Digital Labor Backend in various environments. Always test deployments in staging environments before applying to production.
