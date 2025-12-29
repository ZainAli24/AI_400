---
name: fastapi-pro
description: "Comprehensive FastAPI development skill for building production-ready APIs from hello world to professional applications. Use when creating FastAPI projects, REST APIs, microservices, or when user asks for Python web API development. Covers (1) Simple hello-world apps, (2) Structured applications, (3) CRUD APIs with databases (SQLAlchemy, MongoDB, Prisma), (4) Authentication with JWT/OAuth2, (5) Microservices with background tasks, (6) Docker deployment, (7) Testing with pytest. Trigger on requests like create FastAPI app, build REST API, add authentication, setup database, or deploy FastAPI."
---

# FastAPI Pro

Build FastAPI applications from simple hello-world examples to production-ready microservices.

## Quick Start Templates

Use these templates based on project requirements:

### 1. Hello World (`assets/hello-world/`)
**When to use:** Learning FastAPI, quick prototypes, simple single-file APIs

**Contains:**
- Single `main.py` with basic CRUD endpoints
- Path parameters and query parameters examples
- Request body with Pydantic models

**Setup:**
```bash
cp -r assets/hello-world/* ./
pip install -r requirements.txt
fastapi dev main.py
```

### 2. Structured App (`assets/structured-app/`)
**When to use:** Growing projects that need organization, multi-developer teams

**Structure:**
```
app/
├── api/routes/     # Endpoint routers
├── core/           # Config and settings
├── models/         # Pydantic models
└── schemas/        # Database schemas (optional)
```

**Setup:**
```bash
cp -r assets/structured-app/* ./
pip install -r requirements.txt
python main.py
```

### 3. CRUD API with Database (`assets/crud-api/`)
**When to use:** Data-driven applications, user management, content systems

**Features:**
- SQLAlchemy ORM integration
- Complete CRUD operations
- Database models and Pydantic schemas
- Session management with dependency injection

**Setup:**
```bash
cp -r assets/crud-api/* ./
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your DATABASE_URL
python main.py
```

**Database options:** See [references/databases.md](references/databases.md) for MongoDB, Prisma, or other databases.

### 4. Auth API with JWT (`assets/auth-api/`)
**When to use:** User authentication, protected endpoints, secure APIs

**Features:**
- JWT token authentication
- User registration and login
- Password hashing with bcrypt
- Protected routes with OAuth2
- Token-based authorization

**Setup:**
```bash
cp -r assets/auth-api/* ./
pip install -r requirements.txt
cp .env.example .env
# IMPORTANT: Change SECRET_KEY in .env
python main.py
```

**Endpoints:**
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token
- `GET /api/v1/auth/me` - Get current user (protected)

**Advanced auth:** See [references/authentication.md](references/authentication.md) for OAuth2, RBAC, API keys.

### 5. Microservice with Background Tasks (`assets/microservice/`)
**When to use:** Async operations, email sending, data processing, job queues

**Features:**
- FastAPI BackgroundTasks for simple async work
- Celery integration setup for complex jobs
- Job status tracking
- Email and data processing examples

**Setup:**
```bash
cp -r assets/microservice/* ./
pip install -r requirements.txt
python main.py

# For Celery (optional):
# pip install celery redis
# celery -A app.tasks.celery_tasks worker --loglevel=info
```

## Workflow for New Projects

### Step 1: Choose Template
Select the template closest to project needs. Start simple, migrate to structured as needed.

### Step 2: Copy Template
```bash
cp -r assets/<template-name>/* ./project-name/
cd project-name
```

### Step 3: Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
cp .env.example .env
# Edit .env with actual values
```

### Step 5: Run Application
```bash
# Development
fastapi dev main.py

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Step 6: Access Documentation
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## Database Integration

### Quick Start with SQLAlchemy
Already included in `crud-api` template. For custom setup:

1. Install: `pip install sqlalchemy`
2. Configure DATABASE_URL in `.env`
3. See [references/databases.md](references/databases.md) for complete patterns

### MongoDB
See [references/databases.md](references/databases.md) for Motor and Beanie ODM setup.

### Prisma
See [references/databases.md](references/databases.md) for Prisma setup and usage.

## Authentication

### Adding JWT Authentication
Use `auth-api` template or see [references/authentication.md](references/authentication.md) for:
- Complete JWT implementation
- OAuth2 password flow
- Role-based access control (RBAC)
- API key authentication
- Refresh tokens
- Password reset flow

