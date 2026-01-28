# Security Testing Reference

Comprehensive security testing patterns for FastAPI applications based on OWASP Top 10.

## SQL Injection Testing

### Basic SQL Injection Tests

```python
import pytest

# SQL Injection payloads to test
SQL_INJECTION_PAYLOADS = [
    "'; DROP TABLE users; --",
    "' OR '1'='1",
    "' OR '1'='1' --",
    "' UNION SELECT * FROM users --",
    "1; DELETE FROM users",
    "' OR 1=1 --",
    "admin'--",
    "1' OR '1' = '1",
]

@pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS)
def test_login_sql_injection(client, payload):
    """SQL injection attempt should not bypass authentication"""
    response = client.post("/login", json={
        "email": payload,
        "password": payload
    })
    # Should return 401 (not authenticated) or 422 (validation error)
    # Should NOT return 200 (successful login)
    assert response.status_code in [401, 422]
    assert "token" not in response.json()


@pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS)
def test_search_sql_injection(client, auth_headers, payload):
    """Search should handle SQL injection safely"""
    response = client.get(f"/items/?q={payload}", headers=auth_headers)
    # Should return empty results or validation error
    # Should NOT cause database error (500)
    assert response.status_code != 500


def test_user_id_sql_injection(client, auth_headers):
    """User ID parameter should be validated"""
    malicious_ids = ["1 OR 1=1", "1; DROP TABLE users", "1' OR '1'='1"]

    for mal_id in malicious_ids:
        response = client.get(f"/users/{mal_id}", headers=auth_headers)
        # Should return 422 (validation) or 404 (not found)
        # Should NOT return 500 or expose data
        assert response.status_code in [404, 422]
```

### ORM-Specific SQL Injection Tests

```python
def test_raw_query_injection(client, auth_headers):
    """If raw queries are used, they should be parameterized"""
    # Test with injection in filter
    response = client.get("/items/?filter=name='test' OR 1=1", headers=auth_headers)
    assert response.status_code in [400, 422]


def test_order_by_injection(client, auth_headers):
    """ORDER BY clause should not be injectable"""
    malicious_orders = [
        "name; DROP TABLE items",
        "name DESC; DELETE FROM items",
        "(SELECT password FROM users)",
    ]

    for order in malicious_orders:
        response = client.get(f"/items/?order_by={order}", headers=auth_headers)
        assert response.status_code in [400, 422]
```

---

## XSS Prevention Testing

### Stored XSS Tests

```python
XSS_PAYLOADS = [
    "<script>alert('xss')</script>",
    "<img src=x onerror=alert('xss')>",
    "<svg onload=alert('xss')>",
    "javascript:alert('xss')",
    "<body onload=alert('xss')>",
    "';alert('xss');//",
    "<iframe src='javascript:alert(1)'>",
]

@pytest.mark.parametrize("payload", XSS_PAYLOADS)
def test_xss_in_user_name(client, auth_headers, payload):
    """User name should be sanitized/escaped"""
    response = client.post("/users/", json={
        "name": payload,
        "email": "test@example.com"
    }, headers=auth_headers)

    if response.status_code == 201:
        # If accepted, script tags should be escaped/removed
        returned_name = response.json().get("name", "")
        assert "<script>" not in returned_name
        assert "javascript:" not in returned_name.lower()


@pytest.mark.parametrize("payload", XSS_PAYLOADS)
def test_xss_in_item_description(client, auth_headers, payload):
    """Item description should not execute scripts"""
    response = client.post("/items/", json={
        "name": "Test Item",
        "description": payload
    }, headers=auth_headers)

    if response.status_code == 201:
        # Verify output is escaped
        item_id = response.json()["id"]
        get_response = client.get(f"/items/{item_id}", headers=auth_headers)
        description = get_response.json().get("description", "")

        # Raw script tags should not be present
        assert "<script>" not in description or "&lt;script&gt;" in description
```

### Reflected XSS Tests

```python
@pytest.mark.parametrize("payload", XSS_PAYLOADS)
def test_xss_in_search_query(client, auth_headers, payload):
    """Search query should not be reflected unsanitized"""
    response = client.get(f"/search/?q={payload}", headers=auth_headers)

    # If query is echoed in response, it should be escaped
    response_text = response.text
    if payload in response_text:
        # Raw payload should not appear; only escaped version
        assert "<script>" not in response_text or "script" not in response_text
```

---

## Authentication Bypass Testing

### JWT Token Tests

