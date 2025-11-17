# Deployment Guide

This guide covers deploying OneTimeSecret to production environments.

## Prerequisites

- Docker and Docker Compose (recommended)
- OR: Python 3.11+, PostgreSQL 15+, Redis 7+
- SSL/TLS certificate
- Domain name (recommended)

## Quick Deploy with Docker

### 1. Clone and Configure

```bash
git clone https://github.com/onetimesecret/ots5.git
cd ots5

# Copy environment template
cp .env.example .env

# Generate secret key
openssl rand -hex 32

# Edit .env with your configuration
nano .env
```

### 2. Configure Environment

Edit `.env` with production values:

```bash
# CRITICAL: Change these!
SECRET_KEY=your-generated-secret-key-here
SSL_ENABLED=true
ENVIRONMENT=production
DEBUG=false

# Database
DATABASE_URL=postgresql+asyncpg://ots:STRONG_PASSWORD@postgres:5432/onetimesecret

# Redis
REDIS_URL=redis://redis:6379/0

# CORS (your domain)
CORS_ORIGINS=https://yourdomain.com

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
```

### 3. Deploy

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Check health
curl http://localhost:8000/api/v3/health
```

### 4. Set Up Reverse Proxy

Use nginx or Caddy for SSL termination:

**Nginx Example:**

```nginx
server {
    listen 443 ssl http2;
    server_name secrets.yourdomain.com;

    ssl_certificate /etc/ssl/certs/yourdomain.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.key;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Caddy Example:**

```
secrets.yourdomain.com {
    reverse_proxy localhost:8000
}
```

## Manual Deployment

### 1. System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv postgresql-15 redis-server nginx

# Create user
sudo useradd -m -s /bin/bash ots
sudo su - ots
```

### 2. Application Setup

```bash
# Clone repository
git clone https://github.com/onetimesecret/ots5.git
cd ots5

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements/prod.txt

# Configure
cp .env.example .env
nano .env  # Edit configuration
```

### 3. Database Setup

```bash
# Create database
sudo -u postgres psql
CREATE DATABASE onetimesecret;
CREATE USER ots WITH PASSWORD 'STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE onetimesecret TO ots;
\q

# Run migrations
alembic upgrade head
```

### 4. Systemd Service

Create `/etc/systemd/system/onetimesecret.service`:

```ini
[Unit]
Description=OneTimeSecret API Server
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=ots
Group=ots
WorkingDirectory=/home/ots/ots5
Environment="PATH=/home/ots/ots5/venv/bin"
ExecStart=/home/ots/ots5/venv/bin/gunicorn \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/log/onetimesecret/access.log \
    --error-logfile /var/log/onetimesecret/error.log \
    onetimesecret.main:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable onetimesecret
sudo systemctl start onetimesecret
sudo systemctl status onetimesecret
```

### 5. Celery Workers

Create `/etc/systemd/system/onetimesecret-worker.service`:

```ini
[Unit]
Description=OneTimeSecret Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=ots
Group=ots
WorkingDirectory=/home/ots/ots5
Environment="PATH=/home/ots/ots5/venv/bin"
ExecStart=/home/ots/ots5/venv/bin/celery -A onetimesecret.services.tasks worker --loglevel=info

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/onetimesecret-beat.service`:

```ini
[Unit]
Description=OneTimeSecret Celery Beat
After=network.target redis.service

[Service]
Type=forking
User=ots
Group=ots
WorkingDirectory=/home/ots/ots5
Environment="PATH=/home/ots/ots5/venv/bin"
ExecStart=/home/ots/ots5/venv/bin/celery -A onetimesecret.services.tasks beat --loglevel=info

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Cloud Deployments

### AWS

**Using ECS:**

1. Push image to ECR
2. Create ECS task definition
3. Set up RDS PostgreSQL
4. Set up ElastiCache Redis
5. Deploy ECS service with ALB

**Using EC2:**

Follow manual deployment guide above.

### Google Cloud Platform

**Using Cloud Run:**

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/onetimesecret

# Deploy
gcloud run deploy onetimesecret \
  --image gcr.io/PROJECT_ID/onetimesecret \
  --platform managed \
  --region us-central1 \
  --set-env-vars SECRET_KEY=xxx,DATABASE_URL=xxx
```

### DigitalOcean

**Using App Platform:**

1. Connect GitHub repository
2. Configure environment variables
3. Add PostgreSQL and Redis databases
4. Deploy

## Kubernetes

Example deployment manifests:

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: onetimesecret
spec:
  replicas: 3
  selector:
    matchLabels:
      app: onetimesecret
  template:
    metadata:
      labels:
        app: onetimesecret
    spec:
      containers:
      - name: onetimesecret
        image: onetimesecret:latest
        ports:
        - containerPort: 8000
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: ots-secrets
              key: secret-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: ots-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## Monitoring

### Health Checks

```bash
# Application health
curl https://yourdomain.com/api/v3/health

# Database
psql $DATABASE_URL -c "SELECT 1"

# Redis
redis-cli ping
```

### Logging

Configure centralized logging:

```python
# In .env
LOG_LEVEL=INFO
LOG_FORMAT=json
```

Send logs to:
- CloudWatch (AWS)
- Stackdriver (GCP)
- ELK Stack
- Datadog

### Metrics

Recommended metrics to monitor:
- Request rate
- Response time
- Error rate
- Secret creation rate
- Database connections
- Redis memory usage
- CPU/Memory usage

## Backup

### Database

```bash
# Automated backup
pg_dump $DATABASE_URL > backup-$(date +%Y%m%d).sql

# Restore
psql $DATABASE_URL < backup-20240101.sql
```

### Configuration

- Store `.env` securely
- Back up SSL certificates
- Document configuration changes

## Security Hardening

1. **Firewall Rules**
   ```bash
   # Allow only necessary ports
   ufw allow 22/tcp
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw enable
   ```

2. **Database Security**
   - Use strong passwords
   - Limit network access
   - Enable SSL connections
   - Regular security updates

3. **Application Security**
   - Keep dependencies updated
   - Run security scans
   - Monitor access logs
   - Use WAF if available

## Troubleshooting

### Application won't start

```bash
# Check logs
docker-compose logs app

# Or systemd
journalctl -u onetimesecret -f
```

### Database connection issues

```bash
# Test connection
psql $DATABASE_URL

# Check PostgreSQL status
sudo systemctl status postgresql
```

### Redis connection issues

```bash
# Test connection
redis-cli -u $REDIS_URL ping

# Check Redis status
sudo systemctl status redis
```

## Updates

### Docker

```bash
# Pull latest image
docker-compose pull

# Restart services
docker-compose up -d
```

### Manual

```bash
# Pull updates
cd /home/ots/ots5
git pull

# Update dependencies
source venv/bin/activate
pip install -r requirements/prod.txt

# Run migrations
alembic upgrade head

# Restart service
sudo systemctl restart onetimesecret
```

## Support

For deployment assistance:
- GitHub Issues: https://github.com/onetimesecret/ots5/issues
- Email: support@onetimesecret.com
