# Dockerfile Patterns for FastAPI

## Development Dockerfile

Optimized for fast iteration with hot-reload.

### Simple Project (main.py in root)

```dockerfile
# Dockerfile.dev
FROM python:3.12-slim

# Prevents Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1
# Prevents .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Don't copy code - mounted as volume for hot-reload
# COPY . .  # Commented out - use volume mount instead

EXPOSE 8000

# --reload enables hot-reload when files change
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### Structured Project (app/ folder)

```dockerfile
# Dockerfile.dev
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Note: app.main:app (module path)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

---

## Production Dockerfile

Optimized for security, size, and performance.

### Simple Project - Production

```dockerfile
# Dockerfile
FROM python:3.12-slim AS builder

WORKDIR /app

# Install dependencies in builder stage
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Final stage ---
FROM python:3.12-slim

# Security: Run as non-root user
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Production: Multiple workers, no reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Structured Project - Production (Multi-stage)

```dockerfile
# Dockerfile
# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Stage 2: Production
FROM python:3.12-slim

# Security: Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages from wheels
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copy application
COPY --chown=appuser:appuser ./app ./app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## Production with Gunicorn (Recommended)

For production, Gunicorn manages Uvicorn workers:

```dockerfile
# Dockerfile
FROM python:3.12-slim

RUN useradd --create-home appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

# Gunicorn with Uvicorn workers
# -w: workers (2 * CPU + 1)
# -k: worker class
# --timeout: worker timeout
CMD ["gunicorn", "main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-w", "4", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

---

## .dockerignore

Essential for security and smaller builds.

```dockerignore
# .dockerignore

# Git
.git
.gitignore

# Python
__pycache__
*.py[cod]
*$py.class
*.so
.Python
.env
.venv
env/
venv/
ENV/

# Testing
.pytest_cache
.coverage
htmlcov/
.tox

# IDEs
.idea/
.vscode/
*.swp
*.swo

# Docker
Dockerfile*
docker-compose*
.docker

# Documentation
*.md
docs/

# OS
.DS_Store
Thumbs.db

# Secrets (IMPORTANT!)
*.pem
*.key
.env*
secrets/
```

---

## Pattern Comparison

| Aspect | Development | Production |
|--------|-------------|------------|
| Base image | `python:3.12-slim` | Multi-stage build |
| Code | Volume mounted | Copied into image |
| Reload | `--reload` enabled | No reload |
| Workers | 1 | 4+ (2 × CPU + 1) |
| User | root (convenient) | Non-root (secure) |
| Health check | Optional | Required |
| Image size | Larger (dev tools) | Minimal |

---

## Layer Caching Best Practices

### Do This (Efficient):
```dockerfile
# Dependencies change rarely - cached
COPY requirements.txt .
RUN pip install -r requirements.txt

# Code changes often - only this rebuilds
COPY . .
```

### Don't Do This (Slow):
```dockerfile
# Any code change invalidates pip install cache!
COPY . .
RUN pip install -r requirements.txt
```

---

## Health Check Endpoint

Add this to your FastAPI app for production health checks:

```python
# main.py or app/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

This endpoint is used by:
- Docker HEALTHCHECK
- Load balancers
- Kubernetes probes
- Monitoring systems
