# SmartShop AI - Deployment Guide

Complete guide for deploying SmartShop AI to production environments.

## Table of Contents
1. [Pre-deployment Checklist](#pre-deployment-checklist)
2. [AWS Deployment](#aws-deployment)
3. [Google Cloud Deployment](#google-cloud-deployment)
4. [Heroku Deployment](#heroku-deployment)
5. [Docker Registry Push](#docker-registry-push)
6. [Environment Setup](#environment-setup)
7. [Monitoring & Scaling](#monitoring--scaling)
8. [Backup & Recovery](#backup--recovery)

---

## Pre-deployment Checklist

### Security
- [ ] Set `ENVIRONMENT=production`
- [ ] Set a strong `POSTGRES_PASSWORD` for docker-compose deployments
- [ ] Use HTTPS/TLS certificates
- [ ] Configure SSL/TLS for database
- [ ] Enable CORS for specific domains only
- [ ] Use environment variables for all secrets
- [ ] Enable API rate limiting
- [ ] Configure firewalls and security groups

### Performance
- [ ] Configure Redis caching
- [ ] Enable database connection pooling
- [ ] Set up CDN for static assets
- [ ] Configure compression
- [ ] Test under load
- [ ] Set appropriate worker counts

### Data & Compliance
- [ ] Setup automated backups
- [ ] Configure data retention policies
- [ ] Enable audit logging
- [ ] Implement GDPR compliance
- [ ] Setup data encryption
- [ ] Configure automated updates

### Testing
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Performance tests: `pytest tests/performance/`
- [ ] Security scan: `bandit -r agents/ utils/ api.py`
- [ ] Code quality: `pylint agents/ utils/`

### Documentation
- [ ] Update API documentation
- [ ] Document deployment procedure
- [ ] Create runbook for common issues
- [ ] Document scaling procedures

## AWS Deployment

### Using ECS (Recommended)

#### 1. Create ECR Repository
```bash
# Create repo
aws ecr create-repository --repository-name smartshop-api

# Get login token
aws ecr get-authorization-token

# Build and push image
docker build -t smartshop-api:1.0 .
docker tag smartshop-api:1.0 <account>.dkr.ecr.<region>.amazonaws.com/smartshop-api:1.0
docker push <account>.dkr.ecr.<region>.amazonaws.com/smartshop-api:1.0
```

#### 2. Create RDS Database
```bash
aws rds create-db-instance \
  --db-instance-identifier smartshop-db \
  --db-instance-class db.t4g.micro \
  --engine postgres \
  --master-username admin \
  --allocated-storage 20 \
  --backup-retention-period 7
```

#### 3. Create ElastiCache Redis
```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id smartshop-cache \
  --engine redis \
  --cache-node-type cache.t4g.micro \
  --engine-version 7.0
```

#### 4. Create ECS Task Definition
```json
{
  "family": "smartshop-api",
  "containerDefinitions": [
    {
      "name": "smartshop-api",
      "image": "<account>.dkr.ecr.<region>.amazonaws.com/smartshop-api:1.0",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://admin:password@smartshop-db.xxxxx.rds.amazonaws.com:5432/smartshop"
        },
        {
          "name": "REDIS_URL",
          "value": "redis://smartshop-cache.xxxxx.cache.amazonaws.com:6379"
        }
      ],
      "memory": 512,
      "cpu": 256
    }
  ]
}
```

#### 5. Create ECS Service
```bash
aws ecs create-service \
  --cluster smartshop-cluster \
  --service-name smartshop-api \
  --task-definition smartshop-api:1 \
  --desired-count 2 \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:...
```

#### 6. Setup Auto-scaling
```bash
aws autoscaling create-launch-configuration \
  --launch-configuration-name smartshop-lc \
  --image-id ami-xxxxx \
  --instance-type t3.small

aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name smartshop-asg \
  --launch-configuration-name smartshop-lc \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 2
```

### Estimated AWS Costs
- RDS (db.t4g.micro): ~$20/month
- ElastiCache (cache.t4g.micro): ~$15/month
- ECS (2x t3.small): ~$50/month
- Data transfer: ~$10/month
- **Total**: ~$95/month

---

## Google Cloud Deployment

### Using Cloud Run (Serverless)

#### 1. Authenticate
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

#### 2. Build and Deploy
```bash
# Deploy directly
gcloud run deploy smartshop-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --set-env-vars SUPABASE_URL=your-url,SUPABASE_KEY=your-key

# Or build first then deploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/smartshop-api
gcloud run deploy smartshop-api \
  --image gcr.io/YOUR_PROJECT_ID/smartshop-api
```

#### 3. Configure Database
```bash
# Create Cloud SQL instance
gcloud sql instances create smartshop-db \
  --database-version=POSTGRES_15 \
  --tier=db-g1-small \
  --region=us-central1

# Create database
gcloud sql databases create smartshop \
  --instance=smartshop-db
```

#### 4. Setup Redis
```bash
gcloud redis instances create smartshop-cache \
  --size=1 \
  --region=us-central1 \
  --redis-version=7.0
```

#### 5. Connect Cloud Run to Cloud SQL
```bash
gcloud run services update smartshop-api \
  --add-cloudsql-instances=YOUR_PROJECT:us-central1:smartshop-db \
  --set-env-vars CLOUD_SQL_CONNECTION_NAME=YOUR_PROJECT:us-central1:smartshop-db
```

### Estimated GCP Costs
- Cloud Run: Pay per request (~$20/month for 1M requests)
- Cloud SQL (db-g1-small): ~$60/month
- Memorystore Redis: ~$30/month
- **Total**: ~$110/month

---

## Heroku Deployment

### Using Heroku CLI

#### 1. Create Heroku App
```bash
heroku create smartshop-api
```

#### 2. Add PostgreSQL Addon
```bash
heroku addons:create heroku-postgresql:standard-0 -a smartshop-api
```

#### 3. Add Redis Addon
```bash
heroku addons:create heroku-redis:premium-0 -a smartshop-api
```

#### 4. Set Environment Variables
```bash
heroku config:set \
  SUPABASE_URL=your-url \
  SUPABASE_KEY=your-key \
  ENVIRONMENT=production \
  ALLOWED_ORIGINS=https://yourdomain.com \
  -a smartshop-api
```

#### 5. Create Procfile
```
web: uvicorn api:app --host 0.0.0.0 --port $PORT
worker: python graph/pipeline.py
```

#### 6. Deploy
```bash
git push heroku main
```

#### 7. View Logs
```bash
heroku logs -t -a smartshop-api
```

### Estimated Heroku Costs
- Dyno (Performance-M): ~$50/month
- PostgreSQL (standard-0): ~$50/month
- Redis (premium-0): ~$30/month
- **Total**: ~$130/month

---

## Docker Registry Push

### Push to DockerHub
```bash
# Login
docker login

# Build
docker build -t yourusername/smartshop-api:1.0.0 .

# Push
docker push yourusername/smartshop-api:1.0.0

# Tag latest
docker tag yourusername/smartshop-api:1.0.0 yourusername/smartshop-api:latest
docker push yourusername/smartshop-api:latest
```

### Push to AWS ECR
```bash
# Login
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

# Build and push
docker build -t smartshop-api:1.0.0 .
docker tag smartshop-api:1.0.0 <account>.dkr.ecr.us-east-1.amazonaws.com/smartshop-api:1.0.0
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/smartshop-api:1.0.0
```

---

## Environment Setup

### Production .env
```bash
# Database (Supabase)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-production-key

# Database (docker-compose)
POSTGRES_DB=smartshop_ai
POSTGRES_USER=smartshop_user
POSTGRES_PASSWORD=change-me-strong-password

# API
API_PORT=8000
API_HOST=0.0.0.0
ENVIRONMENT=production
LOG_LEVEL=INFO

# Security
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# AI/Search
COHERE_API_KEY=your-cohere-api-key
TAVILY_API_KEY=your-tavily-api-key

# Email
SMTP_SERVER=smtp.gmail.com
SENDER_EMAIL=alerts@yourdomain.com
SENDER_PASSWORD=your-app-password

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
LOKI_URL=http://loki:3100
DATADOG_API_KEY=your-datadog-key

# Feature Flags
ENABLE_PRICE_PREDICTIONS=True
ENABLE_BUNDLE_RECOMMENDATIONS=True
ENABLE_EMAIL_ALERTS=True
```

---

## Monitoring & Scaling

### Health Checks
```bash
# Check API health
curl https://api.yourdomain.com/health

# CloudWatch monitoring (AWS)
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=smartshop-api \
  --start-time 2024-01-20T00:00:00Z \
  --end-time 2024-01-21T00:00:00Z \
  --period 300 \
  --statistics Average
```

### Auto-scaling Policies

#### Scale up when CPU > 70%
```bash
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name smartshop-asg \
  --policy-name scale-up \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration file://target-tracking.json
```

#### target-tracking.json
```json
{
  "TargetValue": 70.0,
  "PredefinedMetricSpecification": {
    "PredefinedMetricType": "ASGAverageCPUUtilization"
  },
  "ScaleOutCooldown": 300,
  "ScaleInCooldown": 300
}
```

### Monitoring Tools
- **Application**: Sentry for error tracking
- **Metrics**: CloudWatch, DataDog, or Prometheus
- **Logs**: Cloud Logging (GCP) or CloudWatch (AWS)
- **APM**: New Relic or Datadog

---

## Backup & Recovery

### Database Backups
```bash
# AWS RDS automated backups (7 days retention)
aws rds modify-db-instance \
  --db-instance-identifier smartshop-db \
  --backup-retention-period 30 \
  --preferred-backup-window "03:00-04:00"

# Manual snapshot
aws rds create-db-snapshot \
  --db-snapshot-identifier smartshop-backup-2024-01-20 \
  --db-instance-identifier smartshop-db

# GCP Cloud SQL backups
gcloud sql backups create smartshop-backup-2024-01-20 \
  --instance=smartshop-db
```

### Recovery Procedure
```bash
# Restore from snapshot (AWS)
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier smartshop-db-restored \
  --db-snapshot-identifier smartshop-backup-2024-01-20

# Restore from backup (GCP)
gcloud sql backups restore \
  --backup-configuration=default \
  --backup-instance=smartshop-db \
  20240120T030000
```

### Data Export
```bash
# Export to CSV
psql $DATABASE_URL -c "\COPY products TO 'products.csv' WITH CSV HEADER"

# Backup to S3
pg_dump $DATABASE_URL | gzip | \
  aws s3 cp - s3://smartshop-backups/db-backup-$(date +%Y%m%d).sql.gz

# Backup to GCS
gsutil cp smartshop-backup.sql gs://smartshop-backups/
```

---

## Post-Deployment

### Verify Deployment
```bash
# Check services
curl https://api.yourdomain.com/health

# Check database connectivity
curl https://api.yourdomain.com/api/health

# Monitor logs
# View in CloudWatch, Cloud Logging, or Sentry
```

### Rollback Procedure
```bash
# Using ECS
aws ecs update-service \
  --cluster smartshop-cluster \
  --service smartshop-api \
  --task-definition smartshop-api:2

# Using Heroku
heroku releases
heroku rollback v10

# Using Cloud Run
gcloud run deploy smartshop-api \
  --image gcr.io/PROJECT/smartshop-api:previous-version
```

### Performance Tuning
```bash
# Increase worker processes
gunicorn api:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# Database connection pooling
set max_connections = 200 in PostgreSQL

# Redis optimization
CONFIG SET maxmemory-policy allkeys-lru
```

---

## Budget Optimization

### Cost Reduction Strategies
1. Use spot instances (AWS) - save 70%
2. Use preemptible instances (GCP) - save 60%
3. Right-size resources based on actual usage
4. Use reserved instances for predictable workloads
5. Enable caching aggressively
6. Use CDN for static assets

### Monitoring Costs
```bash
# AWS
aws ce get-cost-and-usage --time-period Start=2024-01-01,End=2024-01-31

# GCP
gcloud billing accounts list
gcloud compute billing-accounts get-iam-policy <BILLING_ACCOUNT>

# Track using tags/labels
aws ec2 create-tags --resources <instance-id> --tags Key=Cost-Center,Value=Engineering
```

---

## Support

For deployment issues:
- 📧 Email: deployment@smartshop.ai
- 📖 Docs: https://docs.smartshop.ai/deployment
- 🐛 Issues: GitHub Issues
- 💬 Discord: discord.gg/smartshop

---

**Congratulations!** Your SmartShop AI is now in production! 🚀
