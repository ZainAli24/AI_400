# User Management — Concepts

---

## `select().where().first()` — Filtered Single Row Query

```python
session.exec(select(User).where(User.email == user.email)).first()
```

| Part | Matlab |
|---|---|
| `select(User)` | User table mein jao |
| `.where(User.email == user.email)` | sirf woh row dhundo jahan email match kare |
| `session.exec(...)` | ye query execute karo — database ko bhejo |
| `.first()` | jo pehli matching row mile — sirf woh ek lao |

---

### `.first()` vs `.all()` — Farq

```python
.all()    # → list return karta hai — [user1, user2, ...]
.first()  # → sirf ek object return karta hai — user1  (ya None agar koi na mile)
```

---

### Email ke liye `.first()` kyun sahi hai?

Email **unique hoti hai** — ek email se sirf ek hi user ho sakta hai. Toh saari matching rows list mein lene ki zaroorat nahi — sirf pehli (aur ek hi) row chahiye.

```python
# .all() se milega:   [<User id=1 email="zain@gmail.com">]  ← list mein
# .first() se milega:  <User id=1 email="zain@gmail.com">   ← direct object
```

`.first()` directly object deta hai — phir us object ki properties directly access kar sakte ho:

```python
user = session.exec(select(User).where(User.email == user.email)).first()
print(user.name)    # ✅ direct access
print(user.email)   # ✅ direct access
```

---

> **Email se filter karo, pehli (aur sirf ek) matching row lao — `.first()` direct object deta hai, `.all()` list deta hai.**

---

## `default_factory` — Automatic Field Value

`created_at` dene ki zaroorat nahi — `default_factory` hone ki wajah se class khud value set kar deti hai:

```python
created_at: datetime = Field(default_factory=datetime.now)
#                             ↑
#                      jab bhi naya User object banega
#                      automatically datetime.now() call hoga
```

Toh yeh line bilkul sahi hai:

```python
db_user = User(name=user.name, email=user.email, password=user.password)
#                                              created_at automatically set hoga
#                                              id bhi automatically None → DB auto-generate karega
```

Object bante waqt internally yeh hota hai:

```
User(name="Zain", email="z@z.com", password="hash...")
        ↓
id         = None            (DB khud generate karega)
created_at = datetime.now()  (class khud set karegi)
```

### `default` vs `default_factory` — Farq

| | Kab use hota hai |
|---|---|
| `default=None` | Static value — hamesha wahi value |
| `default_factory=datetime.now` | Dynamic value — har baar fresh call hota hai |

> **`default_factory` wali field manually dene ki zaroorat nahi — object banate waqt class khud set kar deti hai.**

---
