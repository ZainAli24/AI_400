import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from user_manag import app, get_session, User, hash_password


TEST_DATABASE_URL = "sqlite://"


@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app, raise_server_exceptions=True)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def normal_user(session):
    user = User(
        name="Test User",
        email="test@gmail.com",
        password=hash_password("test123"),
        role="user",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def admin_user(session):
    user = User(
        name="Admin User",
        email="admin@gmail.com",
        password=hash_password("admin123"),
        role="admin",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def user_token(client, normal_user):
    response = client.post("/login", json={"email": "test@gmail.com", "password": "test123"})
    return response.json()["access_token"]


@pytest.fixture
def admin_token(client, admin_user):
    response = client.post("/login", json={"email": "admin@gmail.com", "password": "admin123"})
    return response.json()["access_token"]


@pytest.fixture
def user_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
