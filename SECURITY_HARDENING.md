# Security Hardening Guide - Career AI Platform

Production security hardening checklist and best practices.

## Table of Contents
1. [Network Security](#network-security)
2. [Application Security](#application-security)
3. [Database Security](#database-security)
4. [Secrets Management](#secrets-management)
5. [SSL/TLS Configuration](#ssltls-configuration)
6. [Access Control](#access-control)
7. [Security Scanning](#security-scanning)
8. [Incident Response](#incident-response)

---

## Network Security

### Firewall Rules

**Inbound Rules**:
```
SSH (22):     Restricted to admin IPs
HTTP (80):    Open (redirects to HTTPS)
HTTPS (443):  Open to internet
8000:         Closed (backend internal only)
5432:         Closed (database internal only)
6379:         Closed (Redis internal only)
```

**UFW Configuration** (Ubuntu):

```bash
# Enable UFW
sudo ufw enable

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (restrict IP if possible)
sudo ufw allow from ADMIN_IP to any port 22

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow monitoring (internal only)
sudo ufw allow from 10.0.0.0/8 to any port 9090

# Verify rules
sudo ufw status verbose
```

### Network Segmentation

**Docker Network Architecture**:

```yaml
networks:
  career-ai-network:
    driver: bridge
    ipam:
      config:
        - subnet: 10.0.9.0/24
  
  monitoring-network:
    driver: bridge
    ipam:
      config:
        - subnet: 10.0.10.0/24
```

**Service Connectivity**:
- Public: Nginx (port 443)
- Backend: Internal only (10.0.9.0/24)
- Database: Backend only (internal)
- Redis: Backend only (internal)
- Admin: VPN required

### DDoS Protection

**AWS WAF Configuration** (if using AWS):

```bash
# Install AWS WAF
aws wafv2 create-web-acl \
  --name CareerAI-WAF \
  --scope CLOUDFRONT \
  --default-action Block={} \
  --rules file://waf-rules.json

# Rate limiting
Rate: 2000 requests/5 minutes
Block: IPs exceeding limit for 15 minutes
```

**Nginx Rate Limiting** (already configured):

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/m;

limit_req zone=api_limit burst=20 nodelay;
limit_req zone=auth_limit burst=5 nodelay;
```

---

## Application Security

### Input Validation

**FastAPI Pydantic Validation**:

```python
# In app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    username: str = Field(pattern=r'^[a-zA-Z0-9_-]{3,50}$')
    
    @validator('password')
    def password_complexity(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        if not any(c in '!@#$%^&*' for c in v):
            raise ValueError('Password must contain special char')
        return v
```

### SQL Injection Prevention

**Use Parameterized Queries** (SQLAlchemy):

```python
# ✅ CORRECT - Parameterized
query = db.query(User).filter(User.email == user_email)

# ❌ WRONG - String interpolation
query = db.query(User).filter(f"email = '{user_email}'")
```

### XSS Prevention

**Frontend Content Sanitization**:

```typescript
// Use DOMPurify
import DOMPurify from 'dompurify';

const sanitized = DOMPurify.sanitize(userInput);
return <div>{sanitized}</div>;
```

**Backend Content Security Policy** (Nginx):

```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.example.com; style-src 'self' 'unsafe-inline';" always;
```

### CSRF Protection

**Backend CSRF Token** (FastAPI):

```python
from fastapi_csrf_protect import CsrfProtect

@app.post("/submit")
async def submit(csrf_protect: CsrfProtect = Depends()):
    await csrf_protect.validate_csrf(request)
    # Process form
```

### Authentication Security

**JWT Token Hardening**:

```python
# app/core/security.py
from datetime import timedelta

# Short-lived access tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 15

# Long-lived refresh tokens (stored securely)
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Generate tokens with proper claims
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt
```

**Password Security**:

```python
from passlib.context import CryptContext
from passlib.exc import InvalidHash

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Increase security
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

---

## Database Security

### PostgreSQL Security

**User Permissions**:

```sql
-- Create limited user for application
CREATE USER career_ai_app WITH PASSWORD 'strong_random_password';

-- Grant only necessary privileges
GRANT CONNECT ON DATABASE career_ai_prod TO career_ai_app;
GRANT USAGE ON SCHEMA public TO career_ai_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO career_ai_app;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO career_ai_app;

-- Prevent public schema usage
REVOKE ALL ON SCHEMA public FROM PUBLIC;
```

**Connection Security**:

```bash
# PostgreSQL configuration (postgresql.conf)
ssl = on
ssl_cert_file = '/etc/postgresql/server.crt'
ssl_key_file = '/etc/postgresql/server.key'
ssl_protocols = 'TLSv1.3'

# Require SSL for all connections
host    all    all    0.0.0.0/0    ssl
```

**Data at Rest Encryption**:

```bash
# Enable encryption in Docker Compose
postgres:
  command:
    - "-c"
    - "log_connections=on"
    - "-c"
    - "log_disconnections=on"
    - "-c"
    - "log_statement=all"
```

### Redis Security

**Redis Authentication**:

```bash
# Docker Compose
redis:
  command: redis-server --requirepass $REDIS_PASSWORD --appendonly yes
  
# Also set maxmemory and eviction policy
command: >
  redis-server 
  --requirepass $REDIS_PASSWORD 
  --maxmemory 512mb 
  --maxmemory-policy allkeys-lru
```

**Redis ACL** (Redis 6+):

```bash
# Inside Redis container
ACL SETUSER myapp on >strong_password ~* &* -@all +@read +@write

# Verify
ACL LIST
```

---

## Secrets Management

### Environment Variables

**Never commit secrets**:

```bash
# .gitignore
.env
.env.local
.env.production
.env.*.local
secrets/
*.pem
*.key
```

**Use AWS Secrets Manager**:

```python
# app/core/config.py
import boto3

client = boto3.client('secretsmanager', region_name='us-east-1')

response = client.get_secret_value(SecretId='career-ai/production')
secret = json.loads(response['SecretString'])

DATABASE_URL = secret['database_url']
JWT_SECRET = secret['jwt_secret']
```

### Rotating Secrets

```bash
#!/bin/bash
# rotate_secrets.sh

# Rotate JWT secret
NEW_JWT_SECRET=$(openssl rand -hex 32)

# Update in Secrets Manager
aws secretsmanager update-secret \
  --secret-id career-ai/production \
  --secret-string "{\"jwt_secret\": \"$NEW_JWT_SECRET\"}"

# Restart services to pick up new secret
docker-compose restart backend

# Notify team
echo "JWT secret rotated successfully"
```

### Key Rotation Schedule

- JWT Secrets: Quarterly
- Database passwords: Quarterly
- API keys: Annually
- SSL certificates: Annually

---

## SSL/TLS Configuration

### Certificate Generation (Let's Encrypt)

```bash
#!/bin/bash
# generate_certificates.sh

DOMAIN="yourdomain.com"

# Install certbot
apt-get install certbot python3-certbot-nginx

# Generate certificate
certbot certonly \
  --standalone \
  -d $DOMAIN \
  -d www.$DOMAIN \
  --email security@yourdomain.com \
  --agree-tos

# Copy to application
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ./ssl/
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ./ssl/

# Secure permissions
chmod 644 ./ssl/fullchain.pem
chmod 600 ./ssl/privkey.pem
```

### Nginx SSL Configuration

```nginx
# Already configured in nginx.conf
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!eNULL:!EXPORT:!DES:!MD5:!PSK:!RC4;
ssl_prefer_server_ciphers on;

# HSTS
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

# Security headers
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### Certificate Pinning

```python
# For critical APIs, implement certificate pinning
import httpx

verify = "/path/to/cert.pem"
async with httpx.AsyncClient(verify=verify) as client:
    response = await client.get("https://api.example.com/data")
```

---

## Access Control

### Role-Based Access Control (RBAC)

**In app/models/user.py**:

```python
class UserRole(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"

class User(Base):
    __tablename__ = "users"
    
    id: int
    role: UserRole = UserRole.USER
    is_active: bool = True
    is_verified: bool = False
```

**Permission Checking**:

```python
# app/core/dependencies.py
async def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin_user: User = Depends(require_admin)
):
    # Delete user logic
    pass
```

### API Key Management

```python
# Generate secure API keys
def generate_api_key():
    return secrets.token_urlsafe(32)

# Hash and store
hashed_key = hashlib.sha256(api_key.encode()).hexdigest()

# Verify on use
provided_key_hash = hashlib.sha256(provided_key.encode()).hexdigest()
if provided_key_hash != stored_hash:
    raise HTTPException(status_code=401, detail="Invalid API key")
```

### Audit Logging

```python
# app/models/admin.py
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id: int
    user_id: int
    action: str
    resource_type: str
    resource_id: int
    changes: dict
    ip_address: str
    user_agent: str
    timestamp: datetime
    status: str  # "success" or "failure"

# Log all sensitive actions
def log_action(user: User, action: str, resource_type: str, resource_id: int):
    log_entry = AuditLog(
        user_id=user.id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        timestamp=datetime.utcnow()
    )
    db.add(log_entry)
    db.commit()
```

---

## Security Scanning

### SAST (Static Application Security Testing)

```bash
# Install Bandit for Python
pip install bandit

# Scan backend code
bandit -r backend/app -f json -o bandit_report.json

# Install ESLint security plugins
npm install --save-dev eslint-plugin-security

# Scan frontend code
npx eslint src --plugin security
```

### DAST (Dynamic Application Security Testing)

```bash
# Install OWASP ZAP
docker run -v $(pwd):/zap/wrk:rw -t owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:8000/openapi.json \
  -r zap_report.html
```

### Dependency Scanning

```bash
# Backend dependency scan
safety check --json > safety_report.json

# Frontend dependency scan
npm audit --json > npm_audit.json

# Update vulnerable packages
pip install --upgrade pip setuptools wheel
npm update
```

### Container Scanning

```bash
# Scan Docker images with Trivy
trivy image career-ai-backend:latest
trivy image career-ai-frontend:latest

# Scan with Grype
grype career-ai-backend:latest
```

---

## Incident Response

### Security Incident Checklist

**Upon Detection**:
1. Isolate affected system
2. Preserve logs and evidence
3. Notify security team
4. Begin incident investigation
5. Document timeline

```bash
#!/bin/bash
# incident_response.sh

INCIDENT_ID=$(date +%s)
INCIDENT_DIR="/var/log/incidents/$INCIDENT_ID"

mkdir -p $INCIDENT_DIR

# Collect evidence
docker logs career-ai-backend > $INCIDENT_DIR/backend.log
docker logs career-ai-frontend > $INCIDENT_DIR/frontend.log

# Database audit logs
docker exec career-ai-postgres pg_dump -U postgres -a > $INCIDENT_DIR/db_dump.sql

# Network logs (if available)
journalctl -n 10000 > $INCIDENT_DIR/system.log

# Preserve filesystem
tar -czf $INCIDENT_DIR/filesystem_snapshot.tar.gz /opt/career-ai-platform

echo "Evidence collected in $INCIDENT_DIR"
```

### Breach Notification

```bash
#!/bin/bash
# breach_notification.sh

# 1. Notify security team
curl -X POST $SLACK_WEBHOOK \
  -d "🚨 SECURITY INCIDENT - Breach detected. Isolating system."

# 2. Disable affected accounts
# ... account disabling logic ...

# 3. Revoke tokens
redis-cli FLUSHALL

# 4. Notify users (if data exposed)
# ... mass notification logic ...

# 5. File report
# ... compliance reporting ...
```

---

## Security Checklist

**Pre-Production**:
- [ ] All secrets in Secrets Manager
- [ ] No hardcoded credentials
- [ ] HTTPS enabled
- [ ] CSRF protection enabled
- [ ] Rate limiting configured
- [ ] CORS properly restricted
- [ ] Authentication implemented
- [ ] Authorization enforced
- [ ] Input validation enabled
- [ ] SQL injection prevention verified
- [ ] XSS prevention enabled
- [ ] Security headers configured
- [ ] Audit logging enabled
- [ ] Error logging enabled
- [ ] Database encryption enabled
- [ ] Network segmented
- [ ] Firewall rules applied

**Ongoing**:
- [ ] Security scans weekly
- [ ] Dependency updates monthly
- [ ] Certificate validity monthly
- [ ] Access reviews quarterly
- [ ] Security training annually
- [ ] Incident response drills quarterly
- [ ] Penetration testing annually

---

## Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [AWS Security Best Practices](https://aws.amazon.com/architecture/security-identity-compliance/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

---

## Emergency Security Contact

- Security Team: security@yourdomain.com
- On-Call: +1-XXX-XXX-XXXX
- Slack: #security-incidents
