# Middleware & Lifespan Events Guide

## Table of Contents
- Understanding Middleware
- Custom HTTP Middleware
- Middleware Execution Order
- CORS Middleware
- Other Built-in Middleware
- Lifespan Events
- app.state Usage
- Complete Examples

---

## Understanding Middleware

Middleware is code that runs **before** every request reaches the route and **after** every response leaves the route.

### Flow Diagram

```
Client Request
    ↓
Middleware (BEFORE - outer to inner)
    ↓
Route Handler
    ↓
Middleware (AFTER - inner to outer)
    ↓
Client Response
```

### Use Cases

- Request/Response logging
- Timing and performance monitoring
- Authentication checks
- Adding custom headers
- CORS handling
- Rate limiting
- Request modification

---

## Custom HTTP Middleware

### Basic Pattern

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.middleware("http")
async def my_middleware(request: Request, call_next):
    # BEFORE: Request processing
    print(f"Request: {request.method} {request.url.path}")

    # Pass to next middleware/route
    response = await call_next(request)

    # AFTER: Response processing
    print(f"Response: {response.status_code}")

    return response
```

### Key Components

| Component | Description |
|-----------|-------------|
| `request: Request` | Incoming HTTP request object |
| `call_next` | Function to pass request to next layer |
| `await call_next(request)` | Execute route and get response |
| `response` | Response object (can be modified) |

### Timer Middleware (Adding Headers)

```python
@app.middleware("http")
async def timer_middleware(request: Request, call_next):
    import time

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Add custom header to response
    response.headers["X-Process-Time"] = f"{process_time:.4f} sec"

    return response
```

### Request Logging Middleware

```python
from loguru import logger

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"→ {request.method} {request.url.path}")

    response = await call_next(request)

    logger.info(f"← {response.status_code} {request.url.path}")

    return response
```

### Authentication Check Middleware

```python
from fastapi.responses import JSONResponse

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Skip auth for certain paths
    if request.url.path in ["/", "/health", "/docs", "/openapi.json"]:
        return await call_next(request)

    # Check for API key
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key != "valid-key":
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid API Key"}
        )

    return await call_next(request)
```

---

## Middleware Execution Order

### Critical Rule

Middlewares execute in **reverse order** of definition:
- Last defined = Outermost (runs first on request, last on response)
- First defined = Innermost (runs last on request, first on response)

### Example

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.middleware("http")
async def middleware_a(request: Request, call_next):
    print("[A] Before request")
    response = await call_next(request)
    print("[A] After response")
    return response

@app.middleware("http")
async def middleware_b(request: Request, call_next):
    print("[B] Before request")
    response = await call_next(request)
    print("[B] After response")
    return response

@app.middleware("http")
async def middleware_c(request: Request, call_next):
    print("[C] Before request")
    response = await call_next(request)
    print("[C] After response")
    return response

@app.get("/test")
def test():
    print("[Route] Executing")
    return {"message": "Hello"}
```

### Output Order

```
[C] Before request    # C runs first (last defined = outermost)
[B] Before request
[A] Before request
[Route] Executing
[A] After response    # A completes first (innermost)
[B] After response
[C] After response    # C completes last (outermost)
```

### Visual Stack

```
Request → [C] → [B] → [A] → [Route] → [A] → [B] → [C] → Response
          outer       inner          inner       outer
```

---

## CORS Middleware

Cross-Origin Resource Sharing allows frontend apps on different domains to access your API.

### Basic Setup

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Complete Configuration

