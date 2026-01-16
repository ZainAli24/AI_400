# Complete FastAPI + Pytest Examples

## Example 1: Simple CRUD API Testing

### Application Code (main.py)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Item(BaseModel):
    id: int
    name: str
    price: float

items_db = {}
item_counter = 1

@app.post("/items/", response_model=Item, status_code=201)
def create_item(name: str, price: float):
    global item_counter
    item = Item(id=item_counter, name=name, price=price)
    items_db[item_counter] = item
    item_counter += 1
    return item

@app.get("/items/", response_model=List[Item])
def read_items():
    return list(items_db.values())

@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, name: str, price: float):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    item = Item(id=item_id, name=name, price=price)
    items_db[item_id] = item
    return item

@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
```

### Test Code (test_items.py)

```python
import pytest
from fastapi.testclient import TestClient
from main import app, items_db, item_counter

@pytest.fixture(autouse=True)
def reset_db():
    items_db.clear()
    global item_counter
    item_counter = 1
    yield

@pytest.fixture
def client():
    return TestClient(app)

def test_create_item(client):
    response = client.post("/items/?name=Widget&price=9.99")
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Widget"
    assert data["price"] == 9.99
    assert "id" in data

def test_read_items_empty(client):
    response = client.get("/items/")
    assert response.status_code == 200
    assert response.json() == []

def test_read_items(client):
    client.post("/items/?name=Item1&price=10")
    client.post("/items/?name=Item2&price=20")

    response = client.get("/items/")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_read_item(client):
    create_response = client.post("/items/?name=Test&price=5.00")
    item_id = create_response.json()["id"]

    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test"

def test_read_item_not_found(client):
    response = client.get("/items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

def test_update_item(client):
    create_response = client.post("/items/?name=Old&price=5.00")
    item_id = create_response.json()["id"]

    response = client.put(f"/items/{item_id}?name=New&price=10.00")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New"
    assert data["price"] == 10.00

def test_update_item_not_found(client):
    response = client.put("/items/999?name=New&price=10")
    assert response.status_code == 404

def test_delete_item(client):
    create_response = client.post("/items/?name=Delete&price=1.00")
    item_id = create_response.json()["id"]

    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 204

    # Verify deletion
    get_response = client.get(f"/items/{item_id}")
    assert get_response.status_code == 404

def test_delete_item_not_found(client):
    response = client.delete("/items/999")
    assert response.status_code == 404
```

## Example 2: Database Testing with SQLAlchemy

### Application Code

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

```python
# models.py
from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String)
```

```python
# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, engine, Base
from models import User
from pydantic import BaseModel

Base.metadata.create_all(bind=engine)

app = FastAPI()

class UserCreate(BaseModel):
    email: str
    username: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str

    class Config:
        from_attributes = True

@app.post("/users/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(email=user.email, username=user.username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### Test Code (conftest.py)

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from database import Base, get_db
from main import app

TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="function")
def test_db():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
```

### Test Code (test_users.py)

```python
def test_create_user(client):
    response = client.post(
        "/users/",
        json={"email": "test@example.com", "username": "testuser"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data

def test_create_duplicate_user(client):
    user_data = {"email": "test@example.com", "username": "testuser"}

    # Create first user
    response1 = client.post("/users/", json=user_data)
    assert response1.status_code == 201

    # Try to create duplicate
    response2 = client.post("/users/", json=user_data)
    assert response2.status_code == 400
    assert "already registered" in response2.json()["detail"]

def test_read_user(client):
    # Create user
    create_response = client.post(
        "/users/",
        json={"email": "test@example.com", "username": "testuser"}
    )
    user_id = create_response.json()["id"]

    # Read user
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_read_user_not_found(client):
    response = client.get("/users/999")
    assert response.status_code == 404
```

## Example 3: Authentication Testing

### Application Code

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt

app = FastAPI()

SECRET_KEY = "test-secret-key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

fake_users_db = {
    "testuser": {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "fakehashedpassword",
    }
}

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    email: str

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username not in fake_users_db:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return fake_users_db[username]

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or user["hashed_password"] != f"fakehashed{form_data.password}":
        raise HTTPException(status_code=400, detail="Incorrect credentials")

    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
def read_users_me(current_user: dict = Depends(get_current_user)):
    return User(**current_user)
```

### Test Code

```python
import pytest
from fastapi.testclient import TestClient
from main import app, fake_users_db, create_access_token

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_token():
    return create_access_token(data={"sub": "testuser"})

def test_login_success(client):
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "password"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "wrong"}
    )
    assert response.status_code == 400

def test_login_wrong_username(client):
    response = client.post(
        "/token",
        data={"username": "wronguser", "password": "password"}
    )
    assert response.status_code == 400

def test_read_current_user(client, auth_token):
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"

def test_read_current_user_no_token(client):
    response = client.get("/users/me")
    assert response.status_code == 401

def test_read_current_user_invalid_token(client):
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401
```

## Example 4: Parametrized Testing

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.mark.parametrize("email,username,expected_status", [
    ("valid@example.com", "validuser", 201),
    ("invalid-email", "user", 422),
    ("", "user", 422),
    ("test@example.com", "", 422),
    ("test@example.com", "a" * 100, 201),  # Long username
])
def test_create_user_validation(email, username, expected_status):
    response = client.post(
        "/users/",
        json={"email": email, "username": username}
    )
    assert response.status_code == expected_status

@pytest.mark.parametrize("item_id,expected_status", [
    (1, 200),
    (999, 404),
    (-1, 404),
    (0, 404),
])
def test_read_item_various_ids(client, item_id, expected_status):
    # Setup: Create item with id=1
    client.post("/items/", json={"name": "Test", "price": 10})

    response = client.get(f"/items/{item_id}")
    assert response.status_code == expected_status
```

## Example 5: Async Testing

```python
# main.py
from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get("/async-items/")
async def read_async_items():
    await asyncio.sleep(0.1)  # Simulate async operation
    return [{"id": 1, "name": "Item 1"}]

@app.get("/async-slow/")
async def slow_endpoint():
    await asyncio.sleep(2)
    return {"status": "done"}
```

```python
# test_async.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_async_items():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/async-items/")
    assert response.status_code == 200
    assert len(response.json()) == 1

@pytest.mark.asyncio
async def test_slow_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/async-slow/")
    assert response.status_code == 200
    assert response.json()["status"] == "done"
```

## Running the Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_users.py

# Run specific test function
pytest tests/test_users.py::test_create_user

# Run tests matching pattern
pytest -k "create"

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x

# Run only async tests
pytest -m asyncio
```
