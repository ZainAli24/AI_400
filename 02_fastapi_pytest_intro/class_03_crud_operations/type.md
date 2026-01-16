# FastAPI Return Type Annotation aur Response Model

## Concept Overview

FastAPI mein jab aap function ke return type annotation define karte ho (`-> SomeModel`), toh FastAPI us type ko **response_model** ki tarah use karta hai. Ye automatically response ko filter aur validate karta hai.

## Key Points

### 1. Return Type Annotation ka Role
```python
def login_data(...) -> loginResponseData:  # Ye response model define karta hai
    return loginResponseDataReturn(...)     # Actual return value
```

- Function signature mein `-> loginResponseData` ka matlab hai ke **API response mein sirf is model ki fields return hongi**
- Ye FastAPI ko batata hai ke response ko kis structure mein return karna hai

### 2. Automatic Response Filtering

FastAPI automatically extra fields ko filter kar deta hai:

```python
class loginResponseData(BaseModel):
    name: str
    email: str
    age: int

class loginResponseDataReturn(BaseModel):
    name: str
    email: str
    age: int
    is_active: bool = True  # Extra field

@app.get("/login")
def login_data(...) -> loginResponseData:  # Response model
    return loginResponseDataReturn(...)     # Actual return (has is_active)
```

**Response:**
```json
{
  "name": "zain",
  "email": "ali",
  "age": 21
}
```

`is_active` field **return nahi hogi** kyunke wo `loginResponseData` mein defined nahi hai.

### 3. Validation

Agar aap jo return kar rahe ho us mein required fields missing hain, toh **Pydantic validation error** throw hoga:

```python
def login_data(...) -> loginResponseData:
    return {"name": "zain"}  # Error! email aur age missing
```

FastAPI/Pydantic error dega kyunke `loginResponseData` mein `email` aur `age` required fields hain.

### 4. Return Type Change karne par

Agar return type annotation change karo:

```python
def login_data(...) -> loginResponseDataReturn:  # Changed return type
    return loginResponseDataReturn(...)
```

**Response:**
```json
{
  "name": "zain",
  "email": "ali",
  "age": 21,
  "is_active": true
}
```

Ab `is_active` bhi response mein aa jayega!

## Summary

1. **Return type annotation (`-> Model`)** = Response ka structure define karta hai
2. **Actual return value** = Function mein kya return ho raha hai
3. **FastAPI ka kaam** = Actual return se sirf wo fields lena jo return type mein defined hain
4. **Validation** = Required fields missing hain toh error
5. **Filtering** = Extra fields automatically remove ho jati hain

## Practical Use Case

Ye feature tab useful hai jab:
- Database se complete object milta hai but API mein sirf kuch fields show karni hain
- Internal data (password, tokens) ko response se hide karna hai
- Different endpoints ke liye different response structures chahiye

**Example:**
```python
class UserInDB(BaseModel):
    name: str
    email: str
    password: str  # Internal field

class UserResponse(BaseModel):
    name: str
    email: str
    # password nahi hai - security ke liye

@app.get("/user")
def get_user() -> UserResponse:
    user_from_db = UserInDB(name="Ali", email="ali@test.com", password="secret123")
    return user_from_db  # FastAPI automatically password field remove kar dega
```

## Query Parameters vs Request Body aur .model_dump() Method

### 1. FastAPI ka Smart Behavior: Query Params vs Request Body

#### GET Request:
```python
@app.get("/login")
def login_data(name:str, email:str, age:int):
```

**Jab aap simple types use karte ho** (`str`, `int`, `float`, `bool`):
- FastAPI automatically inhe **query parameters** mein expect karta hai
- **GET request** mein data query params ke through aata hai
- Example: `http://localhost:8000/login?name=zain&email=ali@test.com&age=21`

#### POST Request:
```python
@app.post("/register")
def register_data(data:loginResponseData):
```

**Jab aap Pydantic Model use karte ho**:
- FastAPI automatically isko **request body** mein expect karta hai
- **POST request** mein data JSON body ke through aata hai
- Request body:
```json
{
  "name": "zain",
  "email": "ali@test.com",
  "age": 21
}
```

---

### 2. FastAPI ka Rule:

