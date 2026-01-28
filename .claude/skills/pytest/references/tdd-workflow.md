# TDD Workflow Reference

Complete Test-Driven Development patterns for FastAPI applications.

## TDD Philosophy

TDD ka core principle: **Test likhne se pehle code mat likho**.

```
Before: Code → Test → Fix bugs
After:  Test → Code → Refactor → Repeat
```

## Complete TDD Cycle Examples

### Example 1: User Registration Feature

**Iteration 1: Basic User Creation**

```python
# RED: test_users.py
def test_create_user_returns_user_data():
    response = client.post("/users/", json={
        "email": "new@example.com",
        "password": "secret123"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"
    assert "id" in response.json()
    assert "password" not in response.json()  # Password exposed nahi hona chahiye
```

```bash
pytest test_users.py::test_create_user_returns_user_data -v
# ❌ FAIL - endpoint exists nahi
```

```python
# GREEN: main.py - Minimum code
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr

@app.post("/users/", status_code=201, response_model=UserResponse)
def create_user(user: UserCreate):
    return {"id": 1, "email": user.email}
```

```bash
pytest test_users.py::test_create_user_returns_user_data -v
# ✅ PASS
```

**Iteration 2: Duplicate Email Check**

```python
# RED: Add test for duplicate
def test_create_user_with_duplicate_email_returns_400():
    # First user
    client.post("/users/", json={"email": "dup@example.com", "password": "pass1"})
    # Duplicate attempt
    response = client.post("/users/", json={"email": "dup@example.com", "password": "pass2"})
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()
```

```python
# GREEN: Add duplicate check
users_db = {}

@app.post("/users/", status_code=201, response_model=UserResponse)
def create_user(user: UserCreate):
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="Email already exists")
    user_id = len(users_db) + 1
    users_db[user.email] = {"id": user_id, "email": user.email}
    return users_db[user.email]
```

**Iteration 3: Password Validation**

```python
# RED: Password validation test
@pytest.mark.parametrize("password,expected_status", [
    ("short", 422),           # Too short
    ("nouppercase1", 422),    # No uppercase
    ("NOLOWERCASE1", 422),    # No lowercase
    ("NoDigitsHere", 422),    # No digits
    ("ValidPass123", 201),    # Valid
])
def test_password_validation(password, expected_status):
    response = client.post("/users/", json={
        "email": f"test{password}@example.com",
        "password": password
    })
    assert response.status_code == expected_status
```

```python
# GREEN: Add validator
from pydantic import validator
import re

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain digit')
        return v
```

---

## Error-First Testing Pattern

**Test errors BEFORE happy path**. Ye ensure karta hai ki error handling solid hai.

```python
# Order: Error tests first, then success tests

# 1. Validation errors
def test_create_item_without_name_returns_422():
    response = client.post("/items/", json={})
    assert response.status_code == 422

def test_create_item_with_empty_name_returns_422():
    response = client.post("/items/", json={"name": ""})
    assert response.status_code == 422

# 2. Business logic errors
def test_create_item_with_duplicate_name_returns_400():
    client.post("/items/", json={"name": "Existing"})
    response = client.post("/items/", json={"name": "Existing"})
    assert response.status_code == 400

# 3. Authorization errors
def test_create_item_without_auth_returns_401():
    response = client.post("/items/", json={"name": "Test"})
    assert response.status_code == 401

# 4. Permission errors
def test_create_item_as_viewer_returns_403():
    response = client.post("/items/", json={"name": "Test"},
                          headers={"Authorization": "Bearer viewer_token"})
    assert response.status_code == 403

# 5. Finally: Happy path
def test_create_item_success():
    response = client.post("/items/", json={"name": "New Item"},
                          headers={"Authorization": "Bearer admin_token"})
    assert response.status_code == 201
```

---

## Incremental Feature Development

### Building a Search Feature Incrementally

**Step 1: Basic Search**
```python
def test_search_items_returns_matching_results():
    # Setup
    client.post("/items/", json={"name": "Python Book"})
    client.post("/items/", json={"name": "Java Guide"})

    # Test
    response = client.get("/items/?q=Python")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Python Book"
```

**Step 2: Case-Insensitive Search**
```python
def test_search_is_case_insensitive():
    client.post("/items/", json={"name": "Python Book"})

    response = client.get("/items/?q=python")  # lowercase
    assert len(response.json()) == 1
```

**Step 3: Pagination**
```python
def test_search_with_pagination():
    # Create 15 items
    for i in range(15):
        client.post("/items/", json={"name": f"Item {i}"})

    response = client.get("/items/?q=Item&page=1&limit=10")
    assert len(response.json()) == 10

    response = client.get("/items/?q=Item&page=2&limit=10")
    assert len(response.json()) == 5
```

