# Operational Runbooks - Career AI Platform

Quick reference guides for common operational tasks and incident response.

## Table of Contents
1. [Daily Operations](#daily-operations)
2. [Incident Response](#incident-response)
3. [Scaling Operations](#scaling-operations)
4. [Maintenance Windows](#maintenance-windows)
5. [Emergency Procedures](#emergency-procedures)
6. [Troubleshooting](#troubleshooting)

---

## Daily Operations

### Health Check

**Frequency**: Every 4 hours

```bash
#!/bin/bash
# health_check.sh

# Check backend
echo "Checking backend health..."
curl -f http://localhost:8000/health || echo "FAILED: Backend health check"

# Check frontend
echo "Checking frontend health..."
curl -f http://localhost:3000 || echo "FAILED: Frontend health check"

# Check database
echo "Checking database..."
docker exec career-ai-postgres pg_isready -U postgres || echo "FAILED: Database health check"

# Check Redis
echo "Checking Redis..."
docker exec career-ai-redis redis-cli ping || echo "FAILED: Redis health check"

# Check disk space
echo "Checking disk space..."
docker exec career-ai-backend df -h / | tail -1

# Check container status
echo "Checking container status..."
docker-compose ps
```

**Alert Contacts**: 
- On-call engineer
- DevOps team Slack channel
- Pagerduty (if critical)

### Disk Space Monitoring

**Daily check**:

```bash
#!/bin/bash
# monitor_disk.sh

THRESHOLD=80  # Alert when disk usage > 80%

USAGE=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)

if [ $USAGE -gt $THRESHOLD ]; then
    echo "ALERT: Disk usage is ${USAGE}%"
    # Send to monitoring system
    curl -X POST https://monitoring.example.com/alerts \
         -H "Content-Type: application/json" \
         -d "{\"alert\": \"disk_usage_high\", \"value\": ${USAGE}}"
fi
```

### Log Rotation

**Automated via Docker**:

```yaml
# Already configured in docker-compose.prod.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

---

## Incident Response

### Issue: High API Latency

**Symptoms**: 
- API response times > 2 seconds
- User complaints about slowness
- Prometheus alert: `HighLatency`

**Investigation**:

```bash
# 1. Check recent logs for errors
docker-compose logs --tail=100 backend | grep -i error

# 2. Check database performance
docker exec career-ai-postgres psql -U postgres -c \
  "SELECT query, calls, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# 3. Check active connections
docker exec career-ai-postgres psql -U postgres -c \
  "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"

# 4. Check backend metrics
curl http://localhost:8000/metrics | grep http_request_duration

# 5. Check system resources
docker stats --no-stream
```

**Resolution**:

```bash
# Option 1: Restart backend service
docker-compose restart backend

# Option 2: Scale backend instances
docker-compose up -d --scale backend=3

# Option 3: Clear cache
docker exec career-ai-redis redis-cli FLUSHALL

# Option 4: Identify slow queries and optimize
# - Check query logs
# - Add missing indexes
# - Refactor N+1 queries
```

**Post-incident**:
1. Document root cause
2. Add monitoring alert if needed
3. Create ticket for optimization
4. Notify stakeholders of resolution

---

### Issue: Database Connection Pool Exhaustion

**Symptoms**:
- Errors: "pool size exhausted"
- Failed API requests with 503
- Alert: `DatabaseConnectionExhaustion`

**Investigation**:

```bash
# Check current connections
docker exec career-ai-postgres psql -U postgres -c \
  "SELECT pid, usename, application_name, state FROM pg_stat_activity;"

# Check max connections
docker exec career-ai-postgres psql -U postgres -c \
  "SELECT setting FROM pg_settings WHERE name = 'max_connections';"

# Check backend logs for connection errors
docker-compose logs backend | grep -i "connection"
```

**Resolution**:

```bash
# Option 1: Restart backend to reset connections
docker-compose restart backend

# Option 2: Increase connection limit
# Edit docker-compose.prod.yml and increase POSTGRES_INITDB_ARGS
# Example: "-c max_connections=300"
docker-compose up -d --force-recreate

# Option 3: Kill idle connections
docker exec career-ai-postgres psql -U postgres -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < now() - interval '30 minutes';"
```

---

### Issue: Memory Leak in Backend

**Symptoms**:
- Memory usage gradually increasing
- Backend crash after 24+ hours
- Alert: `HighMemoryUsage`

**Investigation**:

```bash
# Monitor memory over time
watch -n 5 'docker stats career-ai-backend --no-stream'

# Check for specific memory issue
docker exec career-ai-backend python -m memory_profiler app/main.py

# Generate memory dump
docker exec career-ai-backend kill -USR2 $(pidof python)
```

**Resolution**:

1. **Identify the leak**:
   - Review recent code changes
   - Check for circular references
   - Look for unclosed resources

2. **Fix and deploy**:
   ```bash
   # Create hotfix branch
   git checkout -b hotfix/memory-leak
   # Fix code
   git push origin hotfix/memory-leak
   # Create PR and merge
   ```

3. **Deploy**:
   ```bash
   docker-compose up -d --build backend
   ```

4. **Monitor**:
   ```bash
   # Watch memory for 24 hours
   watch -n 300 'docker stats career-ai-backend --no-stream'
   ```

---

### Issue: Frontend Not Loading

**Symptoms**:
- Blank page
- 404 errors
- Frontend container crashes

**Investigation**:

```bash
# Check frontend container status
docker-compose ps frontend

# Check frontend logs
docker-compose logs frontend --tail=50

# Check if frontend is listening
docker exec career-ai-frontend curl http://localhost:3000

# Check Nginx configuration
docker exec career-ai-nginx nginx -t
```

**Resolution**:

```bash
# Option 1: Restart frontend
docker-compose restart frontend

# Option 2: Rebuild frontend
docker-compose up -d --build frontend

# Option 3: Check Nginx configuration
docker exec career-ai-nginx cat /etc/nginx/nginx.conf

# Option 4: Clear frontend cache
docker exec career-ai-frontend rm -rf .next/cache
docker-compose restart frontend
```

---

## Scaling Operations

### Horizontal Scaling

**Add more backend instances**:

```bash
# Scale to 3 instances
docker-compose up -d --scale backend=3

# Update Nginx load balancing
docker exec career-ai-nginx nginx -s reload

# Verify all instances are healthy
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
```

**Monitor load distribution**:

```bash
# Check Nginx upstream status
docker exec career-ai-nginx curl http://localhost:8080/upstream_health
```

### Vertical Scaling

**Increase resource limits**:

```yaml
# In docker-compose.prod.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

**Apply changes**:

```bash
docker-compose up -d --force-recreate
```

### Database Scaling

**Read Replicas**:

```sql
-- Create read replica
-- Connection from primary to replica server
-- PRIMARY_IP=primary.example.com

ssh ubuntu@replica.example.com
sudo -i
pg_basebackup -h PRIMARY_IP -D /var/lib/postgresql/data -U postgres -v -P -W
```

**Connection pooling**:

```bash
# Install PgBouncer
docker run -d \
  --name pgbouncer \
  --network career-ai-network \
  -e DATABASES_HOST=postgres \
  -e DATABASES_USER=postgres \
  -e DATABASES_PASSWORD=$DB_PASSWORD \
  pgbouncer:latest
```

---

## Maintenance Windows

### Database Maintenance

**Schedule**: Weekly, Sunday 2-4 AM

**Tasks**:

```bash
#!/bin/bash
# db_maintenance.sh

# 1. Analyze and reindex
docker exec career-ai-postgres psql -U postgres career_ai_prod << EOF
ANALYZE;
REINDEX DATABASE career_ai_prod;
EOF

# 2. Vacuum
docker exec career-ai-postgres psql -U postgres career_ai_prod << EOF
VACUUM ANALYZE;
EOF

# 3. Check table sizes
docker exec career-ai-postgres psql -U postgres career_ai_prod << EOF
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
EOF
```

### Certificate Renewal

**Schedule**: Monthly or auto-renewal

```bash
#!/bin/bash
# renew_certificates.sh

cd /opt/career-ai-platform

# Using Let's Encrypt with certbot
docker run --rm \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/lib/letsencrypt:/var/lib/letsencrypt \
  -v /var/log/letsencrypt:/var/log/letsencrypt \
  -p 80:80 -p 443:443 \
  certbot/certbot renew --quiet

# Reload Nginx
docker exec career-ai-nginx nginx -s reload

# Notify team
echo "SSL certificates renewed successfully"
```

### Dependency Updates

**Schedule**: Monthly

```bash
# Check for updates
docker-compose pull

# Test in staging first
# ... run tests ...

# Deploy to production
docker-compose up -d --pull always
```

---

## Emergency Procedures

### Service Outage Response

**Immediate Response** (0-5 min):

```bash
#!/bin/bash
# emergency_response.sh

# 1. Declare incident
echo "INCIDENT: Service outage detected"
echo "Time: $(date)"
echo "Assigned to: <on-call engineer>"

# 2. Notify stakeholders
curl -X POST $SLACK_WEBHOOK \
  -H 'Content-Type: application/json' \
  -d '{"text": "🚨 SERVICE OUTAGE: API unavailable - investigating..."}'

# 3. Attempt auto-recovery
docker-compose restart

# 4. Monitor recovery
watch -n 2 'docker-compose ps'
```

**Investigation Phase** (5-15 min):

```bash
# Check all services
docker-compose ps

# Review recent logs
docker-compose logs --tail=200 --timestamps

# Check system resources
docker stats

# Verify database
docker exec career-ai-postgres pg_isready
```

**Communication**:
- Update status page
- Notify customers
- Post updates every 15 minutes

---

### Data Loss Recovery

**From Backup**:

```bash
#!/bin/bash
# restore_from_backup.sh

BACKUP_FILE=$1  # e.g., backup_20240115_120000.sql

# 1. Stop services
docker-compose down

# 2. Restore database
docker-compose up -d postgres
sleep 10

# 3. Load backup
docker exec -i career-ai-postgres psql -U postgres < $BACKUP_FILE

# 4. Verify restore
docker exec career-ai-postgres psql -U postgres -c "SELECT COUNT(*) FROM users;"

# 5. Restart services
docker-compose up -d
```

**Pre-incident Preparation**:
- Automated daily backups
- Test restore procedure monthly
- Document recovery time objective (RTO)

---

## Troubleshooting

### SSH into Container

```bash
# Backend
docker exec -it career-ai-backend /bin/bash

# Frontend
docker exec -it career-ai-frontend /bin/sh

# Database
docker exec -it career-ai-postgres /bin/bash
```

### Debug Network Issues

```bash
# Check DNS
docker exec career-ai-backend nslookup postgres

# Test connectivity
docker exec career-ai-backend nc -zv postgres 5432

# Inspect network
docker network inspect career-ai-network
```

### Check File Permissions

```bash
# In backend container
docker exec career-ai-backend ls -la /app
docker exec career-ai-backend ls -la /app/uploads

# Fix permissions if needed
docker exec career-ai-backend chmod -R 755 /app/uploads
```

### View Environment Variables

```bash
# Backend
docker exec career-ai-backend env | sort

# Frontend
docker exec career-ai-frontend env | sort
```

### Database Query Debugging

```bash
# Connect to database
docker exec -it career-ai-postgres psql -U postgres career_ai_prod

# List tables
\dt

# View schema
\d table_name

# Explain query
EXPLAIN ANALYZE SELECT * FROM users WHERE id = 1;

# Monitor active queries
SELECT * FROM pg_stat_activity WHERE state = 'active';
```

---

## Quick Commands Reference

```bash
# Status
docker-compose ps
docker-compose logs -f

# Restart services
docker-compose restart
docker-compose restart backend
docker-compose restart frontend

# Update and deploy
docker-compose pull
docker-compose up -d

# View metrics
curl http://localhost:8000/metrics
docker stats

# Database backup
docker exec career-ai-postgres pg_dump -U postgres career_ai_prod > backup.sql

# Database restore
docker exec -i career-ai-postgres psql -U postgres career_ai_prod < backup.sql

# Execute SQL
docker exec career-ai-postgres psql -U postgres career_ai_prod -c "SELECT COUNT(*) FROM users;"

# View logs
docker-compose logs --tail=100
docker-compose logs -f backend
docker-compose logs backend --since 1h

# Scale services
docker-compose up -d --scale backend=3

# Remove old containers
docker system prune -a --volumes

# Health check endpoint
curl -v http://localhost:8000/health
```

---

## Escalation Procedures

**Level 1**: Team lead / On-call engineer
- Attempts standard troubleshooting
- Gathers logs and metrics
- Documents findings

**Level 2**: Senior engineer / DevOps
- Reviews Level 1 findings
- Performs deep investigation
- Implements fixes
- Reviews code changes

**Level 3**: Architect / CTO
- Post-incident review
- Design improvements
- Policy changes
- Business impact assessment

---

## On-Call Schedule

See: `/docs/on-call-schedule.md` (updated monthly)

**Escalation Contact**:
- Primary: $PRIMARY_ENGINEER
- Secondary: $SECONDARY_ENGINEER
- Manager: $ENGINEERING_MANAGER
