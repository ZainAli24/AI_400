# FastAPI — Error Handling

---

## Status Codes — Poora Framework

HTTP requests ke responses teen categories mein aate hain:

```
2xx → Sab theek raha
4xx → Client ki galti (request galat thi)
5xx → Server ki galti (server se kuch toot gaya)
```

| Code | Naam | Kab use hota hai |
|---|---|---|
| `200` | OK | Normal success — FastAPI ka default |
| `201` | Created | Naya resource bana (POST ke liye) |
| `204` | No Content | Delete successful — kuch return nahi |
| `400` | Bad Request | Business rule fail — tumne manually pakda |
| `404` | Not Found | Resource exist nahi karta |
| `422` | Unprocessable Entity | Pydantic validation fail — automatic |
| `500` | Internal Server Error | Server crash — kabhi intentionally mat karo |

---

## Part 1 — `from fastapi import status` — Magic Numbers mat likho

### Problem — magic numbers

```python
raise HTTPException(status_code=404, detail="Not found")
#                              ^^^
#                    sirf number hai — developer ko yaad rakhna padta hai 404 kya hota hai
```

### Solution — named constants

```python
from fastapi import status

raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
#                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
#                    clearly pata chal raha hai — HTTP 404 Not Found
```

Commonly use hone wale constants:

```python
status.HTTP_200_OK
status.HTTP_201_CREATED
status.HTTP_204_NO_CONTENT
status.HTTP_400_BAD_REQUEST
status.HTTP_404_NOT_FOUND
status.HTTP_422_UNPROCESSABLE_ENTITY
status.HTTP_500_INTERNAL_SERVER_ERROR
```

---

## Part 2 — Decorator `status_code` vs `HTTPException` — Farq

### Ye confusion bahut common hai

```python
@app.post("/tasks", status_code=status.HTTP_201_CREATED)  # ← decorator mein
def create_task(task: TaskCreate):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)  # ← exception mein
```

### Simple rule:

```
decorator status_code  → SUCCESS pe kaunsa code jaayega
HTTPException          → ERROR pe kaunsa code jaayega
```

### Practical example:

```python
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):

    if task.title.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title empty nahi ho sakta"
        )
        # ↑ galti hui — 400 throw hoga, decorator wala 201 ignore hoga

    return new_task
    # ↑ galti nahi hui — decorator wala 201 return hoga
```

### `raise HTTPException(status_code=201)` — Ye WRONG hai

```python
# ❌ WRONG
raise HTTPException(status_code=201, detail="Created")
# HTTPException sirf errors ke liye hoti hai — 4xx, 5xx
# 201 success code hai — isko decorator mein likho, HTTPException mein nahi

# ✅ CORRECT
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    return new_task
```

---

## Part 3 — 400 vs 422 — Bahut Important Farq

### 422 — Pydantic khud pakad leta hai (automatic)

Tumhe kuch nahi karna — FastAPI automatically 422 deta hai:

```python
class TaskCreate(BaseModel):
    title: str = Field(min_length=3)
    age: int

# Ye sab automatically 422 denge:
{"title": "Hi"}       # min_length=3 fail
{"age": "abc"}        # int chahiye tha, str diya
{}                    # required field missing
```

### 400 — Tumhe khud pakad karna hoga (manual)

Data Pydantic se pass ho gaya — type sahi hai — lekin business rule fail hai:

```python
@app.post("/tasks")
def create_task(task: TaskCreate):

    # title="   " — ye str hai, Pydantic pass kar dega
    # lekin sirf spaces wala title valid nahi hona chahiye
    if task.title.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title sirf spaces se nahi ban sakta"
        )

    # status Pydantic ne check nahi kiya — tumhe karna hai
    allowed = ["pending", "in_progress", "completed"]
    if task.status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{task.status}' invalid hai. Allowed: {allowed}"
        )

    return new_task
```

### One-line rule:

```
422 → FastAPI/Pydantic ne pakda  — type galat, field missing
400 → Tumne pakda                — business rule galat
```

---

## Part 4 — Error Messages Kaise Likhein

### Bura message:

```python
detail="Error"        # kya error? kahan? kyun?
detail="Not found"    # kya nahi mila?
```

### Acha message — specific aur context ke saath:

```python
detail=f"Task with id {task_id} not found"
detail=f"Status '{value}' invalid — sirf pending, in_progress, completed allowed"
```

### Best — structured format (agents aur debugging ke liye):

```python
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail={
        "code": "TASK_NOT_FOUND",
        "message": f"Task with id {task_id} not found",
        "task_id": task_id
    }
)
```

### Security rule — yeh kabhi mat karo:

```python
# ❌ internal info kabhi bahar mat bhejo
detail=f"Database error: {str(e)}"
detail=f"SQL failed: {sql_query}"
detail=f"File path: {file_path}"
```

---

## Part 5 — 3 Common Mistakes

### Mistake 1 — `raise` bhool gaye

```python
# ❌ WRONG — kuch nahi hoga, code chalta rahega
HTTPException(status_code=404, detail="Not found")

# ✅ CORRECT
raise HTTPException(status_code=404, detail="Not found")
```

### Mistake 2 — Error ko 200 ke saath return karna

```python
# ❌ WRONG
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = find_task(task_id)
    if not task:
        return {"error": "not found"}   # ← 200 status ke saath error!

# ✅ CORRECT
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = find_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

Agents aur clients **pehle status code check karte hain** — agar 200 aaya toh woh samjhenge sab theek hai, error message andar ignore ho jaayega.

### Mistake 3 — Python exception escape ho jaaye

```python
# ❌ WRONG — task_id exist nahi karta toh Python KeyError dega → 500 banta hai
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    del tasks[task_id]   # KeyError crash → server ki galti lagna shuru

# ✅ CORRECT — pehle check karo, apna error throw karo
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    del tasks[task_id]
    return None
```

500 ka matlab hota hai — **server ki galti** — agent retry karta hai bar bar.
Agar logic ki galti hai toh 400 ya 404 do — agent samjhe ga retry nahi karna.

---

## Summary

```
status module     → magic numbers ki jagah named constants use karo
decorator         → SUCCESS pe kaunsa code jaayega
HTTPException     → ERROR pe kaunsa code jaayega
400               → business rule fail — tumne manually pakda
422               → Pydantic ne pakda — automatic
raise likhna      → kabhi mat bhoolo
200 + error       → kabhi mat karo
Python exceptions → escape mat hone do — 500 se bachao
```
