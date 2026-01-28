from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db.database import create_tables
from app.api.tasks import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="Task Management API",
    description="A simple task management API with CRUD operations",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(tasks_router, prefix="/api/v1")
