# Backup & Recovery Procedures - Career AI Platform

Comprehensive backup and disaster recovery procedures for production data and configurations.

## Table of Contents
1. [Backup Strategy](#backup-strategy)
2. [Automated Backups](#automated-backups)
3. [Manual Backups](#manual-backups)
4. [Backup Verification](#backup-verification)
5. [Recovery Procedures](#recovery-procedures)
6. [Disaster Recovery Plan](#disaster-recovery-plan)
7. [Compliance & Retention](#compliance--retention)

---

## Backup Strategy

### RPO & RTO Targets

**Recovery Point Objective (RPO)**: 1 hour
- Database backups: Every 1 hour
- Application state: Every 4 hours
- Configuration: On-change + Daily

**Recovery Time Objective (RTO)**: 4 hours
- Database restore: < 1 hour
- Application deployment: < 30 minutes
- DNS failover: < 5 minutes

### Backup Components

**Critical Data**:
- PostgreSQL database (daily + hourly)
- Redis cache (daily)
- User uploads (daily)
- Configuration files (on-change)
- SSL certificates (on-change)

**Non-Critical**:
- Docker images (can be rebuilt)
- Node modules (can be reinstalled)
- Build artifacts (can be regenerated)

### Backup Locations

**Primary**: AWS S3
- Durability: 99.999999999%
- Replication: Cross-region
- Versioning: Enabled

**Secondary**: On-premise Storage
- Local backup volume
- 30-day retention
- Weekly offsite sync

---

## Automated Backups

### Database Backup Script

**File**: `scripts/backup_database.sh`

```bash
#!/bin/bash
set -e

# Configuration
BACKUP_DIR="/var/lib/career-ai/backups"
DB_USER="postgres"
DB_NAME="career_ai_prod"
DB_HOST="postgres"
S3_BUCKET="s3://career-ai-prod-backups"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Generate backup filename
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz"

# Create backup
echo "Starting database backup..."
docker exec career-ai-postgres pg_dump \
  -U $DB_USER \
  -h $DB_HOST \
  $DB_NAME | gzip > $BACKUP_FILE

# Get file size
SIZE=$(du -h $BACKUP_FILE | cut -f1)
echo "Database backup completed: $SIZE"

# Upload to S3
echo "Uploading to S3..."
aws s3 cp $BACKUP_FILE $S3_BUCKET/ \
  --storage-class STANDARD_IA \
  --metadata "timestamp=$TIMESTAMP,size=$SIZE,version=v1"

# Local retention
echo "Cleaning up old local backups..."
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Verify backup integrity
echo "Verifying backup integrity..."
gunzip -t $BACKUP_FILE

# Send notification
STATUS="✅ Database backup successful"
SIZE_MB=$(($(stat -f%z $BACKUP_FILE 2>/dev/null || stat -c%s $BACKUP_FILE) / 1024 / 1024))

curl -X POST $SLACK_WEBHOOK \
  -H 'Content-Type: application/json' \
  -d "{\"text\": \"$STATUS\nSize: ${SIZE_MB}MB\nTimestamp: $TIMESTAMP\"}"

echo "Backup process completed successfully"
```

### Volume Backup Script

**File**: `scripts/backup_volumes.sh`

```bash
#!/bin/bash
set -e

# Configuration
BACKUP_DIR="/var/lib/career-ai/backups"
S3_BUCKET="s3://career-ai-prod-backups"
RETENTION_DAYS=7

mkdir -p $BACKUP_DIR

# Backup PostgreSQL volume
echo "Backing up PostgreSQL volume..."
docker run --rm \
  -v career-ai-postgres:/data \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/postgres_volume_$(date +%Y%m%d_%H%M%S).tar.gz /data

# Backup Redis volume
echo "Backing up Redis volume..."
docker run --rm \
  -v career-ai-redis:/data \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/redis_volume_$(date +%Y%m%d_%H%M%S).tar.gz /data

# Backup user uploads
echo "Backing up user uploads..."
docker run --rm \
  -v career-ai-uploads:/data \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/uploads_$(date +%Y%m%d_%H%M%S).tar.gz /data

# Upload to S3
echo "Uploading volume backups to S3..."
aws s3 sync $BACKUP_DIR $S3_BUCKET/volumes/ \
  --storage-class GLACIER \
  --delete

# Cleanup old backups
echo "Cleaning up old backups..."
find $BACKUP_DIR -type f -mtime +$RETENTION_DAYS -delete

echo "Volume backup completed"
```

### Configuration Backup Script

**File**: `scripts/backup_config.sh`

```bash
#!/bin/bash
set -e

# Configuration
BACKUP_DIR="/var/lib/career-ai/backups"
S3_BUCKET="s3://career-ai-prod-backups"

mkdir -p $BACKUP_DIR

# Backup configuration files
echo "Backing up configuration files..."
tar -czf $BACKUP_DIR/config_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  /opt/career-ai-platform/docker-compose.prod.yml \
  /opt/career-ai-platform/nginx.conf \
  /opt/career-ai-platform/.env.production \
  /opt/career-ai-platform/.github/workflows/ \
  /etc/letsencrypt/live/yourdomain.com/ 2>/dev/null || true

# Upload to S3
echo "Uploading configuration backup to S3..."
aws s3 sync $BACKUP_DIR/config_backup_*.tar.gz $S3_BUCKET/config/ \
  --storage-class STANDARD

echo "Configuration backup completed"
```

### Cron Job Setup

**File**: `/etc/cron.d/career-ai-backups`

```cron
# Hourly database backup
0 * * * * root /usr/local/bin/backup_database.sh >> /var/log/career-ai-backup.log 2>&1

# Daily volume backup (2 AM)
0 2 * * * root /usr/local/bin/backup_volumes.sh >> /var/log/career-ai-backup.log 2>&1

# Daily configuration backup (3 AM)
0 3 * * * root /usr/local/bin/backup_config.sh >> /var/log/career-ai-backup.log 2>&1

# Weekly S3 sync to glacier (Sunday 4 AM)
0 4 * * 0 root aws s3 sync s3://career-ai-prod-backups s3://career-ai-prod-backups-archive --storage-class GLACIER
```

---

## Manual Backups

### Quick Database Backup

```bash
#!/bin/bash
# quick_backup.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="manual_backup_$TIMESTAMP.sql.gz"

docker exec career-ai-postgres pg_dump -U postgres career_ai_prod | gzip > $BACKUP_FILE

echo "Backup created: $BACKUP_FILE"
aws s3 cp $BACKUP_FILE s3://career-ai-prod-backups/manual/
echo "Backup uploaded to S3"
```

### Incremental Backup

```bash
#!/bin/bash
# incremental_backup.sh

# Create base backup
docker exec career-ai-postgres pg_basebackup -U postgres -D /backup/base -Xfetch

# Backup WAL files for incremental restore
cp -r /var/lib/postgresql/data/pg_wal /backup/wal

# Compress and upload
tar -czf incremental_backup_$(date +%Y%m%d_%H%M%S).tar.gz /backup/base /backup/wal
aws s3 cp incremental_backup_*.tar.gz s3://career-ai-prod-backups/incremental/
```

---

## Backup Verification

### Automated Verification

```bash
#!/bin/bash
# verify_backups.sh

echo "Verifying recent backups..."

# Check backup age
LATEST_BACKUP=$(aws s3 ls s3://career-ai-prod-backups/db/ | tail -1 | awk '{print $4}')
BACKUP_DATE=$(aws s3 ls s3://career-ai-prod-backups/db/ | tail -1 | awk '{print $1, $2}')

echo "Latest backup: $LATEST_BACKUP"
echo "Backup date: $BACKUP_DATE"

# Check backup size
BACKUP_SIZE=$(aws s3 ls s3://career-ai-prod-backups/db/$LATEST_BACKUP | awk '{print $3}')
BACKUP_SIZE_MB=$((BACKUP_SIZE / 1024 / 1024))
echo "Backup size: ${BACKUP_SIZE_MB}MB"

# Verify backup is valid
if [ $BACKUP_SIZE_MB -lt 10 ]; then
    echo "WARNING: Backup size seems too small"
    exit 1
fi

# Download and test restore on staging
echo "Testing backup restore on staging..."
aws s3 cp s3://career-ai-prod-backups/db/$LATEST_BACKUP backup_test.sql.gz
gunzip -t backup_test.sql.gz || exit 1

# Verify backup integrity
docker run --rm -v /opt/career-ai-staging:/data \
  alpine gunzip -t backup_test.sql.gz

echo "✅ Backup verification successful"
```

### Monthly Full Restore Test

**Schedule**: First Sunday of each month, 1 AM

```bash
#!/bin/bash
# monthly_restore_test.sh

echo "Starting monthly full restore test..."

# Download latest backup
aws s3 cp s3://career-ai-prod-backups/db/$(aws s3 ls s3://career-ai-prod-backups/db/ | tail -1 | awk '{print $4}') latest_backup.sql.gz

# Restore to staging database
docker run --rm -d \
  --name staging-postgres \
  -e POSTGRES_PASSWORD=staging_pass \
  -v staging_data:/var/lib/postgresql/data \
  postgres:15-alpine

sleep 10

# Load backup
gunzip -c latest_backup.sql.gz | docker exec -i staging-postgres psql -U postgres

# Run verification queries
echo "Running verification queries..."

QUERY_RESULTS=$(docker exec staging-postgres psql -U postgres -c "SELECT COUNT(*) FROM users;")
echo "User count: $QUERY_RESULTS"

if [ -z "$QUERY_RESULTS" ]; then
    echo "❌ Restore test FAILED"
    exit 1
fi

# Cleanup
docker stop staging-postgres
docker volume rm staging_data

echo "✅ Monthly restore test PASSED"
```

---

## Recovery Procedures

### Quick Recovery (< 1 hour downtime)

**Scenario**: Database corruption, recent backup available

```bash
#!/bin/bash
# quick_recovery.sh

BACKUP_FILE=$1  # e.g., db_backup_20240115_120000.sql.gz

echo "Starting quick recovery..."
echo "Using backup: $BACKUP_FILE"

# 1. Stop application services
docker-compose stop backend frontend

# 2. Create emergency backup
docker exec career-ai-postgres pg_dump -U postgres career_ai_prod | gzip > emergency_backup_$(date +%s).sql.gz
aws s3 cp emergency_backup_*.sql.gz s3://career-ai-prod-backups/emergency/

# 3. Download restore backup
aws s3 cp s3://career-ai-prod-backups/$BACKUP_FILE ./

# 4. Restore database
gunzip -c $BACKUP_FILE | docker exec -i career-ai-postgres psql -U postgres career_ai_prod

# 5. Verify restore
docker exec career-ai-postgres psql -U postgres career_ai_prod -c "SELECT COUNT(*) FROM users;"

# 6. Restart services
docker-compose up -d backend frontend

# 7. Run health checks
sleep 10
curl -f http://localhost:8000/health || echo "Health check failed"

echo "✅ Recovery completed"
```

### Full Disaster Recovery (< 4 hours)

**Scenario**: Complete infrastructure failure, need to restore to new server

```bash
#!/bin/bash
# disaster_recovery.sh

TARGET_HOST=$1  # e.g., new.server.ip
TARGET_USER=$2  # e.g., ubuntu

echo "Starting disaster recovery to $TARGET_HOST"

# 1. Set up new server
ssh $TARGET_USER@$TARGET_HOST << 'EOF'
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo mkdir -p /opt/career-ai-platform
EOF

# 2. Copy application code
scp -r /opt/career-ai-platform/* $TARGET_USER@$TARGET_HOST:/opt/career-ai-platform/

# 3. Download latest backups
aws s3 cp s3://career-ai-prod-backups/db/$(aws s3 ls s3://career-ai-prod-backups/db/ | tail -1 | awk '{print $4}') latest_db_backup.sql.gz
scp latest_db_backup.sql.gz $TARGET_USER@$TARGET_HOST:/tmp/

# 4. Restore to new server
ssh $TARGET_USER@$TARGET_HOST << 'EOF'
cd /opt/career-ai-platform

# Restore database
gunzip -c /tmp/latest_db_backup.sql.gz | docker exec -i career-ai-postgres psql -U postgres career_ai_prod

# Update DNS
aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch file:///tmp/dns_update.json

# Verify
curl -f http://localhost:8000/health
EOF

echo "✅ Disaster recovery completed"
```

---

## Disaster Recovery Plan

### Infrastructure Failover

**Primary Location**: AWS Region A (us-east-1)
**Secondary Location**: AWS Region B (us-west-2)

**Failover Procedure**:

```bash
#!/bin/bash
# failover_to_secondary.sh

echo "Initiating failover to secondary region..."

# 1. Verify primary is down
if curl -f http://primary.yourdomain.com/health 2>/dev/null; then
    echo "Primary is still up, aborting failover"
    exit 1
fi

# 2. Restore to secondary region
aws s3 cp s3://career-ai-prod-backups/db/latest_backup.sql.gz .
docker exec -i secondary-postgres psql -U postgres < latest_backup.sql.gz

# 3. Update DNS to secondary
aws route53 change-resource-record-sets \
  --hosted-zone-id Z123456789ABC \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.yourdomain.com",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [{"Value": "secondary.ip.address"}]
      }
    }]
  }'

# 4. Verify secondary is healthy
sleep 30
curl -f http://secondary.yourdomain.com/health || exit 1

echo "✅ Failover completed"
```

### RTO/RPO Compliance

**Daily Recovery Drills**:
- Test restore from hourly backup
- Time the recovery process
- Document any issues
- Update procedures as needed

**Monthly Comprehensive Test**:
- Full disaster recovery simulation
- Involve all team members
- Document results
- Post-incident review

---

## Compliance & Retention

### Retention Policies

**Backup Retention Schedule**:
- Hourly backups: 7 days
- Daily backups: 30 days
- Weekly backups: 90 days
- Monthly backups: 1 year
- Yearly backups: 7 years (legal requirement)

**Encryption**:
- In-transit: TLS 1.3
- At-rest: AES-256
- S3 encryption: Enabled
- KMS key rotation: Quarterly

### Compliance Certifications

**SOC 2 Type II Compliance**:
- Backup frequency audit
- Restore testing audit
- Access logging
- Data classification

**GDPR Compliance**:
- Data retention policy enforcement
- Right to deletion compliance
- Data residency verification
- Audit trail maintenance

### Audit Logging

```bash
# Enable comprehensive backup audit logging
cat > /var/log/career-ai-backup-audit.log << 'EOF'
Backup Operations Audit Log

Date: $(date)
Backup File: $BACKUP_FILE
Backup Size: $SIZE_MB MB
Backup Type: [HOURLY|DAILY|WEEKLY]
Status: [SUCCESS|FAILURE]
Duration: $DURATION_SECONDS seconds
Operator: $USER
Verification: [PASSED|FAILED]
EOF
```

---

## Monitoring & Alerting

### Backup Monitoring

```bash
# Check backup status
aws s3 ls s3://career-ai-prod-backups/db/ | tail -10

# Monitor backup upload
aws cloudwatch get-metric-statistics \
  --namespace AWS/S3 \
  --metric-name NumberOfObjects \
  --dimensions Name=BucketName,Value=career-ai-prod-backups \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Average
```

### Backup Failure Alerts

```bash
#!/bin/bash
# monitor_backup_alerts.sh

# Check if latest backup is recent (within 2 hours)
LATEST_BACKUP_TIME=$(aws s3api head-object --bucket career-ai-prod-backups --key $(aws s3 ls s3://career-ai-prod-backups/db/ | tail -1 | awk '{print $4}') --query LastModified --output text)
CURRENT_TIME=$(date -u +%s)
BACKUP_TIME=$(date -u -d "$LATEST_BACKUP_TIME" +%s)
TIME_DIFF=$((CURRENT_TIME - BACKUP_TIME))

if [ $TIME_DIFF -gt 7200 ]; then
    echo "ALERT: Backup is older than 2 hours"
    # Send alert
    curl -X POST $SLACK_WEBHOOK \
      -H 'Content-Type: application/json' \
      -d '{"text": "🚨 ALERT: Database backup is outdated (older than 2 hours)"}'
fi
```

---

## Best Practices

1. **3-2-1 Backup Rule**: 3 copies, 2 different media types, 1 offsite
2. **Test Regularly**: Monthly restore testing mandatory
3. **Automate**: Use cron jobs for scheduled backups
4. **Monitor**: Alert on backup failures immediately
5. **Document**: Keep runbooks updated
6. **Encrypt**: Always encrypt backups in transit and at rest
7. **Verify**: Check backup integrity periodically
8. **Educate**: Train team on recovery procedures

---

## Emergency Contact

**Backup Failures**: #alerts channel
**RTO Breach**: Page on-call engineer
**Compliance Issue**: Email compliance@yourdomain.com