```python
def test_missing_token_returns_401(client):
    """Endpoints should require authentication"""
    protected_endpoints = [
        ("GET", "/users/me"),
        ("POST", "/items/"),
        ("PUT", "/items/1"),
        ("DELETE", "/items/1"),
    ]

    for method, endpoint in protected_endpoints:
        response = getattr(client, method.lower())(endpoint)
        assert response.status_code == 401


def test_invalid_token_returns_401(client):
    """Invalid tokens should be rejected"""
    invalid_tokens = [
        "invalid_token",
        "Bearer invalid",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
        "",
    ]

    for token in invalid_tokens:
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == 401


def test_expired_token_returns_401(client):
    """Expired tokens should be rejected"""
    # Create a token that's already expired
    expired_token = create_access_token(
        data={"sub": "testuser"},
        expires_delta=timedelta(seconds=-1)  # Expired 1 second ago
    )

    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 401


def test_token_from_different_secret_rejected(client):
    """Tokens signed with different secret should be rejected"""
    # Create token with wrong secret
    wrong_secret_token = jwt.encode(
        {"sub": "testuser", "exp": datetime.utcnow() + timedelta(hours=1)},
        "wrong_secret",
        algorithm="HS256"
    )

    headers = {"Authorization": f"Bearer {wrong_secret_token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 401
```

### Authorization Tests

```python
def test_user_cannot_access_other_users_data(client, user1_token, user2_id):
    """Users should only access their own data"""
    headers = {"Authorization": f"Bearer {user1_token}"}

    response = client.get(f"/users/{user2_id}", headers=headers)
    assert response.status_code in [403, 404]


def test_non_admin_cannot_access_admin_endpoints(client, regular_user_token):
    """Non-admin users should not access admin endpoints"""
    headers = {"Authorization": f"Bearer {regular_user_token}"}

    admin_endpoints = [
        ("GET", "/admin/users"),
        ("DELETE", "/admin/users/1"),
        ("POST", "/admin/settings"),
    ]

    for method, endpoint in admin_endpoints:
        response = getattr(client, method.lower())(endpoint, headers=headers)
        assert response.status_code == 403


def test_idor_vulnerability(client, user1_token):
    """Test Insecure Direct Object Reference"""
    headers = {"Authorization": f"Bearer {user1_token}"}

    # Try to access items by guessing IDs
    for item_id in range(1, 100):
        response = client.get(f"/items/{item_id}", headers=headers)
        if response.status_code == 200:
            # If item exists, verify user owns it
            item = response.json()
            assert item.get("owner_id") == 1  # user1's ID
```

---

## Rate Limiting Tests

```python
def test_rate_limiting_on_login(client):
    """Login should have rate limiting to prevent brute force"""
    # Make many rapid requests
    responses = []
    for i in range(20):
        response = client.post("/login", json={
            "email": "test@example.com",
            "password": f"wrong_password_{i}"
        })
        responses.append(response.status_code)

    # After many attempts, should get 429 (Too Many Requests)
    assert 429 in responses, "Rate limiting should trigger after multiple failed attempts"


def test_rate_limiting_on_api(client, auth_headers):
    """API should have rate limiting"""
    responses = []
    for i in range(100):
        response = client.get("/items/", headers=auth_headers)
        responses.append(response.status_code)

    # Should eventually get rate limited
    rate_limited = responses.count(429)
    assert rate_limited > 0, "Rate limiting should be implemented"


def test_rate_limit_reset(client):
    """Rate limit should reset after cooldown period"""
    # Trigger rate limit
    for i in range(20):
        client.post("/login", json={"email": "test@example.com", "password": "wrong"})

    # Wait for reset (this may need adjustment based on your rate limit config)
    import time
    time.sleep(60)  # Wait for rate limit window to reset

    # Should be able to make requests again
    response = client.post("/login", json={
        "email": "test@example.com",
        "password": "wrong"
    })
    assert response.status_code != 429
```

---

## Input Validation Testing

### Data Type Validation

```python
def test_integer_field_rejects_string(client, auth_headers):
    """Integer fields should reject string input"""
    response = client.post("/items/", json={
        "name": "Test",
        "quantity": "not_a_number"
    }, headers=auth_headers)
    assert response.status_code == 422


def test_email_field_validates_format(client, auth_headers):
    """Email fields should validate email format"""
    invalid_emails = [
        "not_an_email",
        "@nodomain.com",
        "no@domain",
        "spaces in@email.com",
        "double@@at.com",
    ]

    for email in invalid_emails:
        response = client.post("/users/", json={
            "email": email,
            "password": "ValidPass123"
        }, headers=auth_headers)
        assert response.status_code == 422


def test_url_field_validates_format(client, auth_headers):
    """URL fields should validate URL format"""
    invalid_urls = [
        "not_a_url",
        "ftp://invalid_protocol.com",
        "javascript:alert(1)",
        "file:///etc/passwd",
    ]

    for url in invalid_urls:
        response = client.post("/links/", json={
            "name": "Test",
            "url": url
        }, headers=auth_headers)
        assert response.status_code == 422
```

