# JWT Token — Concept & Behind the Scene Working

---

## Problem — JWT Kyun Chahiye?

Jab bhi user app pe koi request karta hai, server ko verify karna hota hai ke yeh user kaun hai.
Agar token na ho toh:

```
User → Login kiya (email + password)
Server → Theek hai, andar ao!

5 seconds baad...
User → Dobara request ki
Server → Tum kaun ho? Phir se login karo!
User → 😤 Bhai yaar, pakao mat!
```

**Har request pe login = bahut irritating.**

### Solution — JWT Token

```
User → Pehli baar login kiya (email + password)
Server → Sahi hai! Yeh lo token, 15 minute ke liye valid hai.

Baad mein...
User → Bhai mujhe data chahiye, yeh raha mera token.
Server → Token check kiya... sahi hai! Lo data, login ki zaroorat nahi. ✅
```

---

## SECRET_KEY — Server Ki Private Chaabi

```python
SECRET_KEY = "ZAIN123321"
```

- Yeh sirf **server ke paas** hoti hai — kisi aur ko pata nahi honi chahiye.
- Isse token pe **mauhr (stamp)** lagti hai.
- Koi bhi bina is key ke **valid token nahi bana sakta**.

**Agar SECRET_KEY kisi aur ko pata chal jaye:**
```
Hacker → Fake token banata hai: {"sub": "admin@gmail.com"}
Server → Verify karta hai → Pass ho jata → DISASTER! 💥
```

**Is liye SECRET_KEY hamesha `.env` file mein rakho, code mein hardcode mat karo.**

---

## ALGORITHM — Signing Ka Formula

```python
ALGORITHM = "HS256"
```

- **HS** = HMAC-SHA (ek math formula)
- **256** = 256 bits ki strength (bahut strong)
- Yeh batata hai ke token ko **kaise sign karna hai**.
- Token banate waqt bhi use hota hai, verify karte waqt bhi — **dono jagah same hona chahiye**.

---

## JWT Token Ki Structure — 3 Parts

```
eyJhbGciOiJIUzI1NiJ9 . eyJzdWIiOiJ6YWluQGdtYWlsLmNvbSJ9 . SflKxwRJSMeKKF2QT4fw
        ↑                           ↑                                  ↑
     HEADER                      PAYLOAD                          SIGNATURE
```

### Part 1 — Header

```json
{"alg": "HS256"}
```

- Sirf algorithm ka naam hota hai.
- Base64 se encode hota hai → `eyJhbGciOiJIUzI1NiJ9`

### Part 2 — Payload

```json
{"sub": "zain@gmail.com", "exp": "<expiry time>"}
```

- **sub** = Subject — user kaun hai (email)
- **exp** = Expiry — token kab expire hoga
- Base64 se encode hota hai → `eyJzdWIiOiJ6YWluQGdtYWlsLmNvbSJ9`

> **Important:** Base64 encryption NAHI hai — koi bhi isko decode kar sakta hai.
> Isliye payload mein kabhi password ya sensitive info mat rakho.

### Part 3 — Signature (Sabse Important)

```
Signature = HS256(
    BASE64(Header) + "." + BASE64(Payload),
    SECRET_KEY
)
```

- Signature **Header + Payload + SECRET_KEY** teeno milake banta hai.
- Sirf server bana sakta hai — kyunki SECRET_KEY sirf server ke paas hai.

**Kyun Header + Payload dono signature mein hain?**

```
Agar sirf SECRET_KEY se banta:
  Hacker Payload badal de → {"sub": "admin@gmail.com"}
  Signature same rehta → Server pass kar deta → PROBLEM! 💥

Header + Payload signature mein hone se:
  Hacker Payload badla → Payload ka Base64 badla
  Server ne dobara signature banaya → Match nahi kiya → FAKE pakad liya! ✅
```

---

## Behind the Scene — Token Banana (Encoding)