**Step 4: Empty Results**
```python
def test_search_with_no_results_returns_empty_list():
    response = client.get("/items/?q=NonExistent")
    assert response.status_code == 200
    assert response.json() == []
```

---

## Refactoring Techniques with Test Safety

### Safe Refactoring Steps

1. **Ensure all tests pass** before refactoring
2. **Make one small change** at a time
3. **Run tests** after each change
4. **Commit** when tests pass

### Example: Extracting a Service Layer

**Before (Fat Controller)**
```python
@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Validation
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(400, "Email exists")

    # Hash password
    hashed = bcrypt.hash(user.password)

    # Create user
    db_user = User(email=user.email, password=hashed)
    db.add(db_user)
    db.commit()

    # Send welcome email
    send_email(user.email, "Welcome!")

    return db_user
```

**Refactoring Steps**

```python
# Step 1: Extract validation (tests should still pass)
def check_email_exists(db: Session, email: str) -> bool:
    return db.query(User).filter(User.email == email).first() is not None

# Run tests: pytest -v ✅

# Step 2: Extract password hashing
def hash_password(password: str) -> str:
    return bcrypt.hash(password)

# Run tests: pytest -v ✅

# Step 3: Create service class
class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserCreate) -> User:
        if check_email_exists(self.db, user.email):
            raise HTTPException(400, "Email exists")

        db_user = User(
            email=user.email,
            password=hash_password(user.password)
        )
        self.db.add(db_user)
        self.db.commit()
        return db_user

# Run tests: pytest -v ✅

# Step 4: Update endpoint to use service
@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    db_user = service.create_user(user)
    send_email(user.email, "Welcome!")
    return db_user

# Run tests: pytest -v ✅
```

---

## TDD Anti-Patterns to Avoid

### 1. Testing Implementation Details
```python
# ❌ BAD: Testing internal state
def test_user_password_is_hashed():
    user = create_user("test@example.com", "password")
    assert user._password_hash.startswith("$2b$")  # Testing bcrypt format

# ✅ GOOD: Testing behavior
def test_user_can_login_with_correct_password():
    create_user("test@example.com", "password")
    response = client.post("/login", json={
        "email": "test@example.com",
        "password": "password"
    })
    assert response.status_code == 200
```

### 2. Tests That Are Too Broad
```python
# ❌ BAD: Testing everything in one test
def test_user_crud():
    # Create
    response = client.post("/users/", json={"email": "test@example.com"})
    assert response.status_code == 201
    user_id = response.json()["id"]

    # Read
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200

    # Update
    response = client.put(f"/users/{user_id}", json={"name": "New Name"})
    assert response.status_code == 200

    # Delete
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 204

# ✅ GOOD: Separate focused tests
def test_create_user(): ...
def test_read_user(): ...
def test_update_user(): ...
def test_delete_user(): ...
```

### 3. Skipping the RED Phase
```python
# ❌ BAD: Writing code first, test after
# You wrote the endpoint, now writing test to "prove" it works

# ✅ GOOD: Test first, see it fail, then implement
# Test fails → Implement → Test passes → Refactor
```

### 4. Not Refactoring
```python
# ❌ BAD: Green phase mein ruk jana
# Test pass ho gaya, code messy hai but "it works"

# ✅ GOOD: Always refactor after GREEN
# Clean code, remove duplication, improve naming
```

---

## TDD Development Commands

```bash
# Watch mode - automatic test runs
pip install pytest-watch
ptw  # or: pytest-watch

# Run single test during development
pytest tests/test_users.py::test_create_user -v

# Run tests matching pattern
pytest -k "create_user" -v

# Run with output (print statements)
pytest -v -s

# Run failed tests only
pytest --lf  # last failed
pytest --ff  # failed first

# Coverage check
pytest --cov=app --cov-report=term-missing

# Stop on first failure (fast feedback)
pytest -x
```

---

## TDD Checklist

Before starting:
- [ ] Requirements clear hain?
- [ ] Test file create ki?
- [ ] Fixtures ready hain?

During RED phase:
- [ ] Test behavior describe karta hai (implementation nahi)?
- [ ] Test actually fail hota hai?
- [ ] Failure message clear hai?

During GREEN phase:
- [ ] Minimum code likhi hai?
- [ ] Test pass hota hai?
- [ ] Koi shortcut nahi liya?

During REFACTOR phase:
- [ ] Code clean hai?
- [ ] Duplication remove ki?
- [ ] Tests still pass hote hain?
- [ ] Commit kiya?
