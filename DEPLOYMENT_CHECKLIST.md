# Production Deployment Checklist - Career AI Platform

Complete checklist for deploying the Career AI Platform to production.

---

## Pre-Deployment (1-2 weeks before)

### Infrastructure Planning
- [ ] Determine cloud provider (AWS, GCP, Azure, etc.)
- [ ] Choose region(s) for deployment
- [ ] Plan disaster recovery strategy
- [ ] Estimate monthly costs
- [ ] Allocate budget
- [ ] Document infrastructure diagram

### Team Preparation
- [ ] Assign deployment lead
- [ ] Assign on-call engineer
- [ ] Assign backup on-call
- [ ] Schedule deployment window
- [ ] Notify stakeholders of deployment date
- [ ] Conduct training on operational procedures
- [ ] Review incident response procedures
- [ ] Set up communication channels (Slack, PagerDuty)

### Security Audit
- [ ] Run SAST (Bandit, ESLint security)
- [ ] Run dependency scan (Safety, npm audit)
- [ ] Review secrets management (AWS Secrets Manager)
- [ ] Verify SSL certificate setup
- [ ] Check firewall rules
- [ ] Verify no hardcoded credentials
- [ ] Review database user permissions
- [ ] Verify encryption at rest and in transit

---

## 1-2 Days Before Deployment

### Environment Setup

#### AWS Infrastructure
- [ ] Create VPC with subnets
- [ ] Set up security groups (SSH, HTTP, HTTPS, internal ports)
- [ ] Create EC2 instances:
  - [ ] Backend instance (t3.medium or larger)
  - [ ] Frontend instance (t3.small or larger)
  - [ ] Backup instance (optional)
- [ ] Configure RDS PostgreSQL database
  - [ ] Engine: PostgreSQL 15
  - [ ] Instance: db.t3.small or larger
  - [ ] Multi-AZ enabled: Yes
  - [ ] Backup retention: 30 days
  - [ ] Encryption: Enabled
- [ ] Configure ElastiCache Redis
  - [ ] Node type: cache.t3.small or larger
  - [ ] Automatic failover: Enabled
  - [ ] Encryption at rest: Enabled
  - [ ] Encryption in transit: Enabled
- [ ] Create S3 buckets:
  - [ ] Application backups
  - [ ] Database backups
  - [ ] User uploads
  - [ ] Static assets (optional)
- [ ] Configure Route 53 DNS
  - [ ] Create hosted zone
  - [ ] Set up A records for domains
  - [ ] Set up CNAME records if needed
  - [ ] Enable health checks
- [ ] Set up CloudWatch alarms for:
  - [ ] High CPU usage
  - [ ] High memory usage
  - [ ] High disk usage
  - [ ] Failed health checks
  - [ ] Database connection issues

#### GitHub Configuration
- [ ] Create repository (if private)
- [ ] Create deployment branches:
  - [ ] main (production)
  - [ ] staging (staging)
- [ ] Set up branch protection rules
- [ ] Create GitHub secrets:
  - [ ] PRODUCTION_SERVER_HOST
  - [ ] PRODUCTION_SERVER_USER
  - [ ] PRODUCTION_SERVER_SSH_KEY
  - [ ] STAGING_SERVER_HOST
  - [ ] STAGING_SERVER_USER
  - [ ] STAGING_SERVER_SSH_KEY
  - [ ] SLACK_WEBHOOK (for notifications)
- [ ] Test GitHub Actions workflows