```
Step 1:  Header banao
         {"alg": "HS256"}
                ↓ Base64
         "eyJhbGciOiJIUzI1NiJ9"

Step 2:  Payload banao
         {"sub": "zain@gmail.com", "exp": "3:15 PM"}
                ↓ Base64
         "eyJzdWIiOiJ6YWluQGdtYWlsLmNvbSJ9"

Step 3:  Signature banao
         HS256(
             "eyJhbGci..." + "." + "eyJzdWIi...",
             SECRET_KEY = "ZAIN123321"
         )
         = "SflKxwRJSMeKKF2QT4fw..."

Step 4:  Teeno ko dot se jodo
         eyJhbGci... + "." + eyJzdWIi... + "." + SflKxwRJ...
         = FINAL TOKEN ✅
```

---

## Behind the Scene — Token Verify Karna (Decoding)

```
User ne token bheja:
"eyJhbGci....eyJzdWIi....SflKxwRJ"

Step 1:  Dot pe split karo → 3 parts
         Header | Payload | Signature_from_user

Step 2:  Server DOBARA apni SECRET_KEY se signature banata hai:
         HS256(Header + "." + Payload, SECRET_KEY)
         = "SflKxwRJ..."

Step 3:  Compare karo:
         Naya Signature == User ka Signature?
         ✅ Haan → Token original hai
         ❌ Nahi → Token fake/tampered hai

Step 4:  Expiry check karo:
         exp > abhi ka time?
         ✅ Haan → Valid
         ❌ Nahi → Expired, dobara login karo
```

---

## verify_token — Behind the Scene Deep Working

### Encoding vs Decoding — Direction Confusion Clear Karo

Yeh ulti direction mein hoti hai:

```
ENCODING (Token Banana):
Original JSON  ──►  Base64  ──►  Special Characters
{"sub":"zain"}  ──────────────►  "eyJzdWIiOiJ6YWluIn0"

DECODING (Token Verify Karna):
Special Characters  ──►  Base64  ──►  Original JSON
"eyJzdWIiOiJ6YWluIn0"  ──────────►  {"sub":"zain"}
```

> Decode mein hum Special Characters ko **wapas** original JSON mein laate hain — Base64 encode nahi karte.

---

### Step by Step — jwt.decode() Ke Andar Kya Hota Hai

#### Step 1 — Token ke 3 Parts Alag Karo

```
"eyJhbGci....eyJzdWIi....SflKxwRJ"
         ↓ dot pe split
┌─────────────────────────────────────────┐
│ Part 1: Header   "eyJhbGciOiJIUzI1NiJ9"│
│ Part 2: Payload  "eyJzdWIiOiJ6YWluQG..." │
│ Part 3: Signature "SflKxwRJSMeKKF2QT4fw"│
└─────────────────────────────────────────┘
```

#### Step 2 — Signature Verify Karo (Sabse Pehle!)

Server khud se naya signature banata hai:

```
Naya Signature = HS256(
    "eyJhbGci..." + "." + "eyJzdWIi...",
    SECRET_KEY = "ZAIN123321"
)
= "SflKxwRJ..."

Phir compare:
Naya Signature  ==  Token ka Signature (Part 3)?

✅ Match → Aage bado (token tampered nahi)
❌ No Match → JWTError throw → None return (FAKE token!)
```

> **Kyun pehle signature?** Agar pehle expiry check karein aur baad mein pata chale token fake tha — toh galat cheez check ki. Pehle authenticity, phir validity.

#### Step 3 — Payload ko Base64 Decode Karo

```
"eyJzdWIiOiJ6YWluQGdtYWlsLmNvbSJ9"
         ↓ Base64 DECODE (ulti direction — wapas original)
{
  "sub": "zain@gmail.com",
  "exp": 1234567890
}
```

#### Step 4 — Expiry Check Karo

```
Payload se exp nikalo: 1234567890 (Unix timestamp)
         ↓
Abhi ka time: datetime.utcnow()
         ↓
exp < abhi ka time?

❌ Haan, expire ho gaya → JWTError throw → None return
✅ Nahi, abhi valid hai → Aage bado
```

