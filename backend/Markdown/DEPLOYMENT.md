# FinCloud-AI Backend - Deployment Guide

## 🚀 Production Deployment

This guide covers deploying FinCloud-AI Backend to production environments.

## 📋 Pre-Deployment Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure strong database credentials
- [ ] Set up environment variables securely
- [ ] Configure CORS appropriately (not allow_origins=["*"])
- [ ] Set up monitoring and logging
- [ ] Configure API rate limiting
- [ ] Enable SSL/TLS
- [ ] Set up CI/CD pipeline
- [ ] Configure database backups
- [ ] Set up health checks

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t fincloud-ai-backend:latest .
```

### Run with Docker Compose

```bash
docker-compose up -d
```

Services will be available at:

- Backend: http://localhost:8000
- pgAdmin: http://localhost:5050
- PostgreSQL: localhost:5432

### Docker Compose Configuration

The included `docker-compose.yml` includes:

- PostgreSQL database
- Redis cache
- FastAPI backend
- pgAdmin (database management)

## ☁️ Cloud Platform Deployment

### AWS ECS (Elastic Container Service)

1. **Create ECR Repository**

   ```bash
   aws ecr create-repository --repository-name fincloud-ai-backend
   ```

2. **Push Image**

   ```bash
   docker tag fincloud-ai-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/fincloud-ai-backend:latest
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/fincloud-ai-backend:latest
   ```

3. **Create ECS Task Definition**
   - Use the pushed image
   - Set environment variables
   - Configure logging with CloudWatch

4. **Create ECS Service**
   - Use Fargate launch type
   - Configure load balancer (ALB)
   - Set auto-scaling policies

### Google Cloud Run

```bash
gcloud run deploy fincloud-ai-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars "DATABASE_URL=<your-database-url>" \
  --allow-unauthenticated
```

### Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name fincloud-ai-backend \
  --image myregistry.azurecr.io/fincloud-ai-backend:latest \
  --environment-variables DATABASE_URL=<your-database-url> \
  --ports 8000
```

## 🔧 Kubernetes Deployment

### Create Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fincloud-ai-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fincloud-ai-backend
  template:
    metadata:
      labels:
        app: fincloud-ai-backend
    spec:
      containers:
        - name: backend
          image: fincloud-ai-backend:latest
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: url
            - name: DEBUG
              value: "False"
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "1Gi"
              cpu: "1000m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: fincloud-ai-backend-service
spec:
  selector:
    app: fincloud-ai-backend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

### Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace fincloud

# Create secrets
kubectl create secret generic db-credentials \
  --from-literal=url=postgresql://user:password@host:5432/fincloud_db \
  -n fincloud

# Deploy
kubectl apply -f k8s/deployment.yaml -n fincloud

# Check status
kubectl get pods -n fincloud
kubectl get svc -n fincloud
```

## 🔒 Security Configuration

### Environment Variables

```bash
# .env.prod
APP_NAME=FinCloud-AI Backend
DEBUG=False
LOG_LEVEL=INFO

DATABASE_URL=postgresql://prod_user:strong_password@prod-db.example.com:5432/fincloud_prod
REDIS_URL=redis://prod-redis.example.com:6379/0

HOST=0.0.0.0
PORT=8000

# API Configuration
API_PREFIX=/api/v1

# ML Model Configuration
ANOMALY_CONTAMINATION=0.05
FORECAST_PERIODS=30

# Optional: Add API key authentication
API_KEY=your_secure_api_key_here
```

### Database Configuration

```bash
# Use managed PostgreSQL services:
# - AWS RDS
# - Google Cloud SQL
# - Azure Database for PostgreSQL

# With SSL/TLS enabled
postgresql+psycopg2://user:password@host:5432/dbname?sslmode=require
```

### CORS Configuration

Update in `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specify your frontend domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
```

## 📊 Monitoring & Logging

### CloudWatch (AWS)

```python
# Add to app/main.py
import logging
from watchtower import CloudWatchLogHandler

