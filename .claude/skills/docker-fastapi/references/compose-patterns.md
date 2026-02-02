# Docker Compose Patterns for FastAPI

## Development Compose Files

### FastAPI Only (No Database)

```yaml
# docker-compose.dev.yml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      # Mount source code for hot-reload
      - .:/app
    environment:
      - PYTHONUNBUFFERED=1
```

**Run:** `docker-compose -f docker-compose.dev.yml up --build`

---

### FastAPI + PostgreSQL (Development)

```yaml
# docker-compose.dev.yml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/devdb
      - PYTHONUNBUFFERED=1
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=devdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

**Note:** `depends_on` with `condition: service_healthy` ensures PostgreSQL is ready before FastAPI starts.

---

### FastAPI + SQLite (Development)

```yaml
# docker-compose.dev.yml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - .:/app
      - sqlite_data:/app/data  # Persist SQLite database
    environment:
      - DATABASE_URL=sqlite:///./data/app.db
      - PYTHONUNBUFFERED=1

volumes:
  sqlite_data:
```

**Note:** SQLite file is stored in a volume so it persists across container restarts.

---

## Production Compose Files

### FastAPI + PostgreSQL (Production)

```yaml
# docker-compose.yml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
    env_file:
      - .env.production
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    # Don't expose port in production (only internal access)
    # ports:
    #   - "5432:5432"

volumes:
  postgres_data:
```

**.env.production file:**
```env
POSTGRES_USER=appuser
POSTGRES_PASSWORD=secure_password_here
POSTGRES_DB=production_db
```

---

### FastAPI + PostgreSQL + Redis (Production)

```yaml
# docker-compose.yml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379
    env_file:
      - .env.production
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:
```

---

## Environment Variables

### Option 1: Inline in compose file
```yaml
environment:
  - DATABASE_URL=postgresql://user:pass@db:5432/mydb
```

### Option 2: Reference .env file
```yaml
env_file:
  - .env
```

### Option 3: Variable substitution
```yaml
environment:
  - DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@db:5432/${DB_NAME}
```
Variables read from shell or `.env` file in same directory.

---

## Networking

By default, docker-compose creates a network for all services.

**Service names = hostnames:**
```yaml
services:
  api:
    environment:
      # "db" is the hostname for the database container
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb

  db:
    image: postgres:15
```

**Custom networks:**
```yaml
services:
  api:
    networks:
      - frontend
      - backend

  db:
    networks:
      - backend  # Not accessible from frontend

networks:
  frontend:
  backend:
```

---

## Volume Types

### Named Volume (Persistent data)
```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:  # Docker manages this
```

### Bind Mount (Development)
```yaml
volumes:
  - ./app:/app  # Host path : Container path
```

### Anonymous Volume (Temporary)
```yaml
volumes:
  - /app/node_modules  # Protects from bind mount override
```

---

## Compose File for Both Dev and Prod

Use `docker-compose.override.yml` for development-specific settings:

**docker-compose.yml (base):**
```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**docker-compose.override.yml (dev - auto-loaded):**
```yaml
services:
  api:
    build:
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
    environment:
      - DEBUG=1

  db:
    ports:
      - "5432:5432"  # Expose for local tools
```

**docker-compose.prod.yml (production):**
```yaml
services:
  api:
    restart: unless-stopped
    environment:
      - DEBUG=0

  db:
    restart: unless-stopped
```

**Usage:**
```bash
# Development (uses override automatically)
docker-compose up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Depends_on with Health Checks

**Old way (just ordering):**
```yaml
depends_on:
  - db  # Starts after db, but doesn't wait for db to be ready
```

**Better way (wait for healthy):**
```yaml
depends_on:
  db:
    condition: service_healthy
```

This requires a `healthcheck` on the dependency:
```yaml
db:
  image: postgres:15
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres"]
    interval: 5s
    timeout: 5s
    retries: 5
```