#### Step 5 — Payload Return Karo

```python
return {
    "sub": "zain@gmail.com",
    "exp": 1234567890
}
# Yeh dict caller ko milti hai
# Server samajh jata hai: request zain@gmail.com ki taraf se aayi hai
```

---

### Pura Flow Diagram — verify_token

```
jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            │
            ▼
    ┌───────────────────────────────────┐
    │  Step 1: Token → 3 parts          │
    │  Header | Payload | Signature     │
    └───────────────┬───────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────┐
    │  Step 2: Signature Verify         │
    │  HS256(Header+Payload, SECRET_KEY)│
    │  == Token ka Signature?           │
    └──────┬──────────────┬────────────┘
           │ ❌ No Match  │ ✅ Match
           ▼              ▼
       JWTError    ┌──────────────────────┐
       None        │  Step 3: Base64      │
       return      │  Decode → Payload    │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │  Step 4: Expiry Check│
                   │  exp > abhi ka time? │
                   └──────┬───────┬───────┘
                          │ ❌    │ ✅
                          ▼       ▼
                      JWTError  Payload
                      None      Return ✅
                      return
```

---

### Code — verify_token Har Line Samajh Ke

```python
def verify_token(token: str) -> Optional[dict]:
    # token: str       = user ka bheja hua token string
    # Optional[dict]   = sahi hai toh dict return, ghalat toh None

    try:
        return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        # Andar yeh sab ho raha hai:
        # 1. Token → 3 parts (Header, Payload, Signature)
        # 2. HS256(Header+Payload, SECRET_KEY) → Naya Signature banao
        # 3. Naya Signature == Token Signature? → Nahi toh JWTError
        # 4. Payload Base64 Decode → Original JSON
        # 5. exp > abhi ka time? → Nahi toh JWTError
        # 6. Sab theek → Payload dict return

    except JWTError:
        return None
        # Koi bhi problem (fake, tampered, expired) → None
        # Koi crash nahi — quietly None de do
```

---

## Code — Har Line Samajh Ke

```python
SECRET_KEY = "ZAIN123321"   # Server ki private chaabi
ALGORITHM  = "HS256"        # Signing formula


def create_access_token(data: dict, expire_delta: Optional[timedelta] = None) -> str:

    encode_data = data.copy()
    # Original data safe rakho, copy pe kaam karo

    expire = datetime.utcnow() + (expire_delta or timedelta(minutes=15))
    # Abhi ka time + 15 minute = expiry time
    # expire_delta diya toh use karo, nahi diya toh default 15 min

    encode_data.update({"exp": expire})
    # Expiry time bhi data mein daal do
    # Ab encode_data = {"sub": "zain@gmail.com", "exp": <3:15 PM>}

    return jwt.encode(encode_data, SECRET_KEY, ALGORITHM)
    # 1. encode_data ko Base64 karo (Header + Payload)
    # 2. SECRET_KEY + HS256 se Signature banao
    # 3. Teeno ko dot se jodo → Final Token string return


def decode_token(token: str) -> Optional[dict]:

    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Token ke 3 parts alag karo
        # SECRET_KEY se dobara signature banao
        # Compare karo → sahi hai toh dict return karo

    except JWTError:
        return None
        # Token fake, expired, ya tampered → None return
```

---

## Puri Flow — Ek Jagah

```
1.  User → POST /login { email, password }
2.  Server → DB mein check kiya → Sahi hai!
3.  Server → create_access_token({"sub": "zain@gmail.com"})
4.  Server → Token user ko de diya

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5.  User → GET /profile + Header: "Bearer <TOKEN>"
6.  Server → decode_token(token)
7.  Server → Signature match kiya ✅ + Expiry check kiya ✅
8.  Server → {"sub": "zain@gmail.com"} mila → Data return kar diya

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

(15 minute baad)
9.  User → GET /profile + Header: "Bearer <OLD_TOKEN>"
10. Server → Expiry check kiya → Expired! ❌
11. User → Dobara login karna parega
```

