# Deployment Guide

## Environment Setup

### Local Development
```bash
# Install dependencies
pip install -e ".[dev]"

# Start database
docker-compose up -d

# Run migrations
alembic upgrade head

# Seed data
python -m app.seed

# Start server
uvicorn app.main:app --reload
```

## Production Deployment

### Docker Build

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t grant-service:latest .
docker run -p 8000:8000 --env-file .env grant-service:latest
```

### Docker Compose (Production)

Create a production `docker-compose.yml`:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: grants_svc
      POSTGRES_USER: grants_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U grants_user -d grants_svc"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://grants_user:${DB_PASSWORD}@postgres:5432/grants_svc
      ENVIRONMENT: production
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped

volumes:
  postgres_data:
```

## Kubernetes Deployment

Example Kubernetes manifests:

### ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grant-service-config
data:
  ENVIRONMENT: production
```

### Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: grant-service-secrets
type: Opaque
stringData:
  DATABASE_URL: postgresql+asyncpg://grants_user:password@postgres:5432/grants_svc
```

### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grant-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: grant-service
  template:
    metadata:
      labels:
        app: grant-service
    spec:
      containers:
      - name: api
        image: grant-service:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: grant-service-config
        - secretRef:
            name: grant-service-secrets
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: grant-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: grant-service
```

## CI/CD Pipeline

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: grants_svc_test
          POSTGRES_USER: grants_user
          POSTGRES_PASSWORD: password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -e ".[dev]"
    
    - name: Run tests
      run: pytest --cov=app
      env:
        DATABASE_URL: postgresql+asyncpg://grants_user:password@localhost:5432/grants_svc_test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: success()
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      run: |
        # Add your deployment commands here
        echo "Deploying to production..."
```

## Monitoring & Logging

### Health Checks
- Endpoint: `GET /health`
- Response: `{"status": "ok"}`

### Structured Logging
All logs are JSON-formatted via structlog. Integrate with:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Datadog
- CloudWatch
- Splunk

### Metrics to Monitor
- Request latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- Database connection pool usage
- Grant creation/revocation rate
- Cache hit ratios (if implemented)

## Backup & Recovery

### Database Backups
```bash
# Backup
pg_dump -U grants_user grants_svc > backup.sql

# Restore
psql -U grants_user grants_svc < backup.sql
```

### Automated Backups (Cron)
```bash
0 2 * * * pg_dump -U grants_user grants_svc | gzip > /backups/grant_svc_$(date +\%Y\%m\%d).sql.gz
```

## Scaling Considerations

1. **Database**: Use read replicas for scaling reads
2. **API**: Run multiple instances behind load balancer
3. **Cache**: Implement Redis for grant status caching
4. **Async**: Leverage async/await for high concurrency

## Security Checklist

- [ ] Use HTTPS in production
- [ ] Implement API authentication (OAuth/JWT)
- [ ] Set up rate limiting
- [ ] Enable CORS properly
- [ ] Validate all inputs
- [ ] Use environment variables for secrets
- [ ] Enable database SSL
- [ ] Set up security headers
- [ ] Run security scans
- [ ] Keep dependencies updated

## Troubleshooting

### High Memory Usage
- Check for memory leaks in long-running queries
- Monitor connection pool size
- Use async to prevent thread accumulation

### Slow Requests
- Check database query performance
- Verify indexes are used
- Monitor database connections
- Enable query logging

### Connection Timeouts
- Check database availability
- Verify connection pool settings
- Check network connectivity
