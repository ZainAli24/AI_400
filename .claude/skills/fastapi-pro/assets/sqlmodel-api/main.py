from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

from app.db.database import create_db_and_tables
from app.api import tasks, users
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.

    STARTUP (before yield):
    - Create database tables
    - Initialize app.state with shared settings

    SHUTDOWN (after yield):
    - Cleanup resources
    """
    # ===== STARTUP =====
    print(f"[*] Starting {settings.APP_NAME}...")

    # Create database tables
    create_db_and_tables()

    # Store shared settings in app.state
    app.state.settings = {
        "app_name": settings.APP_NAME,
        "version": "1.0.0",
        "database": "connected",
    }

    yield

    # ===== SHUTDOWN =====
    print(f"[*] Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
)


# ===== MIDDLEWARE =====

# Custom timer middleware - adds X-Process-Time header
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f} sec"
    return response


# CORS Middleware
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"],
)


# ===== ROUTES =====

# Include routers
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])


@app.get("/")
def root():
    return {"message": "SQLModel API is running!", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/info")
def get_info():
    """Access app.state set during lifespan startup."""
    return app.state.settings


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
