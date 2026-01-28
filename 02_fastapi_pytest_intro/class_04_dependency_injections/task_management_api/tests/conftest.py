import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.db.database import get_session
from app.models.task import Task
from main import app


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_task_data():
    return {
        "title": "Complete project",
        "description": "Finish the task management API",
        "priority": "high",
    }


@pytest.fixture
def created_task(session: Session):
    task = Task(
        title="Existing task",
        description="Already in database",
        priority="medium",
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
