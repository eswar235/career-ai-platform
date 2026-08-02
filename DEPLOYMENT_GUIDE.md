# Production Deployment Guide - Career AI SaaS Platform

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Database Setup](#database-setup)
5. [SSL/TLS Configuration](#ssltls-configuration)
6. [Monitoring & Logging](#monitoring--logging)
7. [Scaling & Performance](#scaling--performance)
8. [Backup & Recovery](#backup--recovery)
9. [Security Hardening](#security-hardening)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ or CentOS 8+
- **CPU**: Minimum 2 cores (4+ recommended)
- **RAM**: Minimum 4GB (8GB+ recommended)
- **Storage**: Minimum 50GB SSD (100GB+ recommended)
- **Bandwidth**: 50 Mbps minimum

### Software Requirements
- Docker 20.10+
- Docker Compose 1.29+
- Git 2.30+
- OpenSSL 1.1+

### Installation
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

---

## Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-org/career-ai-platform.git
cd career-ai-platform
```

### 2. Create Environment Files

**Backend (.env)**
```bash
# Database
DB_USER=postgres
DB_PASSWORD=<GENERATE_STRONG_PASSWORD>
DB_NAME=career_ai_prod
DATABASE_URL=postgresql://postgres:<PASSWORD>@postgres:5432/career_ai_prod

# JWT & Security
JWT_SECRET=<GENERATE_STRONG_SECRET>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=720

# Environment
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# API Configuration
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Third-party APIs
OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>

# Email Configuration (optional)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<SENDGRID_API_KEY>
SENDER_EMAIL=noreply@yourdomain.com

# Redis (optional)
REDIS_PASSWORD=<GENERATE_STRONG_PASSWORD>
REDIS_URL=redis://:PASSWORD@redis:6379/0
```

**Frontend (.env.local)**
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_ENVIRONMENT=production
```

### 3. Generate Secure Secrets
```bash
# Generate JWT Secret
openssl rand -base64 32

# Generate Database Password
openssl rand -base64 16

# Generate Redis Password
openssl rand -base64 16
```

---

## Docker Deployment

### 1. Build Images
```bash
# Build backend image
docker build -f backend/Dockerfile.prod -t career-ai-backend:latest ./backend

# Build frontend image
docker build -f frontend/Dockerfile.prod -t career-ai-frontend:latest ./frontend

# Optional: Push to Docker Registry
docker tag career-ai-backend:latest registry.example.com/career-ai-backend:latest
docker push registry.example.com/career-ai-backend:latest
```

### 2. Deploy with Docker Compose
```bash
# Create SSL certificates (first time)
mkdir -p ssl
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Verify services
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f
```

### 3. Initialize Database
```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Create admin user
docker-compose -f docker-compose.prod.yml exec backend python scripts/create_admin.py \
  --email admin@yourdomain.com \
  --password <ADMIN_PASSWORD>
```

---

## Database Setup

### PostgreSQL Configuration

#### Backup Strategy
```bash
# Automated daily backups
0 2 * * * /usr/local/bin/backup-db.sh > /var/log/backup.log 2>&1

# Backup script (backup-db.sh)
#!/bin/bash
BACKUP_DIR="/backups/postgresql"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker exec career-ai-postgres pg_dump -U postgres career_ai_prod | \
  gzip > $BACKUP_DIR/career_ai_$TIMESTAMP.sql.gz
# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete
```

#### Connection Pooling
```sql
-- Create pgBouncer for connection pooling
[databases]
career_ai_prod = host=postgres port=5432 dbname=career_ai_prod user=postgres password=PASSWORD

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
min_pool_size = 10
reserve_pool_size = 5
reserve_pool_timeout = 3
max_db_connections = 100
max_user_connections = 100
```

---

## SSL/TLS Configuration

### Using Let's Encrypt with Certbot
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Copy certificates to Nginx
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/key.pem
sudo chmod 644 ssl/cert.pem ssl/key.pem
```

### Certificate Monitoring
```bash
# Check certificate expiration
certbot certificates

# Set up renewal reminder (14 days before expiration)
0 12 * * * certbot renew --quiet && \
  cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/cert.pem && \
  cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/key.pem && \
  docker-compose -f docker-compose.prod.yml restart nginx
```

---

## Monitoring & Logging

### Docker Logging
```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f nginx

# Centralized logging with ELK Stack
# docker-compose.prod.yml includes logging driver config
```

### Health Checks
```bash
# Manual health checks
curl https://yourdomain.com/health
curl https://yourdomain.com/api/health

# Automated monitoring
watch -n 5 'docker-compose -f docker-compose.prod.yml ps'
```

### Application Monitoring
```python
# app/core/monitoring.py configuration
# Metrics collection for:
# - Request response times
# - Database query performance
# - Error rates
# - System resource usage
# - User activity tracking
```

---

## Scaling & Performance

### Horizontal Scaling
```yaml
# Multiple backend instances behind load balancer
upstream backend {
    least_conn;
    server backend-1:8000;
    server backend-2:8000;
    server backend-3:8000;
    keepalive 32;
}
```

### Caching Strategy
```bash
# Redis caching for:
# - Session tokens
# - Job listings (1 hour TTL)
# - Match scores (4 hour TTL)
# - User profiles (6 hour TTL)
# - Job alerts (30 min TTL)

# Cache invalidation on updates
```

### Database Optimization
```sql
-- Index optimization
CREATE INDEX idx_applications_user_id_date ON job_applications(user_id, applied_date DESC);
CREATE INDEX idx_jobs_source_date ON jobs(source, posted_date DESC);
CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read);

-- Query statistics
SELECT query, calls, total_time FROM pg_stat_statements ORDER BY mean_time DESC;
```

---

## Backup & Recovery

### Automated Backups
```bash
# Daily full backups
0 2 * * * docker exec career-ai-postgres pg_dump -U postgres career_ai_prod | gzip > /backups/$(date +%Y%m%d).sql.gz

# Weekly incremental backups with PITR
# Continuous archiving enabled in PostgreSQL
```

### Recovery Procedure
```bash
# Restore from backup
gunzip < /backups/20240115.sql.gz | docker exec -i career-ai-postgres psql -U postgres

# Point-in-time recovery (if WAL archiving enabled)
# Contact DevOps team for PITR procedures
```

---

## Security Hardening

### Network Security
```bash
# Firewall rules
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 5432/tcp from INTERNAL_NETWORK  # PostgreSQL
sudo ufw enable
```

### Container Security
```bash
# Run containers with security options
docker run --security-opt=no-new-privileges \
           --cap-drop=ALL \
           --cap-add=NET_BIND_SERVICE \
           --read-only \
           --tmpfs /tmp
```

### API Security
```bash
# Rate limiting (handled by Nginx and FastAPI)
# 100 requests/minute for API endpoints
# 1000 requests/minute for frontend

# JWT token validation on every request
# Password hashing with bcrypt (cost factor 12+)
# CORS configuration restricted to known domains
```

### Data Security
```bash
# Encryption at rest
# PostgreSQL with pgcrypto extension
# Sensitive data encrypted with AES-256

# Encryption in transit
# TLS 1.2+ required
# HTTPS only communication

# Data privacy
# GDPR compliant data retention
# User data deletion within 30 days of request
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Check database service
docker-compose -f docker-compose.prod.yml ps postgres

# Check logs
docker-compose -f docker-compose.prod.yml logs postgres

# Verify connection
docker-compose -f docker-compose.prod.yml exec backend \
  psql -h postgres -U postgres -d career_ai_prod -c "SELECT 1"
```

#### 2. Memory Issues
```bash
# Monitor container resources
docker stats

# Increase Docker memory limit
docker update --memory=4g career-ai-backend

# Check application memory usage
docker-compose -f docker-compose.prod.yml exec backend \
  python -c "import psutil; print(psutil.virtual_memory())"
```

#### 3. SSL Certificate Issues
```bash
# Verify certificate validity
openssl x509 -in ssl/cert.pem -text -noout

# Regenerate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes

# Restart Nginx to apply changes
docker-compose -f docker-compose.prod.yml restart nginx
```

#### 4. Performance Issues
```bash
# Check slow queries
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U postgres -d career_ai_prod \
  -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10"

# Clear query cache
docker-compose -f docker-compose.prod.yml exec redis redis-cli FLUSHDB
```

### Recovery Checklist
- [ ] Verify all services are running
- [ ] Check database connectivity
- [ ] Verify SSL certificates are valid
- [ ] Test API endpoints
- [ ] Monitor application logs
- [ ] Check resource utilization
- [ ] Verify backup completion

---

## Maintenance Windows

### Weekly Maintenance (Sunday 2:00 AM UTC)
- Database optimization
- Log rotation
- Security updates check

### Monthly Maintenance (First Sunday, 2:00 AM UTC)
- Full system backup verification
- Dependency updates
- Performance review

### Quarterly Maintenance
- Security audit
- Certificate renewal check
- Disaster recovery drill

---

## Support & Escalation

### Contact Information
- **Technical Issues**: devops@yourdomain.com
- **Security Incidents**: security@yourdomain.com
- **24/7 Hotline**: +1-XXX-XXX-XXXX

### Incident Response
1. Alert on-call engineer
2. Assess severity
3. Initiate recovery procedure
4. Notify stakeholders
5. Document incident
6. Post-mortem within 48 hours

---

## Performance Targets

- **API Response Time**: < 500ms (p95)
- **Database Query Time**: < 100ms (p95)
- **Uptime SLA**: 99.9%
- **Error Rate**: < 0.1%
- **CPU Usage**: < 70%
- **Memory Usage**: < 80%
- **Disk Usage**: < 85%

---

## Compliance & Auditing

- GDPR compliance verified
- Data encryption at rest and in transit
- Audit logging for all admin actions
- 90-day log retention
- Quarterly security audits
- Automated vulnerability scanning

---

For detailed troubleshooting, check application logs or contact the DevOps team.
