from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional


SECRET_KEY="ZAIN123321"
ALOGRITHUM="HS256"


def create_access_token(data:dict, expire_delta: Optional[timedelta] = None) -> str:
    encode_data = data.copy()

    expire = datetime.utcnow() + (expire_delta or timedelta(minutes=15)) 

    encode_data.update({"exp": expire})

    return jwt.encode(encode_data, SECRET_KEY, ALOGRITHUM)



token = create_access_token({"sub": "zain@gmail.com"})
print("\n Access Token: ", token)





def verify_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=ALOGRITHUM)
    except JWTError:
        return None
        



print("\n -=-==-=-=-=-=-=-=-=-=-=--> ", verify_token(token))
