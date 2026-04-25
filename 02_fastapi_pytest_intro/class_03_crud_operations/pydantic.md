# Pydantic — Field() Constraints

---

## Field() — Kya Hai?

Pydantic mein jab tum sirf type likhte ho:
```python
title: str
```
Ye sirf check karta hai ke **string hai ya nahi** — koi aur rule nahi.

`Field()` se tum **extra rules** laga sakte ho:
```python
title: str = Field(min_length=3, max_length=100)
```

---

## Part 1 — String Constraints

```python
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100)
```

| Parameter | Matlab | Example |
|---|---|---|
| `min_length=3` | kam se kam 3 characters | `"Hi"` → ❌ 422 |
| `max_length=100` | zyada se zyada 100 characters | `"a" * 101` → ❌ 422 |

```python
# Ye sab fail honge — 422 aayega:
{"title": "Hi"}        # sirf 2 chars — min_length fail
{"title": "a" * 200}   # 200 chars — max_length fail

# Ye pass hoga:
{"title": "Learn FastAPI"}  # 13 chars — ✅
```

---

## Part 2 — Number Constraints

Numbers ke liye alag parameters hain:

```python
class Product(BaseModel):
    price: float = Field(gt=0, lt=10000)   # greater than, less than
    quantity: int = Field(ge=1, le=100)    # greater or equal, less or equal
```

| Parameter | Matlab | Example |
|---|---|---|
| `gt=0` | 0 se **bada** hona chahiye | `0` → ❌, `0.1` → ✅ |
| `lt=10000` | 10000 se **chhota** hona chahiye | `10000` → ❌, `9999` → ✅ |
| `ge=1` | 1 **ya usse bada** | `0` → ❌, `1` → ✅ |
| `le=100` | 100 **ya usse chhota** | `101` → ❌, `100` → ✅ |

---

## Part 3 — Optional Field with Field()

```python
description: str | None = Field(None, max_length=500)
#                                ^^^
#                            default value = None (optional hai)
```

`Field()` ka pehla argument **default value** hota hai:

| Syntax | Matlab |
|---|---|
| `Field(None, ...)` | field optional hai, default `None` |
| `Field("pending", ...)` | default `"pending"` hai |
| `Field(...)` ya `Field(min_length=3)` | field **required** hai — koi default nahi |

```python
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3)        # REQUIRED — dena hi padega
    status: str = Field("pending")               # OPTIONAL — default "pending"
    description: str | None = Field(None)        # OPTIONAL — default None

# Sirf title diya — valid ✅
{"title": "Learn FastAPI"}
# → title = "Learn FastAPI"
# → status = "pending"   (default)
# → description = None   (default)

# Kuch nahi diya — 422 ❌
{}
# → title Field required error
```

---

## Part 4 — `Literal` — Sirf Specific Values Allow Karo

```python
from typing import Literal

class TaskCreate(BaseModel):
    priority: Literal["low", "medium", "high"] = "medium"
```

`Literal` ka matlab — **in 3 values ke ilawa kuch bhi nahi chalega:**

```python
{"priority": "low"}      # ✅
{"priority": "medium"}   # ✅
{"priority": "high"}     # ✅
{"priority": "urgent"}   # ❌ 422
{"priority": "LOW"}      # ❌ 422 — case sensitive hai
# Field nahi diya?       # ✅ default "medium" lag jata hai
```

---

## Part 5 — Sab Milake Ek Model

```python
from pydantic import BaseModel, Field
from typing import Literal

class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str | None = Field(None, max_length=500)
    priority: Literal["low", "medium", "high"] = "medium"
```

**Kya hoga jab ye data aaye:**

```python
# ✅ Valid — pass hoga
{"title": "Learn FastAPI", "priority": "high"}

# ❌ 422 — title too short
{"title": "Hi", "priority": "low"}

# ❌ 422 — priority invalid value
{"title": "Learn FastAPI", "priority": "urgent"}

# ✅ Valid — description optional hai, priority default "medium" lagega
{"title": "Learn FastAPI"}
```

---

## Summary — Field() ke Rules

```
type hint   → kya type chahiye (str, int, float)
Field()     → kitna bada/chota, kya values allowed
Literal[]   → exactly kaunsi values allowed hain
= None      → optional field
= "medium"  → default value
```

<br>

---

## `->` vs `response_model=` — Response Filtering

### Newer FastAPI (0.89+) mein `->` bhi filter karta hai

Return type annotation `-> TaskResponse` bhi response model ki tarah kaam karta hai — filtering hoti hai.

**Proof:**
- Function ke andar `internal_flag`, `debug_info`, `password` tha
- `-> TaskResponse` lagaya
- Swagger response mein sirf `id`, `title`, `status` aaya ✅

### Actual Farq:

| | `-> TaskResponse` | `response_model=TaskResponse` |
|---|---|---|
| Filtering? | ✅ hoti hai (newer FastAPI) | ✅ hoti hai |
| Validation? | ✅ | ✅ |
| Extra options? | ❌ nahi milte | ✅ milte hain |

