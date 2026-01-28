from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError

SECRET_KEY="your_secret_key"
ALGORITHM="HS256"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT token."""
    to_encode = data.copy()

    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
    


token = create_access_token({"sub": "zain@gmail.com"})

print("\n")

print("[+] Token created successfully: ", token)

print("\n")

data = decode_token(token)

print("[+] Decoded token data:", data)

print("\n")