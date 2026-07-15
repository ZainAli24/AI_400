from jose import jwt, JWTError, ExpiredSignatureError
from datetime import timedelta, datetime, timezone
from typing import Optional

SECRET_KEY="ZAIN_35!R4TT4"
ALOGRITHUM="HS256"


def create_access_token(data: dict, time: Optional[timedelta] = None):
    encode_data = data.copy()

    expire = datetime.now(timezone.utc) + (time or timedelta(minutes=15))

    encode_data.update({"exp": expire})

    jwt_token = jwt.encode(encode_data, SECRET_KEY, algorithm=ALOGRITHUM)
    
    return jwt_token




token = create_access_token({"sub": "zain@gmail.com"})
print(f"\n\n [=] TOKEN: {token} \n\n")



def verify_token(token):
    try:
        verify = jwt.decode(token, SECRET_KEY, algorithms=[ALOGRITHUM])
        return verify
    except (JWTError, ExpiredSignatureError):
        return None



payload = verify_token(token)
print(f"\n\n [-] Payload: {payload}\n\n")