---

## Quick Reference Table

| Cheez | Kya hai | Kyun |
|---|---|---|
| `SECRET_KEY` | Server ki private chaabi | Token sign aur verify karne ke liye |
| `ALGORITHM` | Math formula (HS256) | Signing ka tareeqa batata hai |
| `Header` | Algorithm ka naam (Base64) | Token kaise bana hai |
| `Payload` | User info + Expiry (Base64) | Token mein kya data hai |
| `Signature` | HS256(Header+Payload, KEY) | Prove karta hai token original hai |
| `Base64` | Text → special chars | Data pack karna (encryption nahi!) |
| `exp` | Expiry claim | Token kab tak valid hai |
| `sub` | Subject claim | User kaun hai (email) |

---

## Token Ko Har Request Mein Use Karna — FastAPI Protected Routes

---

### Part 1 — "Bearer" Kya Hai?

Login return karta hai:

```python
{"token_type": "bearer", "access_token": token}
```

**Bearer** ka matlab: **"Jo bhi yeh token laaya, use andar aane do"**

> Real life analogy: Cinema ticket ki tarah. Jo banda ticket laaya — check nahi karte ke ticket khareedne wala wohi hai ya nahi. Token bearer (laane wala) ka haq deta hai.

Jab user kisi protected route pe request karta hai, token **Authorization header** mein bhejta hai:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJz...
                ↑
         Yeh word "Bearer" prefix hota hai
         Phir space ke baad actual token
```

---

### Part 2 — OAuth2PasswordBearer Kya Hai?

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
```

Yeh FastAPI ka ek **built-in helper** hai jo do kaam karta hai:

**Kaam 1:** Har request ke `Authorization` header se **token automatically nikaal leta hai**

```
Request aati hai:
Authorization: Bearer eyJhbGci...

oauth2_scheme → "eyJhbGci..." token nikaalta hai
```

**Kaam 2:** Swagger UI (`/docs`) mein automatically **Authorize (🔒) button** banata hai

```
Tumhare /docs pe ek tala icon aata hai
User wahan token paste karta hai
Phir protected routes test kar sakta hai
```

> `tokenUrl="login"` sirf Swagger ko batata hai: "Token lene ke liye /login pe jao"

---

### Part 3 — Depends() Kya Hai?

`Depends()` FastAPI ka **dependency injection** system hai.

Seedha samjho: **"Pehle yeh kaam karo, phir mujhe result do"**

```python
@app.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    #                                  ↑
    #  Matlab: Pehle get_current_user() chalao
    #  Uska result current_user mein daal do
    #  Phir get_profile() chale ga
```

> Analogy: Restaurant mein order karne se pehle ID card check hota hai. Depends waiter hai jo pehle ID check karta hai, phir order leta hai.

---

### Part 4 — get_current_user Kya Karta Hai?

Yeh function har protected request pe automatically chalta hai aur **3 kaam karta hai:**

```
Request aati hai token ke saath
         ↓
┌─────────────────────────────────────┐
│  Step 1: Token verify karo          │
│  verify_token(token)                │
│  → Sahi? Aage bado                  │
│  → Ghalat/Expired? 401 Error        │
└──────────────────┬──────────────────┘
                   ↓
┌─────────────────────────────────────┐
│  Step 2: Payload se email nikalo    │
│  payload.get("sub")                 │
│  → "zain@gmail.com" mila            │
│  → Email nahi mili? 401 Error       │
└──────────────────┬──────────────────┘
                   ↓
┌─────────────────────────────────────┐
│  Step 3: DB mein user dhundo        │
│  select(User).where(email == ...)   │
│  → User mila? Return karo           │
│  → User nahi mila? 401 Error        │
└──────────────────┬──────────────────┘
                   ↓
            User object return
            (route ko mil jata hai)
```

---

### Part 5 — Puri Flow Login Se Protected Route Tak