```python
origins = [
    "http://localhost:3000",      # React dev server
    "http://localhost:8080",      # Vue dev server
    "https://myapp.com",          # Production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,       # Allow cookies/auth headers
    allow_methods=["*"],          # Allow all HTTP methods
    allow_headers=["*"],          # Allow all headers
    expose_headers=[              # Headers browser JS can access
        "X-Process-Time",
        "X-Request-ID",
        "Content-Disposition",
    ],
    max_age=600,                  # Cache preflight for 10 minutes
)
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `allow_origins` | List of allowed origins | `[]` |
| `allow_credentials` | Allow cookies/auth | `False` |
| `allow_methods` | Allowed HTTP methods | `["GET"]` |
| `allow_headers` | Allowed request headers | `[]` |
| `expose_headers` | Headers browser can read | `[]` |
| `max_age` | Preflight cache time (seconds) | `600` |

### Important Rules

1. **Credentials + Wildcard**: If `allow_credentials=True`, you CANNOT use `["*"]` for `allow_origins`
   ```python
   # ❌ WRONG - Will fail
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_credentials=True,
   )

   # ✅ CORRECT - List specific origins
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_credentials=True,
   )
   ```

2. **expose_headers**: Custom response headers are hidden from browser JS by default. Use `expose_headers` to make them accessible.

---

## Other Built-in Middleware

### TrustedHostMiddleware

Protects against HTTP Host header attacks:

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com"]
)
```

### GZipMiddleware

Compress responses for faster transfer:

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000  # Only compress if > 1000 bytes
)
```

### HTTPSRedirectMiddleware

Force HTTPS in production:

```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
```

### Middleware Order for Production

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()

# Order matters! Add in reverse order of execution:
# 1. GZip (runs last, compresses final response)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 2. CORS (handles preflight, adds headers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. TrustedHost (runs first, validates host)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["myapp.com", "*.myapp.com"]
)
```

---

## Lifespan Events

Modern way to handle application startup and shutdown logic.

### Basic Pattern

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ========== STARTUP ==========
    # Runs BEFORE app starts accepting requests
    print("Starting up...")

    yield  # App runs here, handles requests

    # ========== SHUTDOWN ==========
    # Runs WHEN app is stopping
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)
```

### Lifespan with Resources

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Fake ML model for example
ml_models = {}

def load_model():
    return {"predict": lambda x: x * 42}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load expensive resources
    print("Loading ML model...")
    ml_models["predictor"] = load_model()

    yield

    # Shutdown: Clean up resources
    print("Unloading ML model...")
    ml_models.clear()

app = FastAPI(lifespan=lifespan)

@app.get("/predict/{value}")
def predict(value: float):
    result = ml_models["predictor"]["predict"](value)
    return {"result": result}
```

### Lifespan with Database

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine

engine = create_engine("sqlite:///./app.db")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    SQLModel.metadata.create_all(engine)
    print("Database tables created")

    yield

    # Shutdown: Optional cleanup
    print("Database connection closed")

app = FastAPI(lifespan=lifespan)
```

---

## app.state Usage

`app.state` is a shared storage accessible throughout the application.

### Setting State in Lifespan

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Store configuration
    app.state.settings = {
        "app_name": "My FastAPI App",
        "version": "1.0.0",
        "debug": True
    }

    # Store database pool
    app.state.db_pool = await create_db_pool()

    # Store cache client
    app.state.redis = await aioredis.from_url("redis://localhost")

    yield

    # Cleanup
    await app.state.db_pool.close()
    await app.state.redis.close()

app = FastAPI(lifespan=lifespan)
```

### Accessing State in Routes

```python
from fastapi import Request

@app.get("/info")
def get_info(request: Request):
    # Access via request.app.state
    return {
        "app_name": request.app.state.settings["app_name"],
        "version": request.app.state.settings["version"]
    }

@app.get("/data")
async def get_data(request: Request):
    # Use shared database pool
    async with request.app.state.db_pool.acquire() as conn:
        result = await conn.fetch("SELECT * FROM items")
    return result
```

### Direct Access (Without Request)

```python
@app.get("/version")
def get_version():
    # Direct access when app is in scope
    return {"version": app.state.settings["version"]}
```

---

## Deprecated Patterns

### DO NOT USE: @app.on_event

