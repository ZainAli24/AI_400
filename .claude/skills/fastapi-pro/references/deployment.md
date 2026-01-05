# Deployment Guide

## Table of Contents
- Docker Deployment
- Production Configuration
- Environment Variables
- Logging & Monitoring
- Performance Optimization

## Docker Deployment

### Basic Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run with production server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Multi-Stage Build (Optimized)

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/dbname
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=dbname
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
```

### Build and Run

```bash
# Build image
docker build -t fastapi-app .

# Run container
docker run -d -p 8000:8000 --name fastapi-app \
  -e DATABASE_URL=postgresql://user:password@localhost/dbname \
  fastapi-app

# With docker-compose
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

## Production Configuration

### Production Settings

```python
# app/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALLOWED_HOSTS: list = ["*"]

    # CORS
    ALLOWED_ORIGINS: list

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()
```

### Production Main File

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Production server command
# uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Environment Variables

### .env.production Example

```bash
# Application
APP_NAME="My FastAPI App"
APP_VERSION="1.0.0"
DEBUG=False

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Database
DATABASE_URL=postgresql://user:password@db-host:5432/production_db

# Security
SECRET_KEY=very-long-random-secret-key-generated-with-openssl-rand-hex-32
ALLOWED_HOSTS=["myapp.com","www.myapp.com"]

# CORS
ALLOWED_ORIGINS=["https://myapp.com","https://www.myapp.com"]

# Redis
REDIS_URL=redis://redis-host:6379/0

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@myapp.com
SMTP_PASSWORD=email-password
```

### Loading Environment Variables

```bash
# Generate secret key
openssl rand -hex 32

# Load environment file
export $(cat .env.production | xargs)

# Or use with docker-compose
docker-compose --env-file .env.production up -d
```

## Logging & Monitoring

### Logging Configuration

```python
# app/core/logging.py
import logging
import sys
from loguru import logger

class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())

def setup_logging():
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "format": "{time} {level} {message}",
                "level": "INFO"
            },
            {
                "sink": "logs/app.log",
                "rotation": "500 MB",
                "retention": "10 days",
                "level": "DEBUG"
            }
        ]
    )
```

### Request Logging Middleware

```python
from fastapi import Request
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} "
        f"completed in {process_time:.2f}s with status {response.status_code}"
    )

    return response
```

### Health Check Endpoint

```python
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Check database
        db.execute("SELECT 1")

        # Check Redis (if using)
        # redis_client.ping()

        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }, 503
```

## Performance Optimization

### Use Async Wherever Possible

```python
# Good - Async
@router.get("/items/{item_id}")
async def get_item(item_id: int):
    item = await database.fetch_one(query)
    return item

# Avoid - Sync (unless necessary)
@router.get("/items/{item_id}")
def get_item(item_id: int):
    item = db.query(Item).first()
    return item
```

### Database Connection Pooling

```python
# SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_size=20,          # Max connections in pool
    max_overflow=10,       # Extra connections if pool full
    pool_pre_ping=True,    # Verify connections
    pool_recycle=3600      # Recycle connections every hour
)
```

### Caching with Redis

```python
import redis
from functools import lru_cache

redis_client = redis.from_url(settings.REDIS_URL)

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    # Check cache
    cached = redis_client.get(f"item:{item_id}")
    if cached:
        return json.loads(cached)

    # Fetch from database
    item = await db.fetch_one(query)

    # Cache for 1 hour
    redis_client.setex(
        f"item:{item_id}",
        3600,
        json.dumps(item)
    )

    return item
```

### Response Models

```python
# Use response_model to filter and validate
@router.get("/users/", response_model=List[UserOut])
async def get_users():
    return await db.fetch_all(query)
```

### Gunicorn with Uvicorn Workers

```bash
# Install
pip install gunicorn

# Run with multiple workers
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Nginx Reverse Proxy

```nginx
# nginx.conf
upstream fastapi {
    server api:8000;
}

server {
    listen 80;
    server_name myapp.com;

    location / {
        proxy_pass http://fastapi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static {
        alias /app/static;
    }
}

# HTTPS (with Let's Encrypt)
server {
    listen 443 ssl;
    server_name myapp.com;

    ssl_certificate /etc/letsencrypt/live/myapp.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/myapp.com/privkey.pem;

    location / {
        proxy_pass http://fastapi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Database Migrations in Production

```bash
# Run migrations before starting app
alembic upgrade head

# In Dockerfile
CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000
```

## Best Practices

1. **Use Environment Variables**: Never hardcode secrets
2. **Enable HTTPS**: Use SSL/TLS certificates
3. **Set Workers**: Use multiple Uvicorn workers
4. **Connection Pooling**: Configure database pools properly
5. **Caching**: Use Redis for frequently accessed data
6. **Logging**: Comprehensive logging for debugging
7. **Health Checks**: Implement health check endpoints
8. **Rate Limiting**: Protect against abuse
9. **Monitoring**: Use tools like Prometheus, Grafana
10. **Backups**: Regular database backups
11. **Update Dependencies**: Keep packages up to date
12. **Security Headers**: Add security headers via middleware