```
━━━━━━━━ LOGIN (Token Lena) ━━━━━━━━

User → POST /login {email, password}
Server → Password verify kiya ✅
Server → Token banaya
Server → {"access_token": "eyJ...", "token_type": "bearer"} return
User → Token apne paas rakh leta hai


━━━━━━━━ PROTECTED ROUTE (Token Use Karna) ━━━━━━━━

User → GET /profile
       Header: "Authorization: Bearer eyJ..."
                          ↓
       oauth2_scheme → Token nikaalta hai "eyJ..."
                          ↓
       get_current_user(token) chalta hai:
         → verify_token()  → payload nikala
         → payload["sub"]  → "zain@gmail.com"
         → DB se User nikala
         → User return kiya
                          ↓
       get_profile(current_user = <User object>)
       → Profile data return ✅


━━━━━━━━ AGAR TOKEN GHALAT YA EXPIRED ━━━━━━━━

User → GET /profile
       Header: "Authorization: Bearer FAKE_TOKEN"
                          ↓
       get_current_user → verify_token() → None
                          ↓
       401 Unauthorized Error ❌
       {"detail": "Could not validate credentials"}
```

---

### Part 6 — Code Structure — Kya Kya Likhna Hai

#### Step 1: oauth2_scheme banao

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
# "login" = tumhara /login endpoint ka naam
```

#### Step 2: verify_token function

```python
def verify_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALOGRITHUM])
        # Token sahi → payload dict return
    except JWTError:
        return None
        # Token ghalat/expired → None
```

#### Step 3: get_current_user dependency

```python
def get_current_user(
    token: str = Depends(oauth2_scheme),     # Header se token nikalo
    session: Session = Depends(get_session)  # DB session lo
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_token(token)            # Token verify karo
    if payload is None:
        raise credentials_exception          # Token ghalat → 401

    email = payload.get("sub")               # Email nikalo payload se
    if email is None:
        raise credentials_exception          # Email nahi → 401

    user = session.exec(
        select(User).where(User.email == email)
    ).first()                                # DB se user dhundo

    if user is None:
        raise credentials_exception          # User DB mein nahi → 401

    return user                              # Sab theek → User return
```

#### Step 4: Protected Route banao

```python
@app.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    # current_user automatically verified user hoga
    # Agar token ghalat tha toh yahan tak pahuncha hi nahi
    return {"name": current_user.name, "email": current_user.email}
```

---

### Part 7 — Concepts Summary Table

| Concept | Kya hai | Kaam |
|---|---|---|
| `Bearer` | "Jo token laaya use andar aane do" | Token type standard |
| `OAuth2PasswordBearer` | FastAPI ka built-in helper | Header se token nikalta hai + Swagger lock button |
| `Depends()` | "Pehle yeh chalao, phir mujhe result do" | Route se pehle function run karwata hai |
| `get_current_user` | Token verify + email + DB check | Har protected route ka darban |
| `401 Unauthorized` | Token ghalat ya expire | Access deny |
| `WWW-Authenticate: Bearer` | HTTP standard header | Client ko batata hai Bearer token chahiye |

---

## OAuth2PasswordBearer Ka Asli Kaam — Confusion Clear

---

### Sawaal: "Agar user token header mein khud pass karta hai toh OAuth2PasswordBearer ki kya zaroorat hai?"

Token header mein aisa aata hai:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJz...
```

Is header se sirf token nikalna itna simple nahi — OAuth2PasswordBearer ke bina yeh sab **khud likhna padta**:

```python
# OAuth2PasswordBearer ke BINA — manually likhna padta
def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")  # Header nikalo
    if not auth_header:
        raise HTTPException(401)                         # Nahi hai? Error
    if not auth_header.startswith("Bearer "):
        raise HTTPException(401)                         # Format ghalat? Error
    token = auth_header[7:]                              # "Bearer " hatao, token lo
    ...
```

**OAuth2PasswordBearer ke SAATH — yeh sab automatic:**

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    # token automatically nikal ke aa gaya — kuch likhna nahi pada
    ...
```

> OAuth2PasswordBearer ek **automatic token extractor** hai. Is ke bina har route pe manually header parse karna padta.

**Bonus kaam:** Agar koi request bina token ke aaye — OAuth2PasswordBearer **khud hi 401 return kar deta hai**, tumhara function chalta hi nahi.

---

### tokenUrl="login" Ka Kaam

```python
OAuth2PasswordBearer(tokenUrl="login")
#                             ↑
#              Sirf Swagger UI ko hint deta hai
```

`tokenUrl` ka **sirf ek kaam** hai — **Swagger UI (`/docs`) ko batana ke token kahan se milega.**

Swagger docs pe jab lock icon (🔒) click karo — ek dialog khulta hai jo kehta hai:
```
"Token chahiye? /login pe jao"
         ↑
    tokenUrl="login" se yeh line aati hai
```

> **Actual API requests pe tokenUrl ka koi asar nahi.** Woh sirf Swagger UI ke liye documentation/hint hai.

---

### WWW-Authenticate: Bearer — Kyun Header Mein Dete Hain?

```python
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},   # ← Yeh kyun?
)
```

Jab token ghalat ya expired ho — response kuch aisa hota hai:

```
Response Header:  WWW-Authenticate: Bearer
Response Body:    {"detail": "Could not validate credentials"}
Status Code:      401
```

`WWW-Authenticate: Bearer` ka matlab: **"Bhai, Bearer token chahiye tha — jo sahi nahi tha."**

Yeh HTTP ka standard tareeqa hai client ko batane ka ke authentication kaise kare. Browser aur API clients is header ko padh ke samajhte hain ke dobara sahi token de kar try karo.

---

### Puri Flow — Sab Ek Jagah (Updated)

```
━━━━━━━━ STEP 1: Login ━━━━━━━━