`response_model=` ke saath **extra control** milta hai:

```python
@app.post("/tasks",
    response_model=TaskResponse,
    response_model_exclude_unset=True,      # sirf set fields return karo
    response_model_include={"id", "title"}, # sirf ye fields
    response_model_exclude={"status"}       # ye field hata do
)
```

`->` se ye extra options nahi milte.

> **`-> TaskResponse`** — newer FastAPI mein filtering karta hai, simple cases ke liye kaafi hai.
> **`response_model=`** — jab extra control chahiye (include/exclude specific fields), tab use karo.

<br>

---

## `exclude_unset` — Kya Matlab Hai?

**`unset`** matlab — jo fields user ne request mein **bheje hi nahi.**

```python
class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
```

User sirf yeh bhejta hai:
```json
{"status": "completed"}
```

Pydantic model ke andar kya hota hai:

```python
task_update.title        # → None   ← user ne nahi bheja, default laga
task_update.description  # → None   ← user ne nahi bheja, default laga
task_update.status       # → "completed"  ← user ne bheja
```

`title` aur `description` **unset** hain — user ne touch nahi kiya inhe.

---

## Part 6 — `model_dump(exclude_unset=True)` — PATCH ka Standard Pattern

### Problem — bina `exclude_unset` ke

```python
task.update(task_update.model_dump())
# model_dump() returns:
# {"title": None, "description": None, "status": "completed"}
```

**Result — data destroy ho gaya:**
```python
{"id": 1, "title": None, "description": None, "status": "completed"}
#                  ^^^^              ^^^^
#         user ne ye nahi diya tha, par None ho gaye!
```

### Solution — `exclude_unset=True`

```python
update_data = task_update.model_dump(exclude_unset=True)
# → {"status": "completed"}   ← sirf jo user ne bheja

task.update(update_data)
# → {"id": 1, "title": "Learn FastAPI", "description": "Important", "status": "completed"}
#              title aur description safe rahe ✅
```

### Teen Cases

```python
# Case 1 — sirf status:
# Request: {"status": "completed"}
# update_data = {"status": "completed"}
# title aur description safe ✅

# Case 2 — sirf title:
# Request: {"title": "Learn Pydantic"}
# update_data = {"title": "Learn Pydantic"}
# status aur description safe ✅

# Case 3 — sab kuch:
# Request: {"title": "New", "status": "done", "description": "Updated"}
# update_data = {"title": "New", "status": "done", "description": "Updated"}
# sab update ✅
```

### One-line Rule

```
model_dump()                   → sari fields return karta hai (None bhi)
model_dump(exclude_unset=True) → sirf user ne jo bheja wo return karta hai
```

---

## Part 7 — `model_dump(exclude_unset=True)` vs `response_model_exclude_unset=True`

### Common Confusion

Ye dono similar lagte hain lekin **bilkul alag jagah kaam karte hain.**

```
model_dump(exclude_unset=True)       → INPUT filter karta hai  (kya UPDATE hoga)
response_model_exclude_unset=True    → OUTPUT filter karta hai (kya RETURN hoga)
```

### `response_model_exclude_unset=True` kya karta hai?

Response mein se woh fields hata deta hai jo default value pe hain:

```python
@app.patch("/tasks/{task_id}", response_model=TaskResponse, response_model_exclude_unset=True)
def update_task(task_id: int, ...):
    return {"id": 1, "title": "Learn FastAPI"}

# Response aayega: {"id": 1, "title": "Learn FastAPI"}
# status aur description response mein nahi aayenge — unset hain
```

### Ye PATCH ka bug solve nahi karta

```python
@app.patch("/tasks/{task_id}", response_model_exclude_unset=True)
def update_task(task_id: int, task_update: TaskUpdate):

    update_data = task_update.model_dump()  # ← exclude_unset nahi lagaya
    # {"title": None, "description": None, "status": "completed"}

    task.update(update_data)  # ← title aur description STILL None ho gaye!

    return task  # response clean lag raha hai — lekin data pehle hi kharab ho chuka
```

`response_model_exclude_unset=True` ne sirf **response** clean kiya — data toh already corrupt ho chuka tha.

### Flow Diagram

```
User Request
     ↓
[model_dump(exclude_unset=True)]   ← input filter — sirf bheje fields nikalo
     ↓
Database / Dict update hota hai
     ↓
[response_model_exclude_unset=True] ← output filter — sirf set fields return karo
     ↓
User ko Response
```

### Summary Table

| | `model_dump(exclude_unset=True)` | `response_model_exclude_unset=True` |
|---|---|---|
| Kahan kaam karta hai | **Input** (request body) | **Output** (response) |
| Kya karta hai | Sirf bheje fields nikalta hai update ke liye | Sirf set fields response mein bhejta hai |
| PATCH bug solve karta hai? | ✅ haan | ❌ nahi |
| Kahan likhte hain | Function ke andar | Route decorator mein |

> **PATCH mein `model_dump(exclude_unset=True)` zaroori hai** — `response_model_exclude_unset` iska replacement nahi hai.
