# Deployment Guide

This guide covers production deployment of the IoT Fleet Monitor application on Ubuntu/Linux servers.

## Prerequisites

### System Requirements

- Ubuntu 20.04 LTS or later
- 2+ CPU cores
- 4GB+ RAM
- 20GB+ available disk space
- Sudo/root access

### Software Requirements

- Docker Engine 24.0+
- Docker Compose v2
- Nginx (optional, for reverse proxy)
- SSL certificates (for HTTPS)

## Server Preparation

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Verify installation
docker --version
```

### 3. Install Docker Compose

```bash
sudo apt install docker-compose-plugin -y
docker compose version
```

### 4. Install Additional Tools

```bash
sudo apt install -y git nginx certbot python3-certbot-nginx
```

## Application Deployment

### 1. Create Application Directory

```bash
sudo mkdir -p /opt/iot-fleet-monitor
sudo chown $USER:$USER /opt/iot-fleet-monitor
cd /opt/iot-fleet-monitor
```

### 2. Clone Repository

```bash
git clone <repository-url> .
```

### 3. Configure Environment

Create production environment file:

```bash
cat > .env << 'EOF'
DATABASE_URL=postgresql+asyncpg://iot_user:CHANGE_PASSWORD@postgres:5432/iot_monitor
DATABASE_URL_SYNC=postgresql://iot_user:CHANGE_PASSWORD@postgres:5432/iot_monitor
CRITICAL_TEMP_THRESHOLD=80.0
EOF

chmod 600 .env
```

**Important**: Replace `CHANGE_PASSWORD` with a strong password.

### 4. Update Docker Compose for Production

Edit `docker-compose.yml` to remove PGAdmin (security) and adjust settings:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: iot_postgres
    environment:
      POSTGRES_USER: iot_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: iot_monitor
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always
    networks:
      - iot_network

  api:
    build: .
    container_name: iot_api
    environment:
      DATABASE_URL: postgresql+asyncpg://iot_user:${DB_PASSWORD}@postgres:5432/iot_monitor
    ports:
      - "127.0.0.1:8000:8000"
    depends_on:
      - postgres
    restart: always
    networks:
      - iot_network

volumes:
  postgres_data:

networks:
  iot_network:
```

### 5. Start Services

```bash
docker compose up -d
```

### 6. Verify Deployment

```bash
# Check container status
docker compose ps

# Check logs
docker compose logs -f api

# Test health endpoint
curl http://localhost:8000/health
```

## Nginx Configuration

### 1. Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/iot-monitor
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 2. Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/iot-monitor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Configure SSL

```bash
sudo certbot --nginx -d your-domain.com
```

Follow the prompts to configure HTTPS.

## Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

## Systemd Service (Optional)

Create a systemd service for automatic startup:

```bash
sudo nano /etc/systemd/system/iot-monitor.service
```

Add:

```ini
[Unit]
Description=IoT Fleet Monitor
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/iot-fleet-monitor
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
User=your-username

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable iot-monitor
sudo systemctl start iot-monitor
```

## Database Backup

### Automated Backup Script

Create backup script:

```bash
nano /opt/iot-fleet-monitor/backup.sh
```

Add:

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/iot-monitor"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

docker exec iot_postgres pg_dump -U iot_user iot_monitor > \
  $BACKUP_DIR/backup_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete

echo "Backup completed: backup_$DATE.sql"
```

Make executable:

```bash
chmod +x /opt/iot-fleet-monitor/backup.sh
```

### Schedule with Cron

```bash
crontab -e
```

Add daily backup at 2 AM:

```
0 2 * * * /opt/iot-fleet-monitor/backup.sh >> /var/log/iot-backup.log 2>&1
```

## Monitoring

### Check Logs

```bash
# Application logs
docker compose logs -f api

# Database logs
docker compose logs -f postgres

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Resource Monitoring

```bash
# Container resource usage
docker stats

# System resources
htop
```

### Health Checks

```bash
# API health
curl https://your-domain.com/health

# Database connection
docker exec -it iot_postgres psql -U iot_user -d iot_monitor -c "SELECT 1;"
```

## Maintenance

### Update Application

```bash
cd /opt/iot-fleet-monitor
git pull
docker compose build --no-cache
docker compose up -d
```

### Database Restore

```bash
# Restore from backup
docker exec -i iot_postgres psql -U iot_user -d iot_monitor < backup.sql
```

### Clean Docker Resources

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Full cleanup
docker system prune -a --volumes
```

## Performance Tuning

### Increase Uvicorn Workers

Edit `Dockerfile`:

```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "8"]
```

### Adjust Database Connections

Edit `app/database.py`:

```python
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=40,
)
```

### Nginx Tuning

Add to nginx configuration:

```nginx
worker_processes auto;
worker_connections 1024;

http {
    keepalive_timeout 65;
    gzip on;
    gzip_types text/plain application/json;
}
```

## Security Checklist

- [ ] Strong database passwords
- [ ] SSL/TLS enabled
- [ ] Firewall configured
- [ ] Regular security updates
- [ ] Database backups automated
- [ ] Logs monitored
- [ ] Non-root containers
- [ ] Environment variables secured
- [ ] CORS properly configured
- [ ] Rate limiting enabled (if needed)

## Scaling

### Horizontal Scaling

For high-traffic deployments, consider:

1. Load balancer (Nginx, HAProxy)
2. Multiple API instances
3. Database replication (read replicas)
4. Container orchestration (Kubernetes, Docker Swarm)

### Vertical Scaling

1. Increase server resources (CPU, RAM)
2. Optimize database queries
3. Add caching layer (Redis)
4. Use CDN for static assets

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker compose logs

# Rebuild containers
docker compose down
docker compose build --no-cache
docker compose up -d
```

### High Memory Usage

```bash
# Check resource usage
docker stats

# Restart services
docker compose restart
```

### Database Connection Issues

```bash
# Check PostgreSQL logs
docker compose logs postgres

# Verify network
docker network inspect iot-fleet-monitor_iot_network

# Test connection
docker exec -it iot_postgres psql -U iot_user -d iot_monitor
```

### SSL Certificate Issues

```bash
# Renew certificate
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

## Support

For additional support:
- Check application logs
- Review GitHub issues
- Contact system administrator

## References

- Docker Documentation: https://docs.docker.com
- Nginx Documentation: https://nginx.org/en/docs/
- FastAPI Documentation: https://fastapi.tiangolo.com
- PostgreSQL Documentation: https://www.postgresql.org/docs/
