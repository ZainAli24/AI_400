"""
SQLModel Structured App Example
Production-ready FastAPI + SQLModel project structure.

Run with: fastapi dev main.py
Docs at: http://localhost:8000/docs
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.database import create_tables
from app.api import tasks_router, users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables on startup"""
    create_tables()
    yield


app = FastAPI(
    title="Task Manager API",
    description="Task management with users and tasks",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Task Manager API",
        "docs": "/docs",
        "health": "/health"
    }