User → POST /login {email, password}
Server → verify kiya → token banaya → return kar diya


━━━━━━━━ STEP 2: Protected Request ━━━━━━━━

User → GET /profile
       Header: "Authorization: Bearer eyJhbGci..."
                    ↓
       OAuth2PasswordBearer → "eyJhbGci..." automatically nikaalta hai
       (manually kuch nahi karna — yeh automatic hai)
                    ↓
       get_current_user(token="eyJhbGci...") chalta hai
                    ↓
       verify_token(token) → payload nikala ya None
                    ↓
       email = payload["sub"] → "zain@gmail.com"
                    ↓
       DB se User object nikala
                    ↓
       User return → route function ko mil gaya ✅


━━━━━━━━ STEP 3: Token Ghalat/Expired ━━━━━━━━

User → GET /profile
       Header: "Authorization: Bearer FAKE_TOKEN"
                    ↓
       verify_token → None return
                    ↓
       credentials_exception raise:
         Body:   status 401 + "Could not validate credentials"
         Header: WWW-Authenticate: Bearer
                    ↓
       Route function chala hi nahi ❌
```

---

### Final Summary Table

| Sawaal | Jawab |
|---|---|
| Bearer kya hai? | "Jo token laaya use andar aane do" |
| OAuth2PasswordBearer kyun? | Header se token automatic nikalta hai, khud likhna nahi padta |
| tokenUrl="login" kyun? | Sirf Swagger UI ko hint — actual API pe koi asar nahi |
| WWW-Authenticate: Bearer kyun? | Client ko batata hai ke Bearer token chahiye tha |
| Agar token nahi aaya? | OAuth2PasswordBearer khud 401 return kar deta hai |

---

## ExpiredSignatureError vs JWTError — Expired Token Ka Alag Message

---

### Problem — Abhi Kya Ho Raha Tha?

```
Token expire hua  → JWTError → None → "Could not validate credentials"
Token fake hua    → JWTError → None → "Could not validate credentials"
```

Dono cases mein same error — user ko samajh nahi aata ke token expire hua hai ya kuch aur problem hai.

---

### jwt.decode Andar Kya Karta Hai?

Jab `jwt.decode(token)` chalta hai, yeh khud decide karta hai kaunsi error throw karni hai:

```
jwt.decode(token)
      │
      ├── Signature sahi hai? (SECRET_KEY se verify)
      │         Nahi → JWTError throw karo
      │
      └── exp > abhi ka time? (expiry check)
                Nahi → ExpiredSignatureError throw karo