| Parameter Type | GET Request | POST/PUT/PATCH Request |
|---------------|-------------|------------------------|
| Simple types (`str`, `int`, etc.) | Query Parameters | Query Parameters (agar specify na karo) |
| Pydantic Model (BaseModel) | ❌ (Rarely used) | **Request Body** |

**Key Point**:
- **Pydantic BaseModel** = Automatically **Request Body**
- **Simple types** = Automatically **Query Parameters**

---

### 3. Agar aap POST mein `str` type use karo:

```python
@app.post("/register")
def register_data(name: str):  # Simple type
```

Ye **query parameter** ban jayega, body nahi!
- Request: `http://localhost:8000/register?name=zain`

**Ye galat hai POST ke liye!** POST mein data body mein hona chahiye.

**Sahi tareeqa:**
```python
@app.post("/register")
def register_data(data: loginResponseData):  # Pydantic Model
```

Ab data **request body** mein ayega (JSON format).

---

### 4. `.model_dump()` kya karta hai?

```python
return loginResponseDataReturn(**data.model_dump())
```

**Note:** Pydantic V2 mein `.dict()` deprecated hai, ab `.model_dump()` use karo.

#### Step-by-step:

**Step 1:** `data` ek Pydantic model object hai:
```python
data = loginResponseData(name="zain", email="ali@test.com", age=21)
```

**Step 2:** `data.model_dump()` - Ye object ko **dictionary** mein convert karta hai:
```python
data.model_dump()
# Output: {"name": "zain", "email": "ali@test.com", "age": 21}
```

**Step 3:** `**` operator - Ye dictionary ko **unpack** karta hai (keyword arguments mein convert):
```python
**data.model_dump()
# Ye ban jata hai:
# name="zain", email="ali@test.com", age=21
```

**Step 4:** Pura statement:
```python
loginResponseDataReturn(**data.model_dump())

# Equivalent to:
loginResponseDataReturn(
    name="zain",
    email="ali@test.com",
    age=21
)
```

#### Simple Example:
```python
# Ye dono same hain:

# Method 1: Manual
data = loginResponseData(name="zain", email="ali@test.com", age=21)
return loginResponseDataReturn(name=data.name, email=data.email, age=data.age)

# Method 2: Smart (using .model_dump() and **)
data = loginResponseData(name="zain", email="ali@test.com", age=21)
return loginResponseDataReturn(**data.model_dump())
```

---

### Summary:

1. **GET + Simple types (`str`, `int`)** = Query parameters (`?name=zain&age=21`)
2. **POST + Pydantic Model** = Request body (JSON format)
3. **`.model_dump()`** = Pydantic object ko dictionary mein convert karta hai (Pydantic V2)
4. **`**` operator** = Dictionary ko unpack karke keyword arguments bana deta hai

**Best Practice:**
- **GET** → Query parameters use karo (simple types)
- **POST/PUT/PATCH** → Request body use karo (Pydantic Model)
- **Pydantic V2** → `.model_dump()` use karo (`.dict()` deprecated hai)

---

# HTTP aur HTTPException - Complete Guide

## 1. HTTP kya hai?

**HTTP** = **H**yper**T**ext **T**ransfer **P**rotocol

### Definition
- Ye ek **protocol** (rules/tarika) hai jis se internet par communication hoti hai
- **Browser** (client) aur **Server** ke beech baat-cheet ka tarika
- Jab bhi aap koi website kholte hain ya API call karte hain, HTTP use hota hai

### HTTP kaise kaam karta hai?

```
Client (Browser)  ----Request---->  Server
                  <---Response----
```

**Example:**
1. Aap browser mein `www.google.com` type karte hain
2. Browser **HTTP Request** bhejta hai Google ke server ko
3. Server **HTTP Response** wapis bhejta hai webpage ke saath

---

## 2. HTTP Status Codes

HTTP mein har response ke saath ek **status code** hota hai jo batata hai ke kya hua:

### Success Codes (2xx)
- **200** - OK (sab theek hai) ✅
- **201** - Created (naya data ban gaya)

### Client Error Codes (4xx)
- **400** - Bad Request (user ne galat data bheja)
- **401** - Unauthorized (login nahi kiya)
- **403** - Forbidden (permission nahi hai)
- **404** - Not Found (cheez nahi mili)
- **422** - Validation Error (data validation fail)

