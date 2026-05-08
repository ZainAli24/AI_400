# User Tasks — Concepts & Notes

---

## Foreign Key — Concept

---

### Pehle Problem Samjho — Bina Foreign Key Ke

Maan lo tumhare paas 2 tables hain:

```
user table:
┌────┬──────────┐
│ id │  name    │
├────┼──────────┤
│  1 │  Zain    │
│  2 │  Sara    │
└────┴──────────┘

task table (bina foreign key):
┌────┬──────────────┬──────────┐
│ id │  title       │ owner_id │
├────┼──────────────┼──────────┤
│  1 │ "Buy milk"  │    1     │
│  2 │ "Read book" │    99    │  ← 99?? Koi user hi nahi is id ka!
│  3 │ "Exercise"  │  "ZAIN"  │  ← String?? id honi chahiye thi!
└────┴──────────────┴──────────┘
```

**Problem:** Koi bhi kuch bhi `owner_id` mein daal sakta hai — galat id, string, kuch bhi. DB rok nahi sakta.

---

### Foreign Key Kya Karta Hai

Foreign Key DB ko batata hai:

> **"Yeh column sirf wahi values le sakta hai jo dusre table ke is column mein exist karti hain"**

```
task table ka owner_id  →  sirf user table ke id ki values le sakta hai
```

```
user table:             task table:
┌────┬──────┐           ┌────┬─────────────┬──────────┐
│ id │ name │           │ id │   title     │ owner_id │
├────┼──────┤           ├────┼─────────────┼──────────┤
│  1 │ Zain │ ◄─────────│  1 │ "Buy milk" │    1     │ ✅ Zain exist karta hai
│  2 │ Sara │ ◄─────────│  2 │ "Read book"│    2     │ ✅ Sara exist karti hai
└────┴──────┘           │  3 │ "Exercise" │   99     │ ❌ DB reject karega!
                        └────┴─────────────┴──────────┘
                                              ↑
                                    99 user table mein nahi — ERROR!
```

---

### Real Life Analogy

> School mein attendance register mein sirf **registered students** ki entry ho sakti hai.
> Agar koi unknown naam daal do — office wala reject karega.
>
> **Foreign Key = Office wala** jo check karta hai ke naam register mein hai ya nahi.

---

### String Format Kyun? `"user.id"`

```python
owner_id: int = Field(foreign_key="user.id")
#                                  ↑    ↑
#                              table   column
#                               naam    naam
```

Yeh string DB ko instruction hai:

```
"user.id" ka matlab:
  → user   = task table ko user table se link karo
  → .id    = specifically user table ke 'id' column se match karo
```

Python class `User` hai — lekin **SQLite/PostgreSQL database mein table** lowercase `user` banta hai automatically. Isliye string mein `"user.id"` lowercase likhte hain.

---

### Foreign Key Ke Bina vs Saath — Comparison

```
BINA Foreign Key:
owner_id = 999   → DB ne allow kar diya ✅ (lekin 999 user exist nahi karta!)
owner_id = "abc" → DB ne allow kar diya ✅ (string?? id honi chahiye thi!)
owner_id = -5    → DB ne allow kar diya ✅ (negative id?? nonsense!)

SAATH Foreign Key:
owner_id = 1     → DB check kiya: user.id=1 exist karta hai? ✅ Allow
owner_id = 999   → DB check kiya: user.id=999 exist karta hai? ❌ Error! Reject
owner_id = "abc" → DB check kiya: string nahi chalega ❌ Error! Reject
```

---

### Tumhare Code Mein Exactly Kya Ho Raha Hai

```python
class Tasks(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = Field(default=None)
    status: str = Field(default="pending")
    owner_id: int = Field(foreign_key="user.id")  # ← Yeh line
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

```
owner_id: int                → sirf integer accept karega
Field(foreign_key="user.id") → aur sirf woh integer jo user table ke id mein exist karta ho
```

Matlab:

```
Task banana chahte ho jisme owner_id = 5?
DB pehle check karega: "user table mein koi user hai jiska id = 5?"
  → Haan hai → Task ban jayega ✅
  → Nahi hai → Error aa jayega, task nahi banega ❌