cloudwatch_handler = CloudWatchLogHandler(
    log_group='fincloud-ai-backend',
    stream_name='production'
)
logger.addHandler(cloudwatch_handler)
```

### Application Insights (Azure)

```python
from opencensus.ext.azure.log_exporter import AzureLogHandler

handler = AzureLogHandler(connection_string='InstrumentationKey=...')
logger.addHandler(handler)
```

### Datadog

```bash
# Configure via environment
export DD_API_KEY=your_api_key
export DD_SITE=datadoghq.com
export DD_SERVICE=fincloud-ai-backend
export DD_ENV=production
```

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Build Docker image
        run: docker build -t fincloud-ai-backend:${{ github.sha }} .

      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push fincloud-ai-backend:${{ github.sha }}

      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/fincloud-ai-backend \
            backend=fincloud-ai-backend:${{ github.sha }} \
            -n fincloud
```

## 📈 Performance Optimization

### Database Optimization

```sql
-- Create indexes for common queries
CREATE INDEX idx_cost_date ON processed_cost_data(date);
CREATE INDEX idx_anomaly_service ON anomalies(service);
CREATE INDEX idx_forecast_date ON forecasts(date);

-- Enable query plan analysis
EXPLAIN ANALYZE SELECT * FROM processed_cost_data WHERE service = 'ec2';
```

### Caching Strategy

```python
# Enable Redis caching
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cost_summary(days: int):
    # Cached for 5 minutes
    pass
```

### Connection Pooling

```python
# In database.py
engine = create_engine(
    settings.database_url,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

## 📦 Backup & Recovery

### Database Backup (PostgreSQL)

```bash
# Automated daily backup
pg_dump fincloud_db > backup_$(date +%Y%m%d).sql

# Or use AWS RDS Snapshots
aws rds create-db-snapshot \
  --db-instance-identifier fincloud-db \
  --db-snapshot-identifier fincloud-db-$(date +%Y%m%d)
```

### Data Recovery

```bash
# Restore from backup
psql fincloud_db < backup_20240101.sql

# Or AWS RDS restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier fincloud-db-restored \
  --db-snapshot-identifier fincloud-db-20240101
```

## 🔐 SSL/TLS Configuration

### Using Let's Encrypt with Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name api.fincloud.ai;

    ssl_certificate /etc/letsencrypt/live/api.fincloud.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.fincloud.ai/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Load Balancing

### Nginx Load Balancer

```nginx
upstream fincloud_backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 80;
    server_name api.fincloud.ai;

    location / {
        proxy_pass http://fincloud_backend;
    }
}
```

## 🧪 Production Testing

### Health Check

```bash
curl https://api.fincloud.ai/health
```

### Load Testing

```bash
# Using Apache Bench
ab -n 10000 -c 100 https://api.fincloud.ai/api/v1/cost/summary

# Using wrk
wrk -t12 -c400 -d30s https://api.fincloud.ai/api/v1/cost/summary
```

## 📝 Rollback Procedure

### Docker/Kubernetes

```bash
# Rollback to previous deployment
kubectl rollout undo deployment/fincloud-ai-backend -n fincloud

# Check rollout history
kubectl rollout history deployment/fincloud-ai-backend -n fincloud
```

## 🆘 Troubleshooting

### Database Connection Issues

```python
# Check connection
from sqlalchemy import text
db = SessionLocal()
db.execute(text("SELECT 1"))
db.close()
```

### High Memory Usage

```bash
# Monitor memory
docker stats fincloud_backend

# Check Python memory leaks
pip install memory-profiler
python -m memory_profiler app/main.py
```

### Slow Queries

```sql
-- Enable query logging
SET log_statement = 'all';
SET log_duration = on;

-- Analyze slow query
EXPLAIN ANALYZE <query>
```

## 📞 Support & Escalation

- Production Issues: alert@fincloud.ai
- On-call: Check PagerDuty
- Incident Response: Follow incident.md

---

**Last Updated**: 2024  
**Version**: 1.0.0
