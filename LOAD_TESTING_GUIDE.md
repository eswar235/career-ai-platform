# Load Testing & Capacity Planning Guide - Career AI Platform

Guide for performance testing and planning for production scale.

## Table of Contents
1. [Load Testing Strategy](#load-testing-strategy)
2. [Test Scenarios](#test-scenarios)
3. [Tools & Setup](#tools--setup)
4. [Running Tests](#running-tests)
5. [Analyzing Results](#analyzing-results)
6. [Capacity Planning](#capacity-planning)
7. [Performance Optimization](#performance-optimization)

---

## Load Testing Strategy

### Testing Phases

**Phase 1: Smoke Test** (Week 1)
- Verify test environment
- 10 concurrent users
- 5 minute duration
- Baseline metrics collection

**Phase 2: Load Test** (Week 2)
- Realistic production load
- 100 concurrent users
- 30 minute duration
- Peak hour simulation

**Phase 3: Stress Test** (Week 3)
- Beyond expected capacity
- 500 concurrent users
- 15 minute ramp-up
- System failure point identification

**Phase 4: Soak Test** (Week 4)
- Extended load
- 200 concurrent users
- 4 hour duration
- Memory leak detection

### Key Metrics

**Response Time**:
- p50: < 200ms
- p95: < 500ms
- p99: < 1000ms

**Throughput**:
- Target: 100 requests/second
- Error rate: < 0.1%

**Resource Utilization**:
- CPU: < 80%
- Memory: < 85%
- Disk I/O: < 75%

---

## Test Scenarios

### Scenario 1: User Authentication

```
Endpoint: POST /auth/login
Payload: {"email": "user@example.com", "password": "password123"}
Expected Response: 200 OK with JWT token
Concurrent Users: 100
Duration: 30 minutes
Think Time: 2 seconds
```

### Scenario 2: Job Search

```
Endpoint: GET /jobs/search?keyword=python&location=remote
Parameters: Vary by user
Expected Response: 200 OK with job listings
Concurrent Users: 200
Duration: 1 hour
Ramp-up: 100 users/minute
```

### Scenario 3: Resume Upload & Parsing

```
Endpoint: POST /resumes/upload
Payload: PDF file (2-5MB)
Expected Response: 202 Accepted with parsing job ID
Concurrent Users: 50
Duration: 30 minutes
File Sizes: Random 2-5MB
```

### Scenario 4: Cover Letter Generation

```
Endpoint: POST /cover-letters/generate
Payload: Job description + resume data
Expected Response: 200 OK with generated content
Concurrent Users: 30
Duration: 30 minutes
Think Time: 5 seconds (AI processing time)
```

### Scenario 5: Application Tracking

```
Endpoint: GET /applications?status=pending&sort=date
Parameters: Various filters
Expected Response: 200 OK with application list
Concurrent Users: 150
Duration: 1 hour
Cache hits expected: 70%
```

---

## Tools & Setup

### Apache JMeter Setup

**Installation**:

```bash
# Download JMeter
wget https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-5.6.tgz
tar -xzf apache-jmeter-5.6.tgz
cd apache-jmeter-5.6

# Install plugins
./bin/pluginmanager.sh install-all-plugins

# Run GUI
./bin/jmeter.sh
```

**Test Plan Structure**:

```
Test Plan
├── Thread Group (100 users, 30 min, 10 second ramp-up)
├── HTTP Request Defaults (hostname, port)
├── Cookie Manager
├── Cache Manager
├── HTTP Request: Login
├── Extractors (JWT token)
├── HTTP Request: Search Jobs
├── HTTP Request: Apply for Job
├── Listeners
│   ├── View Results Tree
│   ├── Summary Report
│   └── Graph Results
└── Assertions
    ├── Response Code
    └── Response Time
```

### Locust Setup (Python)

**Installation**:

```bash
pip install locust
```

**locustfile.py**:

```python
from locust import HttpUser, task, between
import json

class CareerAIUser(HttpUser):
    wait_time = between(2, 5)
    
    @task(3)
    def search_jobs(self):
        self.client.get("/jobs/search?keyword=python&page=1")
    
    @task(1)
    def view_job_detail(self):
        self.client.get("/jobs/123")
    
    def on_start(self):
        # Login before starting tasks
        response = self.client.post(
            "/auth/login",
            json={"email": "user@example.com", "password": "pass123"}
        )
        self.token = response.json()["access_token"]
        self.client.headers.update({
            "Authorization": f"Bearer {self.token}"
        })

# Run with: locust -f locustfile.py --host=http://localhost:8000
```

### k6 Setup (JavaScript)

**Installation**:

```bash
# macOS
brew install k6

# Linux
apt-get install k6

# Windows
choco install k6
```

**Load Test Script** (load_test.js):

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp-up
    { duration: '5m', target: 100 },   // Stay at 100
    { duration: '2m', target: 200 },   // Ramp-up to 200
    { duration: '5m', target: 200 },   // Stay at 200
    { duration: '2m', target: 0 },     // Ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.1'],
  },
};

export default function() {
  // Login
  let loginRes = http.post('http://localhost:8000/auth/login', {
    email: 'user@example.com',
    password: 'password123',
  });
  
  let token = loginRes.json('access_token');
  
  let headers = {
    headers: { Authorization: `Bearer ${token}` },
  };
  
  // Search jobs
  let searchRes = http.get('http://localhost:8000/jobs/search?keyword=python', headers);
  
  check(searchRes, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  sleep(3);
}

// Run with: k6 run load_test.js
```

---

## Running Tests

### Pre-Test Checklist

```bash
#!/bin/bash
# pre_test_checklist.sh

echo "Pre-Load Test Checklist"
echo "======================="

# 1. Verify test environment is clean
echo "1. Checking test database..."
docker exec career-ai-postgres psql -U postgres career_ai_test -c "SELECT COUNT(*) FROM users;"

# 2. Clear caches
echo "2. Clearing caches..."
docker exec career-ai-redis redis-cli FLUSHALL

# 3. Restart services
echo "3. Restarting services..."
docker-compose restart backend frontend

# 4. Wait for health checks
echo "4. Waiting for services to be healthy..."
sleep 30

# 5. Verify endpoints
echo "5. Testing endpoints..."
curl -f http://localhost:8000/health
curl -f http://localhost:3000

# 6. Collect baseline metrics
echo "6. Collecting baseline metrics..."
curl http://localhost:8000/metrics > baseline_metrics.txt

echo "✅ Pre-test checklist complete"
```

### Running JMeter Test

```bash
#!/bin/bash
# run_jmeter_test.sh

TEST_NAME=$1
USERS=$2
DURATION=$3

echo "Starting JMeter load test"
echo "Test: $TEST_NAME, Users: $USERS, Duration: $DURATION"

./apache-jmeter-5.6/bin/jmeter.sh \
  -n \
  -t tests/$TEST_NAME.jmx \
  -Jusers=$USERS \
  -Jduration=$DURATION \
  -l results/test_$TEST_NAME_$(date +%s).jtl \
  -j logs/jmeter_$TEST_NAME_$(date +%s).log \
  -Jreport_dir=results/html_report_$TEST_NAME_$(date +%s)

echo "✅ Test complete"
```

### Running k6 Test

```bash
#!/bin/bash
# run_k6_test.sh

k6 run \
  --vus 100 \
  --duration 30m \
  --out csv=results/k6_results_$(date +%s).csv \
  load_test.js
```

---

## Analyzing Results

### JMeter Result Analysis

```bash
#!/bin/bash
# analyze_jmeter_results.sh

RESULTS_FILE=$1

echo "JMeter Results Analysis"
echo "======================="

# Extract key metrics using awk
awk -F',' '
NR==1 {next}
{
  samples++
  response_time += $2
  if ($2 < min_rt || min_rt == 0) min_rt = $2
  if ($2 > max_rt) max_rt = $2
  if ($3 ~ /200/) success++
  else failure++
}
END {
  avg_rt = response_time / samples
  success_rate = (success / samples) * 100
  
  print "Total Samples: " samples
  print "Success Rate: " success_rate "%"
  print "Failures: " failure
  print "Average Response Time: " avg_rt "ms"
  print "Min Response Time: " min_rt "ms"
  print "Max Response Time: " max_rt "ms"
}
' $RESULTS_FILE
```

### k6 Result Analysis

```bash
#!/bin/bash
# analyze_k6_results.sh

RESULTS_FILE=$1

echo "k6 Results Analysis"
echo "==================="

# Generate summary
k6 run --out csv=$RESULTS_FILE summary_test.js

# Python script for detailed analysis
python3 << 'EOF'
import csv
import statistics

with open('$RESULTS_FILE', 'r') as f:
    reader = csv.DictReader(f)
    times = []
    errors = 0
    total = 0
    
    for row in reader:
        total += 1
        if row['error']:
            errors += 1
        else:
            times.append(float(row['time']))
    
    if times:
        print(f"Total Requests: {total}")
        print(f"Errors: {errors}")
        print(f"Success Rate: {((total-errors)/total)*100:.2f}%")
        print(f"Average Response Time: {statistics.mean(times):.2f}ms")
        print(f"Median Response Time: {statistics.median(times):.2f}ms")
        print(f"P95: {sorted(times)[int(len(times)*0.95)]:.2f}ms")
        print(f"P99: {sorted(times)[int(len(times)*0.99)]:.2f}ms")
EOF
```

### Grafana Dashboard Import

```bash
# Create Prometheus data source in Grafana
curl -X POST http://localhost:3000/api/datasources \
  -H "Authorization: Bearer $GRAFANA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Prometheus",
    "type": "prometheus",
    "url": "http://prometheus:9090",
    "access": "proxy",
    "isDefault": true
  }'

# Import load test dashboard
curl -X POST http://localhost:3000/api/dashboards/db \
  -H "Authorization: Bearer $GRAFANA_TOKEN" \
  -H "Content-Type: application/json" \
  -d @load_test_dashboard.json
```

---

## Capacity Planning

### Resource Requirements

**Current Capacity** (1 backend instance):
- Max concurrent users: 100
- Requests/second: 50
- CPU utilization: 40%
- Memory utilization: 60%

**Projected Growth**:

| Month | Users | RPS | Backends | Memory | CPU |
|-------|-------|-----|----------|--------|-----|
| Jan   | 10k   | 50  | 1        | 2GB    | 2   |
| Apr   | 50k   | 200 | 2        | 4GB    | 4   |
| Jul   | 200k  | 800 | 4        | 8GB    | 8   |
| Dec   | 500k  | 2000| 8        | 16GB   | 16  |

### Scaling Strategy

**Horizontal Scaling** (add more instances):

```bash
# Scale backend to 3 instances
docker-compose up -d --scale backend=3

# Update Nginx load balancing
docker exec career-ai-nginx nginx -s reload

# Monitor load distribution
watch -n 5 'docker stats --no-stream'
```

**Vertical Scaling** (increase resources):

```yaml
# In docker-compose.prod.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
```

**Database Optimization**:

```sql
-- Add indexes for common queries
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_applications_user_id ON applications(user_id);

-- Enable query caching
ALTER SYSTEM SET shared_buffers = '512MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
```

---

## Performance Optimization

### Database Query Optimization

```python
# Bad: N+1 Query Problem
for user in db.query(User).all():
    print(user.applications)  # Queries database for each user

# Good: Eager loading
users = db.query(User).options(
    joinedload(User.applications)
).all()
```

### Caching Strategy

```python
# App-level caching with Redis
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

@app.get("/jobs/search")
@cached(namespace="jobs", expire=300)
async def search_jobs(keyword: str):
    # Cached for 5 minutes
    return db.query(Job).filter(Job.title.contains(keyword)).all()
```

### API Response Optimization

```python
# Use response models to limit fields
class JobListResponse(BaseModel):
    id: int
    title: str
    company: str
    
    class Config:
        from_attributes = True

@app.get("/jobs", response_model=List[JobListResponse])
async def list_jobs():
    return db.query(Job).all()
```

### Frontend Optimization

```typescript
// Code splitting
const JobSearchPage = lazy(() => import('./pages/JobSearch'));
const InterviewCoach = lazy(() => import('./pages/InterviewCoach'));

// Image optimization
import Image from 'next/image';
<Image 
  src="/job-image.jpg" 
  alt="Job" 
  width={300} 
  height={200}
  priority={false}
/>

// Data fetching optimization
const { data, isLoading } = useQuery(
  'jobs',
  fetchJobs,
  {
    staleTime: 5 * 60 * 1000,  // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  }
);
```

---

## Load Test Reports

### Sample Report Template

```markdown
# Load Test Report - Career AI Platform

## Test Date
January 15, 2024

## Test Configuration
- Tool: k6
- Duration: 30 minutes
- Concurrent Users: 100
- Ramp-up Time: 2 minutes
- Think Time: 2-5 seconds

## Results Summary

### Success Metrics
- Total Requests: 18,000
- Successful: 17,940 (99.7%)
- Failed: 60 (0.3%)

### Response Time Metrics
- Average: 245ms
- P50: 198ms
- P95: 428ms
- P99: 652ms

### Resource Utilization
- CPU: 65% peak
- Memory: 72% peak
- Disk I/O: 42% peak
- Network: 85 Mbps peak

## Conclusions
✅ System passed load test
✅ All SLA targets met
✅ No memory leaks detected

## Recommendations
1. Add database indexes for job search
2. Implement response caching
3. Consider CDN for static assets

## Next Steps
- Schedule stress test for next week
- Implement recommendations
- Monitor production metrics
```

---

## Automated Load Testing CI/CD

```yaml
# .github/workflows/load-test.yml
name: Weekly Load Test

on:
  schedule:
    - cron: '0 2 * * 6'  # Saturday 2 AM

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup k6
        uses: grafana/setup-k6-action@v1
      
      - name: Run load test
        run: k6 run tests/load_test.js
      
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: load-test-results
          path: results/
      
      - name: Comment on issue
        if: failure()
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '⚠️ Load test failed. Check results.'
            })
```

---

## References

- [Apache JMeter Documentation](https://jmeter.apache.org/usermanual/index.html)
- [Locust Documentation](https://docs.locust.io/)
- [k6 Documentation](https://k6.io/docs/)
- [Performance Testing Best Practices](https://en.wikipedia.org/wiki/Software_performance_testing)