```

---

### Summary Table

| Cheez | Matlab |
|---|---|
| Foreign Key kya hai | Ek column jo dusre table ke column se link hota hai |
| Kya kaam karta hai | Galat/non-existent values ko DB level pe rokta hai |
| `"user.id"` kyun string | DB ko instruction dete hain: "user table ka id column" |
| `user` lowercase kyun | SQLModel Python class `User` ko DB mein `user` table banata hai |
| Benefit kya hai | Data consistency — orphan tasks nahi ban sakte (bina user ke) |

---

## Foreign Key — Mera Concept Verify (W3Schools se Confirmed)

---

### Mera Concept Jo Sahi Nikla

> `foreign_key="user.id"` ka matlab:
> **"Jo value `owner_id` mein aaye — pehle check karo ke woh value `user` table ke `id` column mein exist karti hai ya nahi. Hai toh accept karo, nahi hai toh reject karo."**

W3Schools ke exact words:
> **"The value has to exist in the parent table — otherwise the database rejects it."**

---

### Tumhare Code Pe Apply

```python
owner_id: int = Field(foreign_key="user.id")
```

```
Task create karo: owner_id = 1
DB check karega: user table mein id = 1 exist karta hai?
  ✅ Haan → Task DB mein save ho gaya

Task create karo: owner_id = 999
DB check karega: user table mein id = 999 exist karta hai?
  ❌ Nahi → Error! Task reject — DB mein nahi jayega
```

---

### Bonus — Dono Taraf Protection (Referential Integrity)

Foreign key sirf insert pe hi nahi — **delete pe bhi** check karta hai:

```
Zain (id=1) ka account delete karna chaho —
DB pehle check karega: tasks table mein koi task hai jiska owner_id = 1?
  ❌ Haan hain → User delete nahi hoga!
  → Pehle tasks delete karo, phir user delete hoga
```

Iska naam hai **Referential Integrity** — DB dono taraf se data consistent rakhta hai:

| Action | DB Kya Check Karta Hai |
|---|---|
| Task insert karo | `owner_id` user table mein exist karta hai? |
| User delete karo | Koi task us user ka exist karta hai? |
| Dono pass | ✅ Allow |
| Koi fail | ❌ Reject — Error |

---

## `.where()` Mein Multiple Conditions — AND Logic

---

### Mera Concept Jo Sahi Nikla

```python
session.exec(select(Tasks).where(Tasks.owner_id == user.id, Tasks.status == task_status)).all()
```

> **"Jahan `owner_id` aur `status` dono ek saath match karein — sirf wohi row return karo. Agar ek bhi false hai toh woh row skip."**

`.where()` mein **comma = AND** — matlab dono conditions ek saath true hongi tabhi row return hogi.

---

### Line by Line

```
select(Tasks)                    → tasks table se sab rows lao (draft)
.where(
    Tasks.owner_id == user.id,   → Condition 1: owner_id match karo
    Tasks.status == task_status  → Condition 2: status match karo
)                                → comma = AND — dono saath true honi chahiye
.all()                           → sab matching rows list mein return karo
```

---

### Table Pe Apply

```
tasks table:
┌────┬─────────────┬──────────┬───────────┐
│ id │   title     │ owner_id │  status   │
├────┼─────────────┼──────────┼───────────┤
│  1 │ "Buy milk"  │    1     │ pending   │  ✅ dono match (user.id=1, pending)
│  2 │ "Read book" │    2     │ pending   │  ❌ owner_id fail (Sara ka task)
│  3 │ "Exercise"  │    1     │ completed │  ❌ status fail (completed chahiye pending)
│  4 │ "Cook food" │    1     │ pending   │  ✅ dono match (user.id=1, pending)
└────┴─────────────┴──────────┴───────────┘

Zain (id=1) ne filter kiya task_status="pending":
Result: sirf row 1 aur row 4 → ["Buy milk", "Cook food"]
```

---

### SQL Se Comparison

SQLModel ka `.where(condition1, condition2)` exactly SQL ka AND hai:

```sql
SELECT * FROM tasks
WHERE owner_id = 1 AND status = 'pending'
```

```python
# SQLModel mein same kaam:
select(Tasks).where(Tasks.owner_id == user.id, Tasks.status == task_status)
```

---

### Summary

| Cheez | Matlab |
|---|---|
| `.where(c1, c2)` comma | AND — dono conditions saath true honni chahiye |
| Ek bhi false | Woh row return nahi hogi |
| `.all()` | Sab matching rows list mein return |
