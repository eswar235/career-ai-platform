# Monitoring & Observability Guide - Career AI Platform

## Overview

This guide covers setting up comprehensive monitoring, logging, and observability for the Career AI Platform in production environments.

## Table of Contents
1. [Logging Architecture](#logging-architecture)
2. [Metrics Collection](#metrics-collection)
3. [Distributed Tracing](#distributed-tracing)
4. [Error Tracking](#error-tracking)
5. [Performance Monitoring](#performance-monitoring)
6. [Health Checks](#health-checks)
7. [Alerting & Notifications](#alerting--notifications)
8. [Log Aggregation](#log-aggregation)
9. [Dashboards](#dashboards)
10. [Troubleshooting](#troubleshooting)

---

## Logging Architecture

### Application Logging

**Backend (FastAPI)**

The backend uses structured JSON logging via `python-json-logger`:

```python
# In app/core/logging.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
```

**Log Levels**:
- `DEBUG`: Development and troubleshooting (not in production)
- `INFO`: General information about application flow
- `WARNING`: Warning conditions
- `ERROR`: Error conditions
- `CRITICAL`: System is unusable

**Log Output Format**:
```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "logger": "app.services.job_service",
  "message": "Job search completed",
  "request_id": "req-12345",
  "user_id": "usr-789",
  "duration_ms": 1234,
  "results_count": 42
}
```

### Log Collection

**Docker Logging**:

All containers send logs to JSON-file driver:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

**Log Rotation**:
- Max file size: 10MB
- Max files: 3
- Automatic rotation and compression

**Access logs for Nginx**:

```nginx
# Access logs
access_log /var/log/nginx/access.log main buffer=32k flush=1s;

# Error logs
error_log /var/log/nginx/error.log warn;
```

---

## Metrics Collection

### Prometheus Setup

**Docker Compose addition** (optional):

```yaml
prometheus:
  image: prom/prometheus:latest
  container_name: career-ai-prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
    - ./alert.rules.yml:/etc/prometheus/alert.rules.yml:ro
    - prometheus_data:/prometheus
  ports:
    - "9090:9090"
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
    - '--storage.tsdb.retention.time=30d'
  networks:
    - career-ai-network
  restart: unless-stopped
```

**prometheus.yml** configuration:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'career-ai-production'

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - 'alertmanager:9093'

rule_files:
  - 'alert.rules.yml'

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:9113']
```

### Backend Metrics Endpoint

Add Prometheus metrics to FastAPI:

```python
# In requirements.txt
prometheus-client==0.19.0

# In app/main.py
from prometheus_client import Counter, Histogram, Gauge
from prometheus_client import make_asgi_app

# Create metrics
request_count = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('request_duration_seconds', 'Request duration', ['method', 'endpoint'])
active_users = Gauge('active_users', 'Number of active users')

# Mount metrics endpoint
app.mount("/metrics", make_asgi_app())
```

### Key Metrics to Monitor

**Backend Performance**:
- Request latency (p50, p95, p99)
- Request rate (requests/second)
- Error rate (errors/total requests)
- Active connections
- Database query duration
- API endpoint response times

**Database**:
- Query duration
- Connection count
- Lock waits
- Cache hit ratio
- Table sizes
- Transaction throughput

**System**:
- CPU usage
- Memory usage
- Disk I/O
- Network bandwidth
- Container uptime
- Restart count

---

## Distributed Tracing

### Jaeger Setup

**Docker Compose addition** (optional):

```yaml
jaeger:
  image: jaegertracing/all-in-one:latest
  container_name: career-ai-jaeger
  ports:
    - "6831:6831/udp"
    - "16686:16686"
  networks:
    - career-ai-network
  restart: unless-stopped
  environment:
    COLLECTOR_ZIPKIN_HTTP_PORT: "9411"
```

**Backend Integration**:

```python
# In requirements.txt
jaeger-client==4.8.0

# In app/core/tracing.py
from jaeger_client import Config

def init_tracer(service_name):
    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
        },
        service_name=service_name,
        validate=True,
    )
    return config.initialize_tracer()

# In app/main.py
tracer = init_tracer('career-ai-backend')
```

---

## Error Tracking

### Sentry Integration

**Backend Configuration**:

```python
# In requirements.txt
sentry-sdk==1.39.2

# In app/core/config.py
import sentry_sdk

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=0.1,
        integrations=[
            sentry_sdk.integrations.fastapi.FastApiIntegration(),
            sentry_sdk.integrations.sqlalchemy.SqlalchemyIntegration(),
        ],
    )
```

**Frontend Configuration**:

```typescript
// In frontend/.env.production
NEXT_PUBLIC_SENTRY_DSN=https://your-sentry-dsn

// In frontend/sentry.client.config.ts
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT,
  tracesSampleRate: 0.1,
});
```

---

## Performance Monitoring

### Database Query Monitoring

**Enable Query Logging**:

```python
# In app/core/database.py
from sqlalchemy import event

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total_time = time.time() - conn.info['query_start_time'].pop(-1)
    if total_time > 1.0:  # Log slow queries > 1 second
        logger.warning(f"Slow query ({total_time:.2f}s): {statement}")
```

### API Endpoint Performance

Monitor via middleware:

```python
# In app/core/middleware.py
import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log slow endpoints
    if process_time > 2.0:
        logger.warning(f"Slow endpoint {request.url.path} took {process_time:.2f}s")
    
    return response
```

---

## Health Checks

### Backend Health Check

**Endpoint**: `GET /health`

```python
@app.get("/health", tags=["System"])
async def health_check(db: Session = Depends(get_db)):
    try:
        # Check database connectivity
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    try:
        # Check Redis connectivity
        redis_client.ping()
        redis_status = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        redis_status = "unhealthy"
    
    overall_status = "healthy" if all([db_status == "healthy", redis_status == "healthy"]) else "unhealthy"
    
    return {
        "status": overall_status,
        "database": db_status,
        "redis": redis_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    }
```

### Frontend Health Check

```typescript
// In frontend/lib/health.ts
export async function checkHealth(): Promise<HealthStatus> {
  try {
    const response = await fetch(`${API_URL}/health`, {
      timeout: 5000
    });
    
    return {
      status: response.ok ? 'healthy' : 'unhealthy',
      statusCode: response.status,
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    return {
      status: 'unhealthy',
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
}
```

### Kubernetes Probes

For Kubernetes deployment:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2
```

---

## Alerting & Notifications

### Alert Rules (alert.rules.yml)

```yaml
groups:
  - name: career_ai
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: rate(requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/sec"

      # High latency
      - alert: HighLatency
        expr: histogram_quantile(0.95, request_duration_seconds) > 2
        for: 5m
        annotations:
          summary: "High API latency"
          description: "p95 latency is {{ $value }}s"

      # Database connection exhaustion
      - alert: DatabaseConnectionExhaustion
        expr: pg_stat_activity_count > 90
        for: 5m
        annotations:
          summary: "Database connection limit approaching"
          description: "{{ $value }}/100 connections in use"

      # Disk space low
      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.1
        for: 10m
        annotations:
          summary: "Disk space running low"
          description: "{{ $value | humanizePercentage }} disk space available"

      # Memory pressure
      - alert: HighMemoryUsage
        expr: (container_memory_usage_bytes / container_spec_memory_limit_bytes) > 0.85
        for: 5m
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value | humanizePercentage }}"

      # Service down
      - alert: ServiceDown
        expr: up == 0
        for: 2m
        annotations:
          summary: "Service is down"
          description: "{{ $labels.job }} has been down for more than 2 minutes"
```

### Slack Notifications

Configure AlertManager for Slack:

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m

route:
  receiver: 'slack'
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h

receivers:
  - name: 'slack'
    slack_configs:
      - api_url: $SLACK_WEBHOOK_URL
        channel: '#alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
        send_resolved: true
```

---

## Log Aggregation

### ELK Stack (Elasticsearch, Logstash, Kibana)

**Docker Compose addition**:

```yaml
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
  container_name: career-ai-elasticsearch
  environment:
    discovery.type: single-node
    xpack.security.enabled: "false"
  volumes:
    - elasticsearch_data:/usr/share/elasticsearch/data
  ports:
    - "9200:9200"
  networks:
    - career-ai-network
  restart: unless-stopped

logstash:
  image: docker.elastic.co/logstash/logstash:8.11.0
  container_name: career-ai-logstash
  volumes:
    - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf:ro
  environment:
    LS_JAVA_OPTS: "-Xmx256m -Xms256m"
  depends_on:
    - elasticsearch
  networks:
    - career-ai-network
  restart: unless-stopped

kibana:
  image: docker.elastic.co/kibana/kibana:8.11.0
  container_name: career-ai-kibana
  ports:
    - "5601:5601"
  environment:
    ELASTICSEARCH_HOSTS: http://elasticsearch:9200
  depends_on:
    - elasticsearch
  networks:
    - career-ai-network
  restart: unless-stopped
```

**Logstash Configuration** (logstash.conf):

```
input {
  tcp {
    port => 5000
    codec => json
  }
}

filter {
  # Add any filters here
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "career-ai-%{+YYYY.MM.dd}"
  }
}
```

### Grafana Dashboards

**Create Dashboard**:

1. Navigate to Grafana: `http://localhost:3001`
2. Add Prometheus data source
3. Create dashboard with panels for:
   - Request rate
   - Error rate
   - Response time
   - Database connections
   - Memory usage
   - CPU usage

**Example dashboard JSON** available in `grafana/dashboard.json`

---

## Troubleshooting

### Debug Checklist

```bash
# Check container logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Check container status
docker ps
docker-compose ps

# Check network connectivity
docker exec career-ai-backend ping postgres
docker exec career-ai-backend curl http://redis:6379

# Database health
docker exec career-ai-postgres psql -U postgres -c "SELECT version();"

# Redis health
docker exec career-ai-redis redis-cli ping

# Backend health endpoint
curl http://localhost:8000/health

# Check metrics
curl http://localhost:8000/metrics

# Monitor real-time logs
docker-compose logs -f --tail=100
```

### Common Issues

**Issue**: High memory usage
- Solution: Check for memory leaks, optimize queries, increase container memory limit

**Issue**: Database connection pool exhaustion
- Solution: Increase max_connections, reduce connection timeout, optimize connection usage

**Issue**: API latency degradation
- Solution: Check database query performance, enable caching, scale horizontally

**Issue**: Disk space warning
- Solution: Clean old logs, archive old data, increase disk size

---

## Best Practices

1. **Log Aggregation**: Centralize all logs for easier searching and debugging
2. **Metric Retention**: Keep metrics for at least 30 days for trend analysis
3. **Alert Fatigue**: Tune alert thresholds to reduce false positives
4. **Documentation**: Keep runbooks and troubleshooting guides updated
5. **Testing**: Regularly test alerting and notification systems
6. **Capacity Planning**: Monitor trends and plan for growth
7. **Security**: Secure access to monitoring dashboards and logs
8. **Retention Policies**: Define data retention policies for compliance

---

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Sentry Documentation](https://docs.sentry.io/)
- [ELK Stack Documentation](https://www.elastic.co/guide/index.html)
