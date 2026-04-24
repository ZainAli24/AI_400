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