### Quick Auth Setup
```python
from app.core.security import create_access_token, verify_password
from app.api.auth import get_current_user

# Protect endpoint
@router.get("/protected")
def protected_route(current_user = Depends(get_current_user)):
    return {"user": current_user.username}
```

## Testing

### Setup Testing
```bash
pip install pytest pytest-asyncio httpx
```

Create `tests/` directory with `conftest.py` and test files. See [references/testing.md](references/testing.md) for:
- Complete pytest setup
- Testing endpoints (GET, POST, PUT, DELETE)
- Testing with database fixtures
- Testing authentication
- Mocking dependencies
- Coverage reports

### Quick Test Example
```python
def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
```

## Deployment

### Docker Deployment
Docker files available in `assets/docker/`:
- `Dockerfile` - Production-ready image
- `docker-compose.yml` - Multi-container setup with PostgreSQL and Redis
- `.dockerignore` - Exclude unnecessary files

**Quick Docker Setup:**
```bash
# Copy Docker files to project
cp assets/docker/* ./

# Build and run
docker-compose up -d

# View logs
docker-compose logs -f api
```

See [references/deployment.md](references/deployment.md) for:
- Production configuration
- Environment variables
- Logging and monitoring
- Performance optimization
- Nginx reverse proxy
- HTTPS setup
- Gunicorn with multiple workers

## Common Tasks

### Add New Endpoint
```python
# app/api/new_router.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/new-endpoint")
def new_endpoint():
    return {"message": "New endpoint"}

# main.py
from app.api import new_router
app.include_router(new_router.router, prefix="/api/v1", tags=["new"])
```

### Add Database Model
```python
# app/models/product.py
from sqlalchemy import Column, Integer, String
from app.db.database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)
```

### Add Background Task
```python
from fastapi import BackgroundTasks

def send_email(email: str):
    # Email logic
    pass

@router.post("/send")
def send_notification(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, "user@example.com")
    return {"message": "Email will be sent"}
```

## Reference Documentation

Detailed guides available when needed:

- **[databases.md](references/databases.md)** - SQLAlchemy, MongoDB, Prisma patterns and migrations
- **[authentication.md](references/authentication.md)** - JWT, OAuth2, RBAC, API keys, security best practices
- **[testing.md](references/testing.md)** - pytest setup, fixtures, mocking, coverage
- **[deployment.md](references/deployment.md)** - Docker, production config, monitoring, performance

## Best Practices

1. **Start Simple**: Use hello-world for learning, migrate to structured as needed
2. **Environment Variables**: Always use `.env` files, never hardcode secrets
3. **Type Hints**: Use Pydantic models for validation and documentation
4. **Async/Await**: Use async for I/O operations (database, external APIs)
5. **Dependency Injection**: Use `Depends()` for database sessions, auth
6. **Error Handling**: Use HTTPException with appropriate status codes
7. **Documentation**: FastAPI auto-generates docs, keep Pydantic models descriptive
8. **Testing**: Write tests before deploying to production
9. **Security**: Hash passwords, use HTTPS, validate inputs
10. **Monitoring**: Add logging and health check endpoints

## Project Structure Example

```
my-fastapi-project/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── items.py
│   │   └── users.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   └── database.py
│   ├── models/
│   │   ├── item.py
│   │   └── user.py
│   └── schemas/
│       ├── item.py
│       └── user.py
├── tests/
│   ├── conftest.py
│   └── test_api.py
├── .env
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── main.py
└── requirements.txt
```

## Quick Command Reference

```bash
# Development
fastapi dev main.py

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# With Gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# Docker
docker-compose up -d

# Tests
pytest
pytest --cov=app

# Generate secret key
openssl rand -hex 32
```

## Troubleshooting

**Module not found errors:**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**Database connection errors:**
- Check DATABASE_URL in `.env`
- Ensure database server is running
- Verify credentials

**Import errors:**
- Add `__init__.py` files in all directories
- Use absolute imports: `from app.models import User`

**Port already in use:**
- Change PORT in `.env` or use different port: `--port 8001`

## Next Steps

1. **Start with a template** that matches your use case
2. **Run the app** and test the auto-generated docs at `/docs`
3. **Add your endpoints** following the existing patterns
4. **Read reference docs** for advanced features
5. **Write tests** before deployment
6. **Deploy with Docker** using provided configuration