```

> Tumhein khud kuch check nahi karna — `jwt.decode` automatically sahi error throw karta hai.

---

### ExpiredSignatureError aur JWTError Ka Rishta

```
JWTError                ← Parent (Baap)
    │
    └── ExpiredSignatureError   ← Child (Beta)
```

`ExpiredSignatureError` **JWTError ka beta** hai — yani yeh JWTError bhi hai, lekin zyada specific.

> Bilkul jaise: "Janwar" parent hai, "Kutta" child hai. Kutta ek janwar bhi hai, lekin specific type.

---

### Python Except Blocks Kaise Check Karta Hai?

Python **upar se neeche** except blocks check karta hai — **pehla match jeet jaata hai:**

```python
try:
    jwt.decode(...)

except ExpiredSignatureError:   # ← Pehle check hota hai (specific/beta)
    return "expired"

except JWTError:                # ← Baad mein check hota hai (general/baap)
    return None
```

#### Case 1 — Token Expired:
```
jwt.decode → ExpiredSignatureError throw karta hai
      ↓
Python: "ExpiredSignatureError hai?" → ✅ Haan, match!
      ↓
return "expired"  ← Yahan ruk jaata hai, JWTError tak nahi jaata
```

#### Case 2 — Token Fake/Ghalat:
```
jwt.decode → JWTError throw karta hai
      ↓
Python: "ExpiredSignatureError hai?" → ❌ Nahi
      ↓
Python: "JWTError hai?"              → ✅ Haan, match!
      ↓
return None
```

#### Case 3 — Token Bilkul Sahi:
```
jwt.decode → Koi error nahi
      ↓
return user_obj  ← Directly return, koi except nahi chala
```

---

### Order Kyun Important Hai?

Agar ulta likho — pehle JWTError, baad mein ExpiredSignatureError:

```python
except JWTError:                # ← Pehle — GALAT!
    return None

except ExpiredSignatureError:   # ← Baad mein — KABHI NAHI CHALEGA!
    return "expired"
```

```
Token expire hua → ExpiredSignatureError throw hua
      ↓
Python: "JWTError hai?" → ✅ Haan! (kyunki ExpiredSignatureError JWTError ka beta hai)
      ↓
None return  ← Galat! "expired" wala block skip ho gaya
```

> **Rule:** Hamesha specific (beta) pehle, general (baap) baad mein likho.

---

### Solution — verify_token Updated

```python
from jose import jwt, JWTError, ExpiredSignatureError

def verify_token(token: str) -> Optional[dict]:
    try:
        user_obj = jwt.decode(token, SECRET_KEY, algorithms=[ALOGRITHUM])
        return user_obj              # Token sahi → payload return
    except ExpiredSignatureError:
        return "expired"             # Token expire hua → "expired" string
    except JWTError:
        return None                  # Token fake/ghalat → None
```

### get_access_user mein Alag Messages

```python
user_data = verify_token(token)

if user_data == "expired":
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token expired! Please login again.",
        headers={"WWW-Authenticate": "Bearer"},
    )

if not user_data:
    raise credentailHttpException    # Fake/ghalat token
```

---

### Puri Flow — Teen Cases

```
verify_token(token)
      │
      ├── Token valid      → payload dict return ✅
      │                          ↓
      │                    email nikalo → DB check → User return
      │
      ├── Token EXPIRED    → "expired" string return ⏰
      │                          ↓
      │                    401 "Token expired! Please login again."
      │
      └── Token FAKE/BAD   → None return ❌
                                 ↓
                           401 "Could not validate credentials"
```