### Certificate Generation
- [ ] Generate SSL certificate (Let's Encrypt)
- [ ] Verify certificate validity
- [ ] Set certificate auto-renewal
- [ ] Add certificate to Secrets Manager
- [ ] Test HTTPS on staging

### Secrets Management
- [ ] Create AWS Secrets Manager secret with all environment variables
- [ ] Verify secret format matches `.env.production`
- [ ] Test secret retrieval
- [ ] Document secret update procedure
- [ ] Set up rotation schedule (quarterly)

### Configuration Files
- [ ] Copy `.env.production` template
- [ ] Update all placeholders:
  - [ ] Database credentials
  - [ ] JWT secret
  - [ ] API keys (OpenAI, SendGrid, etc.)
  - [ ] Domain names
  - [ ] Redis credentials
  - [ ] AWS credentials
- [ ] Verify `.env.production` is NOT committed to git
- [ ] Store final `.env.production` in Secrets Manager

### Docker Images
- [ ] Build backend Docker image
- [ ] Build frontend Docker image
- [ ] Tag images with version numbers
- [ ] Push to Docker registry (Docker Hub, ECR, etc.)
- [ ] Verify images pull correctly
- [ ] Test images in staging environment

---

## Day Before Deployment

### Final Testing
- [ ] Run full test suite
- [ ] Run security scans
- [ ] Run load tests
- [ ] Test backup and restore procedures
- [ ] Test failover procedures
- [ ] Verify all API endpoints in staging
- [ ] Verify frontend functionality in staging
- [ ] Test authentication flow
- [ ] Test file uploads
- [ ] Test email notifications
- [ ] Test monitoring and alerting

### Database Preparation
- [ ] Create database user for application
- [ ] Grant appropriate permissions
- [ ] Run migrations on staging database
- [ ] Verify migrations successful
- [ ] Create initial admin user (staging)
- [ ] Test backup restore (staging)

### Monitoring Setup
- [ ] Create Prometheus scrape configs
- [ ] Create Grafana dashboards
- [ ] Configure AlertManager rules
- [ ] Test alert notifications
- [ ] Create Sentry project
- [ ] Configure Sentry DSN
- [ ] Test error tracking (staging)

### Documentation Review
- [ ] Review DEPLOYMENT_GUIDE.md
- [ ] Review OPERATIONAL_RUNBOOKS.md
- [ ] Review MONITORING_GUIDE.md
- [ ] Print runbooks for on-call team
- [ ] Update internal wiki/documentation
- [ ] Notify all team members of documentation updates

### Backup Verification
- [ ] Verify backups are being created
- [ ] Verify backup integrity
- [ ] Test restore from backup (staging)
- [ ] Document restore time (RTO)
- [ ] Document data loss window (RPO)
- [ ] Verify S3 bucket encryption

### Communication
- [ ] Send deployment announcement to team
- [ ] Send deployment announcement to users (if needed)
- [ ] Verify Slack channel access
- [ ] Verify PagerDuty setup
- [ ] Verify email notifications working
- [ ] Test communication channels

---

## Deployment Day - Before Launch

### Morning Checklist (2 hours before)
- [ ] Team present and ready
- [ ] Communication channels open (Slack, PagerDuty)
- [ ] Monitoring dashboards displayed
- [ ] Incident response runbook printed
- [ ] Database backup verified
- [ ] Server connectivity tested (SSH)
- [ ] All team members briefed
- [ ] Rollback plan reviewed

### 1 Hour Before Launch
- [ ] Freeze code changes
- [ ] Take final database backup
- [ ] Verify staging environment is clean
- [ ] Clear caches
- [ ] Verify all third-party services available (AWS, SendGrid, OpenAI, etc.)
- [ ] Start monitoring for baseline metrics

### 30 Minutes Before Launch
- [ ] Final health check of all systems
- [ ] Re-verify all credentials
- [ ] Re-verify DNS records
- [ ] Final review of deployment commands
- [ ] Team ready for incident response
- [ ] PagerDuty on-call activated

---

## Deployment Execution

### Phase 1: Backend Deployment (t=0 min)
- [ ] SSH into backend server
- [ ] Pull latest code: `git pull origin main`
- [ ] Pull latest Docker images: `docker-compose pull`
- [ ] Run database migrations: `docker-compose run --rm backend alembic upgrade head`
- [ ] Restart backend service: `docker-compose restart backend`
- [ ] Wait 30 seconds for service startup
- [ ] Verify backend health: `curl http://localhost:8000/health`
- [ ] Monitor logs: `docker-compose logs -f backend`
- [ ] Alert: If health check fails, STOP and investigate

### Phase 2: Frontend Deployment (t=5 min)
- [ ] Verify backend is healthy
- [ ] Restart frontend service: `docker-compose restart frontend`
- [ ] Wait 30 seconds for service startup
- [ ] Verify frontend loads: `curl http://localhost:3000`
- [ ] Monitor logs: `docker-compose logs -f frontend`
- [ ] Alert: If frontend fails, STOP and investigate

### Phase 3: Reverse Proxy Update (t=10 min)
- [ ] Reload Nginx: `docker exec career-ai-nginx nginx -s reload`
- [ ] Verify Nginx status: `docker exec career-ai-nginx nginx -t`
- [ ] Test HTTPS: `curl -I https://yourdomain.com`
- [ ] Alert: If Nginx fails, STOP and investigate

### Phase 4: Verify All Services (t=15 min)
- [ ] Check all containers running: `docker-compose ps`
- [ ] Verify database connectivity: `curl http://localhost:8000/health`
- [ ] Verify Redis connectivity: `docker exec career-ai-redis redis-cli ping`
- [ ] Check logs for errors: `docker-compose logs`

---

## Post-Deployment - First 1 Hour

### Immediate Verification (t=0-15 min)
- [ ] Monitor all services
- [ ] Check for error spikes in logs
- [ ] Verify metrics are being collected
- [ ] Verify alerts are functioning
- [ ] Monitor CPU/memory usage
- [ ] Monitor network traffic
- [ ] Check API response times
- [ ] Verify no critical errors in Sentry

### Health Check Battery (t=15-30 min)
- [ ] Login with test user
- [ ] Search for jobs
- [ ] Upload a test resume
- [ ] Generate a test cover letter
- [ ] Create a test application
- [ ] Test interview coach
- [ ] Verify notifications
- [ ] Check analytics dashboard
- [ ] Verify admin panel

### External Service Verification (t=30-45 min)
- [ ] Test email notifications
- [ ] Verify SendGrid logs
- [ ] Test OpenAI integration
- [ ] Check API call logs
- [ ] Verify file uploads to S3
- [ ] Test backup process

### Performance Baseline (t=45-60 min)
- [ ] Record baseline metrics
- [ ] Document response times
- [ ] Document error rates
- [ ] Document resource utilization
- [ ] Take screenshot of monitoring dashboard
- [ ] Save initial state for comparison

### Team Communication
- [ ] Post initial success message to Slack
- [ ] Notify stakeholders of deployment success
- [ ] Thank team for effort
- [ ] Set schedule for continued monitoring

---

## Post-Deployment - First 24 Hours

### Continuous Monitoring
- [ ] Monitor every 30 minutes:
  - [ ] Error rates
  - [ ] Response times
  - [ ] Resource utilization
  - [ ] Database connections
  - [ ] Cache hit rates
- [ ] Watch for memory leaks
- [ ] Watch for connection pool exhaustion
- [ ] Watch for database slow queries
- [ ] Monitor backup completion

### Load Monitoring
- [ ] Monitor active user count
- [ ] Monitor API request rate
- [ ] Monitor database query rate
- [ ] Watch for any anomalies
- [ ] Verify no capacity issues

### Test Coverage
- [ ] Run smoke tests hourly
- [ ] Test critical user flows
- [ ] Monitor error tracking (Sentry)
- [ ] Check for new error patterns

### Documentation Updates
- [ ] Update deployment log
- [ ] Document any issues encountered
- [ ] Document resolutions
- [ ] Update runbooks if needed

### Stakeholder Communication
- [ ] Daily status updates
- [ ] Hour 2: "System stable"
- [ ] Hour 6: "All systems nominal"
- [ ] Hour 12: "24-hour stability goal close"
- [ ] Hour 24: "Deployment successful, monitoring continues"

---

## Post-Deployment - First Week

### Daily Tasks
- [ ] Review logs for errors
- [ ] Check metrics for anomalies
- [ ] Verify backups completed
- [ ] Verify no security alerts
- [ ] Monitor user feedback
- [ ] Check error tracking

### End of Week Review
- [ ] Compile deployment report
- [ ] Document lessons learned
- [ ] Identify improvements
- [ ] Update procedures
- [ ] Plan for next deployment

### Performance Analysis
- [ ] Analyze full week metrics
- [ ] Compare to baselines
- [ ] Identify bottlenecks
- [ ] Plan optimizations

### Security Review
- [ ] Review access logs
- [ ] Check for suspicious activity
- [ ] Verify firewall rules effective
- [ ] Review audit logs

### Team Retrospective
- [ ] Schedule post-deployment retrospective
- [ ] Discuss what went well
- [ ] Discuss what could improve
- [ ] Document action items
- [ ] Update playbooks

---

## Post-Deployment - First Month

### Stabilization
- [ ] Monitor for late-appearing issues
- [ ] Fix any discovered bugs
- [ ] Optimize performance based on real usage
- [ ] Scale if needed
- [ ] Refine alerting thresholds

### User Feedback
- [ ] Collect user feedback
- [ ] Address any issues
- [ ] Monitor support tickets
- [ ] Improve based on feedback

### Documentation
- [ ] Update documentation with real-world findings
- [ ] Create operational guides based on actual usage
- [ ] Train additional ops team members
- [ ] Update incident runbooks

### Cost Optimization
- [ ] Analyze AWS billing
- [ ] Identify cost optimization opportunities
- [ ] Right-size resources
- [ ] Cancel unused services

### Scaling Preparation
- [ ] Monitor growth metrics
- [ ] Plan for next scaling event
- [ ] Stress test at 2x current load
- [ ] Prepare scaling procedures

---

## Rollback Procedures

### If Critical Issues Occur During Deployment

**Step 1: Immediate Response** (first 5 minutes)
- [ ] Declare incident
- [ ] Notify all team members
- [ ] Alert stakeholders
- [ ] Freeze all changes

**Step 2: Assessment** (next 5 minutes)
- [ ] Assess severity (critical, high, medium, low)
- [ ] Determine if rollback needed
- [ ] Check time to fix vs time to rollback

**Step 3: Rollback Decision**
- If < 10 minute fix: Attempt fix
- If > 10 minute fix: Proceed with rollback

**Step 4: Execute Rollback**
```bash
cd /opt/career-ai-platform

# Rollback to previous version
git reset --hard HEAD~1

# Restore previous database backup
docker exec career-ai-postgres psql -U postgres career_ai_prod < backup_previous.sql

# Restart services
docker-compose down
docker-compose up -d

# Verify rollback
curl http://localhost:8000/health
```

**Step 5: Verify Rollback**
- [ ] All services running
- [ ] Health checks passing
- [ ] User traffic restored
- [ ] No errors in logs

**Step 6: Post-Rollback**
- [ ] Notify stakeholders
- [ ] Document cause
- [ ] Plan investigation
- [ ] Schedule next deployment

---

## Troubleshooting During Deployment

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Verify environment variables
docker exec career-ai-backend env | grep DATABASE_URL

# Check database connectivity
docker exec career-ai-backend curl http://postgres:5432

# Restart with fresh state
docker-compose restart backend
```

### Database migrations fail
```bash
# Check migration status
docker exec career-ai-postgres psql -U postgres career_ai_prod -c "SELECT version FROM alembic_version;"

# Rollback migration
docker-compose run --rm backend alembic downgrade -1

# Re-run migrations
docker-compose run --rm backend alembic upgrade head
```

### Frontend not responding
```bash
# Check logs
docker-compose logs frontend

# Check if port is listening
docker exec career-ai-frontend netstat -tuln | grep 3000

# Rebuild frontend
docker-compose up -d --build frontend
```

### Nginx can't connect to backend
```bash
# Check Nginx config
docker exec career-ai-nginx nginx -t

# Check upstream configuration
docker exec career-ai-nginx curl -v http://backend:8000

# Check network connectivity
docker exec career-ai-nginx ping backend
```

---

## Success Criteria

✅ **Deployment is successful when**:
- All services are running
- Health checks passing
- No errors in logs
- API endpoints responding
- Frontend loading
- Database connected
- Backups working
- Monitoring active
- Alerts configured
- Users can access platform
- No memory leaks detected (24 hours)
- Performance acceptable
- Error rate < 0.1%
- Response times within SLA

---

## Contact & Escalation

**During Deployment**:
- Primary Contact: [Name/Phone]
- Secondary Contact: [Name/Phone]
- Slack Channel: #deployment
- PagerDuty: [Link]

**If Critical Issue**:
1. Contact primary
2. If no response in 5 min, contact secondary
3. If no response in 10 min, escalate to manager
4. Page on-call engineer

---

## Sign-Off

**Deployment Lead**: _________________ Date: _______

**On-Call Engineer**: _________________ Date: _______

**Engineering Manager**: _________________ Date: _______

---

**Notes**: ____________________________________________________________________________

________________________________________________________________________

________________________________________________________________________