```python
# ❌ DEPRECATED - Don't use these patterns:

@app.on_event("startup")
async def startup_event():
    print("Starting up...")

@app.on_event("shutdown")
def shutdown_event():
    print("Shutting down...")
```

### Why Deprecated?

1. Cannot share state between startup and shutdown easily
2. No proper resource cleanup guarantee
3. `lifespan` is the modern, recommended approach

### Migration Example

```python
# ❌ OLD WAY (deprecated)
app = FastAPI()
db_connection = None

@app.on_event("startup")
async def startup():
    global db_connection
    db_connection = await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await db_connection.close()


# ✅ NEW WAY (recommended)
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = await connect_db()
    yield
    await app.state.db.close()

app = FastAPI(lifespan=lifespan)
```

### Warning

If you provide a `lifespan` parameter, `@app.on_event("startup")` and `@app.on_event("shutdown")` handlers will **NOT be called**.

---

## Complete Examples

### Production-Ready Main File

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time

from app.core.config import settings
from app.db.database import create_db_and_tables, close_db_connections
from app.api import items, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ===== STARTUP =====
    print(f"Starting {settings.APP_NAME}...")

    # Initialize database
    create_db_and_tables()

    # Store shared config
    app.state.settings = {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG
    }

    yield

    # ===== SHUTDOWN =====
    print(f"Shutting down {settings.APP_NAME}...")
    await close_db_connections()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)


# ===== MIDDLEWARE (reverse order of execution) =====

# Custom timer middleware
@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.time() - start:.4f}"
    return response

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"],
)

# Trusted hosts (production)
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )


# ===== ROUTES =====
app.include_router(items.router, prefix="/api/v1/items", tags=["items"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])


@app.get("/")
def root():
    return {"message": f"Welcome to {app.state.settings['app_name']}"}


@app.get("/health")
def health():
    return {"status": "healthy", "version": app.state.settings["version"]}
```

### Middleware-Only Example

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS with expose_headers
origins = ["http://localhost:3000", "http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-Request-ID"],
)


# Multiple custom middlewares
@app.middleware("http")
async def middleware_a(request: Request, call_next):
    print(f"[A] Before: {request.method} {request.url.path}")
    response = await call_next(request)
    print(f"[A] After: {response.status_code}")
    return response


@app.middleware("http")
async def middleware_b(request: Request, call_next):
    print(f"[B] Before: {request.method} {request.url.path}")
    response = await call_next(request)
    print(f"[B] After: {response.status_code}")
    return response


@app.middleware("http")
async def timer_middleware(request: Request, call_next):
    import time
    start = time.time()
    response = await call_next(request)
    process_time = f"{time.time() - start:.4f} sec"
    response.headers["X-Process-Time"] = process_time
    return response


@app.get("/hello")
def hello():
    return {"message": "Hello World"}
```

### Lifespan-Only Example

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("[*] Starting up...")
    app.state.settings = {
        "app_name": "FastAPI with Lifespan Events",
        "version": "1.0.0"
    }

    yield

    # Shutdown
    print("[*] Shutting down...")


app = FastAPI(lifespan=lifespan)


@app.get("/data")
def get_data():
    return {
        "app_name": app.state.settings["app_name"],
        "version": app.state.settings["version"]
    }


@app.get("/goodbye")
def goodbye():
    return {"message": "Goodbye World"}
```

---

## Quick Reference

### Middleware Cheatsheet

```python
# Custom middleware
@app.middleware("http")
async def my_middleware(request: Request, call_next):
    # Before
    response = await call_next(request)
    # After
    return response

# CORS
app.add_middleware(CORSMiddleware, allow_origins=[...], ...)

# Trusted hosts
app.add_middleware(TrustedHostMiddleware, allowed_hosts=[...])

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### Lifespan Cheatsheet

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code here
    app.state.key = value
    yield
    # Shutdown code here

app = FastAPI(lifespan=lifespan)

# Access state in routes
@app.get("/")
def route(request: Request):
    return request.app.state.key
```
