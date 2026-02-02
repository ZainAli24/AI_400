# Docker Core Concepts

## What Problem Does Docker Solve?

**The "Works on My Machine" Problem:**
```
Developer A: "The app works fine on my laptop"
Developer B: "It crashes on mine - different Python version"
Server: "Missing dependencies, won't start"
```

**Docker Solution:**
Package your app + ALL its dependencies (Python, libraries, OS tools) into a single "container" that runs identically everywhere.

---

## Key Concepts

### 1. Image vs Container

| Image | Container |
|-------|-----------|
| Blueprint/Recipe | Running instance |
| Like a Python class | Like an object |
| Read-only | Can write to its own layer |
| Stored on disk | Runs in memory |
| Built from Dockerfile | Created from image |

```
# Python analogy
class FastAPIApp:        # Image
    def __init__(self):
        self.setup()

app1 = FastAPIApp()      # Container 1
app2 = FastAPIApp()      # Container 2 (independent)
```

### 2. Dockerfile

A text file with instructions to build an image. Each instruction creates a **layer**.

```dockerfile
# Each line = one layer
FROM python:3.12-slim    # Layer 1: Base OS + Python
WORKDIR /app             # Layer 2: Set working directory
COPY requirements.txt .  # Layer 3: Copy requirements
RUN pip install -r ...   # Layer 4: Install dependencies
COPY . .                 # Layer 5: Copy app code
CMD ["uvicorn", ...]     # Not a layer - just the start command
```

### 3. Layers and Caching

Docker caches each layer. If nothing changed, it reuses the cache.

**Why requirements.txt is copied before app code:**
```dockerfile
COPY requirements.txt .   # Changes rarely
RUN pip install -r ...    # Cached if requirements unchanged
COPY . .                  # Changes often - only this rebuilds
```

If you copied everything first, changing ANY file would reinstall all packages!

### 4. Volumes

Containers are **ephemeral** - data is lost when container stops.
Volumes persist data outside the container.

```yaml
# docker-compose.yml
volumes:
  - postgres_data:/var/lib/postgresql/data  # Named volume (persistent)
  - ./app:/app                               # Bind mount (dev hot-reload)
```

| Volume Type | Use Case |
|-------------|----------|
| Named volume | Database data, persistent storage |
| Bind mount | Development (live code changes) |

### 5. Port Mapping

Containers have their own network. Port mapping connects them to your computer.

```yaml
ports:
  - "8000:8000"   # host_port:container_port
```

```
Your browser → localhost:8000 → Container's port 8000 → FastAPI
```

### 6. Networks

Containers can talk to each other by service name (not localhost).

```yaml
services:
  api:
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/mydb  # "db" = service name

  db:
    image: postgres:15
```

Inside the `api` container, `db` resolves to the PostgreSQL container's IP.

---

## Visual Mental Model

```
┌─────────────────────────────────────────────────────────┐
│                    Your Computer                         │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Docker Engine                       │   │
│  │                                                  │   │
│  │  ┌──────────────┐    ┌──────────────┐          │   │
│  │  │  Container 1 │    │  Container 2 │          │   │
│  │  │  (FastAPI)   │◄──►│  (PostgreSQL)│          │   │
│  │  │  Port: 8000  │    │  Port: 5432  │          │   │
│  │  └──────────────┘    └──────────────┘          │   │
│  │         ▲                   │                   │   │
│  │         │                   │                   │   │
│  │  ┌──────┴──────┐     ┌─────┴─────┐            │   │
│  │  │ Volume:     │     │ Volume:    │            │   │
│  │  │ ./app:/app  │     │ pg_data    │            │   │
│  │  │ (your code) │     │ (database) │            │   │
│  │  └─────────────┘     └───────────┘            │   │
│  └─────────────────────────────────────────────────┘   │
│         ▲                                               │
│         │ Port mapping 8000:8000                       │
│         │                                               │
│  ┌──────┴───────┐                                      │
│  │   Browser    │                                      │
│  │ localhost:8000                                      │
│  └──────────────┘                                      │
└─────────────────────────────────────────────────────────┘
```

---

## Common Docker Objects

| Object | Command | Example |
|--------|---------|---------|
| Image | `docker images` | `python:3.12-slim`, `postgres:15` |
| Container | `docker ps` | Running instances |
| Volume | `docker volume ls` | `postgres_data` |
| Network | `docker network ls` | `myapp_default` |

---

## Docker vs docker-compose

| docker | docker-compose |
|--------|----------------|
| Single container | Multiple containers |
| Manual networking | Automatic networking |
| Long commands | YAML config file |
| `docker run ...` | `docker-compose up` |

**Use docker-compose** for anything beyond a single container (which is most real apps).

---

## FastAPI-Specific Concepts

### Uvicorn Workers
- Development: 1 worker with reload
- Production: Multiple workers (2 × CPU cores + 1)

```dockerfile
# Development
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0"]

# Production
CMD ["uvicorn", "main:app", "--workers", "4", "--host", "0.0.0.0"]
```

### ASGI vs WSGI
- FastAPI uses **ASGI** (Async Server Gateway Interface)
- Uvicorn is an ASGI server
- Gunicorn can manage Uvicorn workers in production

```dockerfile
# Production with Gunicorn managing Uvicorn
CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "4"]
```