### Server Error Codes (5xx)
- **500** - Internal Server Error (server mein problem)
- **503** - Service Unavailable (server kaam nahi kar raha)

---

## 3. HTTPException kya hai?

**HTTPException** FastAPI ka ek special class hai jo **HTTP errors ko properly handle** karta hai.

### Syntax
```python
from fastapi import HTTPException

raise HTTPException(status_code=400, detail="Error message")
```

### Components
1. **status_code** - HTTP status code (400, 404, 500, etc.)
2. **detail** - Error message jo user ko dikhana hai

---

## 4. HTTPException kyun use karte hain?

### ❌ Without HTTPException (Galat tarika)
```python
@app.post("/register")
def register_data(data: loginResponseData):
    if data.id == 0:
        return {"error": "ID 0 not allowed"}  # Ye proper nahi hai
```

**Problem:**
- Status code 200 (success) jayega, jabke error hai
- Client ko confuse hoga

### ✅ With HTTPException (Sahi tarika)
```python
@app.post("/register")
def register_data(data: loginResponseData):
    if data.id == 0:
        raise HTTPException(status_code=400, detail="ID 0 is not allowed!")
```

**Benefits:**
- Proper **400 status code** jayega
- Client samajh jayega ke error hai
- Professional API standards follow hota hai

---

## 5. Real Example - Aapki Code se

```python
@app.post("/register")
def register_data(data: loginResponseData) -> loginResponseDataReturn:
    if data.id == 0:
        raise HTTPException(status_code=400, detail="ID 0 is not allowed! 😫")
    return loginResponseDataReturn(**data.model_dump())
```

### Kya ho raha hai?

1. **Check**: Agar `id == 0` hai
2. **Raise Error**: HTTPException raise hota hai
3. **Response**: Client ko ye milta hai:

```json
Status Code: 400 Bad Request

{
  "detail": "ID 0 is not allowed! 😫"
}
```

---

## 6. Common HTTPException Examples

### Example 1: User Not Found
```python
@app.get("/user/{user_id}")
def get_user(user_id: int):
    user = database.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### Example 2: Unauthorized Access
```python
@app.get("/admin")
def admin_panel(is_admin: bool):
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"message": "Welcome Admin"}
```

### Example 3: Validation Error
```python
@app.post("/create")
def create_item(name: str):
    if len(name) < 3:
        raise HTTPException(status_code=422, detail="Name must be at least 3 characters")
    return {"name": name}
```

---

## 7. HTTP aur HTTPException ka Relationship

```
┌─────────────────────────────────────────┐
│         HTTP Protocol                    │
│  (Internet communication ka tarika)      │
│                                          │
│  - Status Codes (200, 400, 404, etc.)   │
│  - Request/Response Format               │
│  - Headers, Body, etc.                   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      HTTPException                       │
│  (FastAPI mein errors handle karne ka    │
│   tarika jo HTTP rules follow karta hai) │
│                                          │
│  - HTTP status codes use karta hai      │
│  - HTTP response format banata hai      │
│  - Proper error handling provide karta   │
└─────────────────────────────────────────┘
```

---

## 8. Summary

| Concept | Kya hai | Kyun use karte hain |
|---------|---------|---------------------|
| **HTTP** | Internet communication protocol | Browser aur server ke beech baat-cheet |
| **HTTP Status Codes** | 200, 400, 404 jaise codes | Batane ke liye request ka result kya hua |
| **HTTPException** | FastAPI ka error handling class | Proper HTTP errors bhejne ke liye |

### Key Points
1. **HTTP** = Communication ka protocol
2. **HTTP Status Codes** = Response ka result (success/error)
3. **HTTPException** = FastAPI mein errors ko HTTP standards ke saath handle karna

---

## 9. Best Practices

✅ **Karna chahiye:**
- Sahi status code use karein (400 for bad request, 404 for not found)
- Clear error messages dein
- HTTPException use karein errors ke liye

❌ **Nahi karna chahiye:**
- Simple return statements se errors bhejein
- Hamesha 200 status code bhejein (jab error ho)
- Confusing error messages dein

---

**Updated with HTTP and HTTPException guide** 🚀