### Length and Size Validation

```python
def test_field_max_length(client, auth_headers):
    """Fields should enforce maximum length"""
    # Very long string (potential buffer overflow)
    long_string = "A" * 100000

    response = client.post("/users/", json={
        "name": long_string,
        "email": "test@example.com"
    }, headers=auth_headers)

    # Should reject or truncate
    assert response.status_code == 422 or len(response.json().get("name", "")) < 100000


def test_file_upload_size_limit(client, auth_headers):
    """File uploads should have size limits"""
    # Create large file (10MB)
    large_file = b"X" * (10 * 1024 * 1024)

    response = client.post(
        "/upload/",
        files={"file": ("large.txt", large_file)},
        headers=auth_headers
    )

    # Should reject large files
    assert response.status_code in [413, 422]
```

---

## OWASP Top 10 Testing Summary

### Quick Test Checklist

```python
# conftest.py - Security fixtures
import pytest

@pytest.fixture
def security_test_payloads():
    return {
        "sql_injection": [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1 OR 1=1",
        ],
        "xss": [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert(1)>",
        ],
        "path_traversal": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
        ],
        "command_injection": [
            "; cat /etc/passwd",
            "| ls -la",
            "$(whoami)",
        ],
    }

# Test file
class TestOWASPTop10:
    """OWASP Top 10 Security Tests"""

    def test_a01_broken_access_control(self, client, user_token):
        """A01: Test for broken access control"""
        pass  # Implement IDOR, privilege escalation tests

    def test_a02_cryptographic_failures(self, client):
        """A02: Test for cryptographic weaknesses"""
        # Verify sensitive data is encrypted
        # Verify passwords are hashed
        pass

    def test_a03_injection(self, client, security_test_payloads):
        """A03: Test for injection vulnerabilities"""
        pass  # SQL, NoSQL, OS command injection tests

    def test_a04_insecure_design(self, client):
        """A04: Test for insecure design patterns"""
        pass  # Rate limiting, business logic tests

    def test_a05_security_misconfiguration(self, client):
        """A05: Test for security misconfigurations"""
        # Check for sensitive headers
        response = client.get("/")
        assert "Server" not in response.headers
        assert response.headers.get("X-Content-Type-Options") == "nosniff"

    def test_a06_vulnerable_components(self):
        """A06: Check for vulnerable dependencies"""
        # Run: pip-audit or safety check
        pass

    def test_a07_auth_failures(self, client):
        """A07: Test authentication mechanisms"""
        pass  # Password strength, session management tests

    def test_a08_data_integrity_failures(self, client):
        """A08: Test for integrity verification"""
        pass  # CSRF, unsigned data tests

    def test_a09_logging_failures(self, client, caplog):
        """A09: Verify security events are logged"""
        client.post("/login", json={"email": "test@example.com", "password": "wrong"})
        assert "failed login" in caplog.text.lower()

    def test_a10_ssrf(self, client, auth_headers):
        """A10: Test for Server-Side Request Forgery"""
        ssrf_urls = [
            "http://localhost:22",
            "http://127.0.0.1:6379",
            "http://169.254.169.254/",  # AWS metadata
        ]
        for url in ssrf_urls:
            response = client.post("/fetch-url/", json={"url": url}, headers=auth_headers)
            assert response.status_code in [400, 422, 403]
```

---

## Security Testing Commands

```bash
# Run security tests only
pytest -m security -v

# Run with coverage
pytest tests/security/ --cov=app --cov-report=html

# Static security analysis
pip install bandit
bandit -r app/

# Dependency vulnerability scan
pip install safety
safety check

# Or using pip-audit
pip install pip-audit
pip-audit
```

---

## Security Testing Markers

```python
# conftest.py
import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "security: security related tests")
    config.addinivalue_line("markers", "owasp: OWASP Top 10 tests")
    config.addinivalue_line("markers", "injection: injection vulnerability tests")
    config.addinivalue_line("markers", "auth: authentication tests")
```

```ini
# pytest.ini
[pytest]
markers =
    security: security related tests
    owasp: OWASP Top 10 tests
    injection: injection vulnerability tests
    auth: authentication tests
```
