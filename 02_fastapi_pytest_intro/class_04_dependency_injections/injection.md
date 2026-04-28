# FastAPI — Dependency Injection & Caching Concepts

---

## 1. Dependency Injection (DI) kya hai?

**Simple definition:** Jab ek function ko kisi doosre function ka result chahiye hota hai — to FastAPI khud us doosre function ko pehle chalata hai aur result deta hai. Ye kaam manually nahi karna padta.

### Without DI (manual way):
```python
@app.get("/hello")
def greet():
    app_data = get_app_data()   # khud call karna padta hai
    return {"app_name": app_data["app_name"]}
```

### With DI (FastAPI ka tarika):
```python
@app.get("/hello")
def greet(app_data: dict = Depends(get_app_data)):  # FastAPI khud call karta hai
    return {"app_name": app_data["app_name"]}
```

---

## 2. `Depends()` ka flow — Step by Step

```
User → /hello request bhejta hai
         ↓
FastAPI route dhoondhta hai
         ↓
FastAPI dekhta hai: "is function mein Depends(get_app_data) hai"
         ↓
FastAPI pehle get_app_data() chalata hai
         ↓
get_app_data() ka result app_data variable mein daal deta hai
         ↓
greet(app_data=...) function chalata hai
         ↓
Response return
```

**Order hamesha:** Dependency function PEHLE → Route function BAAD MEIN

---

## 3. Yield wali Dependency (Cleanup ke saath)

Jab resource use karne ke baad clean up bhi karna ho — `yield` use karte hain.

```python
import tempfile
import os

def get_temp_file():
    fd, path = tempfile.mkstemp()      # temporary file create ki
    file = os.fdopen(fd, "w")          # file open ki likhne ke liye
    try:
        yield file                     # file route function ko de di
    finally:
        file.close()                   # route khatam hone ke baad — file band
        os.unlink(path)                # aur delete

@app.get("/fileworking")
def do_work_in_file(file=Depends(get_temp_file)):
    file.write("MY NAME IS ZAIN")
    return {"Status": "Processed"}
```

### Yield wala flow:
```
Request aai
    ↓
get_temp_file() chali — file bani
    ↓
yield — file route function ko mili
    ↓
do_work_in_file() chali — file mein likha
    ↓
Response gaya
    ↓
finally block chala — file band aur delete  ← CLEANUP
```

---

## 4. `@lru_cache` — Caching Concept

### Problem (without cache):
```python
def get_data_from_db():
    print("-------- call DataBase ----------")
    return {"app_name": "Task_API", "debug": True}
```
Har request pe ye function dobara chalega — 1000 requests = 1000 baar database call. Slow aur expensive.

### Solution (with cache):
```python
from functools import lru_cache

@lru_cache
def get_data_from_db():
    print("-------- call DataBase ----------")
    return {"app_name": "Task_API", "debug": True}

@app.get("/data")
def get_data(data: dict = Depends(get_data_from_db)):
    app_name = data["app_name"]
    return f"APP_NAME IS : {app_name}"
```
Pehli request pe chalta hai. Baad mein — memory se result milta hai seedha.

---

## 5. `@lru_cache` Behind the Scene — Asli kaam

### Decorator kya karta hai?

```python
# Aap ye likhte ho:
@lru_cache
def get_data_from_db():
    ...

# Python actually ye karta hai:
get_data_from_db = lru_cache(get_data_from_db)
```

**Matlab:** `get_data_from_db` naam ab original function ki taraf nahi — balke **lru_cache ke wrapper** ki taraf point karta hai.

FastAPI jab `get_data_from_db()` call karta hai — wo wrapper call hota hai, original function nahi.

---

## 6. Poora Correct Flow — 1st aur 2nd Request

### 1st Request `/data`:
```
FastAPI: "Depends(get_data_from_db) hai — call karo"
    ↓
[LRU_CACHE WRAPPER call hota hai — original function nahi]
    ↓
Wrapper: "kya pehle ye call aaya tha?"
Wrapper: "NAHI — pehli baar hai"
    ↓
Wrapper original function body chalata hai:
    → print("-------- call DataBase ----------")  ← TERMINAL MEIN DIKHTA HAI
    → result banta hai
    → result MEMORY MEIN SAVE hota hai
    ↓
FastAPI ko result milta hai
    ↓
get_data(data=...) chalta hai → Response
```

### 2nd Request `/data` (aur uske baad sab):
```
FastAPI: "Depends(get_data_from_db) hai — call karo"
    ↓
[LRU_CACHE WRAPPER call hota hai]
    ↓
Wrapper: "kya pehle ye call aaya tha?"
Wrapper: "HAAN — memory mein result hai"
    ↓
Original function body NAHI CHALTI:
    → print() NAHI DIKHTA terminal mein
    → memory se saved result seedha return
    ↓
FastAPI ko result milta hai
    ↓
get_data(data=...) chalta hai → Response
```

---

## 7. Common Confusion — Cleared

> **Confusion:** "FastAPI get_data_from_db ko call karta hai lekin data toh cache ke paas hai — to kaise milta hai?"

> **Answer:** FastAPI ko pata hi nahi ke cache hai ya nahi. Uske liye sirf ek function hai `get_data_from_db`. Wo usse call karta hai. Lekin wo naam ab **lru_cache wrapper** ka hai. Wrapper andar decide karta hai — original function chalana hai ya memory se dena hai.

```
FastAPI
    ↓ call karta hai
get_data_from_db()   ← YE NAAM AB WRAPPER KA HAI
    ↓
[WRAPPER ANDAR DECIDE KARTA HAI]
    ├── Pehli baar → original function chalao → result save karo
    └── Dobara → memory se do seedha
```

---

## 8. Kab `@lru_cache` use karo

| Situation | Use karo? |
|-----------|-----------|
| Config/settings file padhna | Haan |
| Database connection banana | Haan |
| API key / secret load karna | Haan |
| Har request ke liye alag data (user ID, token) | Nahi |
| Request body ya query params pe depend kare | Nahi |

---

## 9. Quick Test — Cache verify karo

```bash
uvicorn dep:app --reload
```

Browser mein `/data` baar baar reload karo:

| Request # | Terminal mein print dikhega? |
|-----------|------------------------------|
| 1st       | Haan — "call DataBase"       |
| 2nd       | Nahi                         |
| 3rd       | Nahi                         |
| 100th     | Nahi                         |

Yehi proof hai ke `@lru_cache` kaam kar raha hai.

---

## 10. Summary — Ek Nazar Mein

| Concept | Matlab |
|---------|--------|
| `Depends(func)` | FastAPI pehle `func` chalata hai, result route function ko deta hai |
| `yield` dependency | Resource use karo, kaam khatam hone ke baad cleanup automatic |
| `@lru_cache` | Function pehli baar chalao, result yaad rakho, dobara mat chalao |
| Wrapper | `@lru_cache` original function ki jagah ek wrapper bana deta hai — FastAPI wrapper ko call karta hai |

---

---

# Complete Example: Request Logger

---

## 11. Request Logger — Kya Hai aur Kyun?

**Real-life analogy:** Hotel mein receptionist har aane jaane wale ka record rakhta hai — kaun aaya, kab aaya, kitna waqt ruka. Request Logger bilkul yehi kaam HTTP requests ke liye karta hai.

Ye dependency:
- Request ke **shuru hone ka waqt** record karti hai
- **Method** (GET/POST) aur **URL path** save karti hai
- Route ka kaam hone ke baad **kitna time laga** calculate karke print karti hai

---

## 12. Complete Code

```python
from fastapi import FastAPI, Depends, Request   # Line 1
from datetime import datetime                    # Line 2

app = FastAPI()                                  # Line 3

def get_request_logger(request: Request):        # Line 4
    start = datetime.now()                       # Line 5
    method = request.method                      # Line 6
    path = request.url.path                      # Line 7
    print(f"[{start}] {method} {path} - started")          # Line 8
    yield {"method": method, "path": path, "start": start}  # Line 9
    end = datetime.now()                                     # Line 10
    duration = (end - start).total_seconds()                 # Line 11
    print(f"[{end}] {method} {path} - completed in {duration:.3f}s")  # Line 12

@app.get("/tasks")                                           # Line 13
def list_tasks(log: dict = Depends(get_request_logger)):     # Line 14
    return {"tasks": [], "logged_path": log["path"]}         # Line 15

@app.post("/tasks")                                          # Line 16
def create_task(log: dict = Depends(get_request_logger)):    # Line 17
    return {"id": 1, "logged_method": log["method"]}         # Line 18
```

---

## 13. Line by Line Explanation

**Line 1:**
```python
from fastapi import FastAPI, Depends, Request
```
Teesri cheez `Request` nai import hui. Ye FastAPI ki built-in class hai jo **incoming HTTP request ki saari info rakhti hai** — method (GET/POST), URL, headers, body sab kuch.

---

**Line 2:**
```python
from datetime import datetime
```
Python ki built-in `datetime` library se `datetime` class import ki — taake `datetime.now()` se current time pata kar sakein.

---

**Line 4:**
```python
def get_request_logger(request: Request):
```
Dependency function. Parameter `request: Request` — ye FastAPI ka **magic** hai. Aapne khud kuch pass nahi kiya. FastAPI dekhta hai ke type `Request` hai — toh **khud hi current HTTP request ka object bana ke inject kar deta hai.**

---

**Line 5:**
```python
start = datetime.now()
```
`datetime.now()` is waqt ka exact date aur time deta hai — jaise `2026-04-28 14:30:00.123456`. Ye `start` mein save hua — matlab **request aane ka waqt.**

---

**Line 6:**
```python
method = request.method
```
`request.method` se pata chalta hai ke user ne kaisa request bheja — `"GET"`, `"POST"`, `"DELETE"` etc.
> `/tasks` pe GET request aaye toh `method = "GET"`

---

**Line 7:**
```python
path = request.url.path
```
`request.url.path` se URL ka sirf path wala hissa milta hai.
> `http://localhost:8000/tasks` mein se sirf `/tasks` milega.

---

**Line 8:**
```python
print(f"[{start}] {method} {path} - started")
```
Request ke shuru hote hi terminal mein pehli line print hoti hai. `f"..."` matlab **f-string** — `{}` ke andar variable ki value seedha aa jaati hai.

Terminal output:
```
[2026-04-28 14:30:00.123] GET /tasks - started
```

---

**Line 9:**
```python
yield {"method": method, "path": path, "start": start}
```
**`yield`** — function yahan **ruk jaata hai** aur ek dictionary route function ko de deta hai.

Dictionary mein:
- `method` — GET ya POST
- `path` — /tasks etc
- `start` — request ka start time

> Yaad karo: `yield` matlab "ye lo use karo, aur jab kaam khatam ho toh wapas aana mere paas"

---

**Line 10:**
```python
end = datetime.now()
```
Route function ka kaam khatam hone ke baad control yahan wapas aata hai. Ab **request khatam hone ka waqt** `end` mein save.

---

**Line 11:**
```python
duration = (end - start).total_seconds()
```
`end - start` = do datetime values ka farq — ye ek `timedelta` object deta hai.
`.total_seconds()` us farq ko seconds mein convert karta hai.

> Jaise end `14:30:00.125` aur start `14:30:00.123` — farq = `0.002 seconds`

---

**Line 12:**
```python
print(f"[{end}] {method} {path} - completed in {duration:.3f}s")
```
Request complete hone ke baad doosri line terminal mein print.

`{duration:.3f}` — **float formatting**: `.3f` matlab teen decimal places tak dikhao.
> `0.002456` → `0.002` ban jaayega

Terminal output:
```
[2026-04-28 14:30:00.125] GET /tasks - completed in 0.002s
```

---

**Lines 13–15:**
```python
@app.get("/tasks")
def list_tasks(log: dict = Depends(get_request_logger)):
    return {"tasks": [], "logged_path": log["path"]}
```
`Depends(get_request_logger)` — logger dependency pehle chalegi, `yield` se jo dict mili wo `log` mein aayegi. Route function `log["path"]` use kar sakta hai.

---

**Lines 16–18:**
```python
@app.post("/tasks")
def create_task(log: dict = Depends(get_request_logger)):
    return {"id": 1, "logged_method": log["method"]}
```
Alag route — POST `/tasks`. Lekin **same dependency** use ki. Ek dependency — kai routes mein reuse. Yehi DI ka asli faida hai — code ek jagah, use har jagah.

---

## 14. Poora Flow — Step by Step

```
USER → GET /tasks request bhejta hai
            ↓
FASTAPI: "is route mein Depends(get_request_logger) hai"
            ↓
FASTAPI: Request object khud banata hai aur get_request_logger() ko deta hai
            ↓
get_request_logger() chalta hai:
    → start = datetime.now()              "14:30:00.123"
    → method = "GET"
    → path  = "/tasks"
    → print("GET /tasks - started")      ← TERMINAL: 1st LINE
    → YIELD — dict de deta hai, RUKA REHTA HAI
            ↓
FASTAPI: log = {"method":"GET", "path":"/tasks", "start":...}
            ↓
list_tasks(log=...) chalta hai:
    → return {"tasks": [], "logged_path": "/tasks"}
            ↓
RESPONSE USER KO GAYA
            ↓
CONTROL WAPAS get_request_logger mein — yield ke BAAD se
    → end = datetime.now()               "14:30:00.125"
    → duration = 0.002s
    → print("GET /tasks - completed in 0.002s")  ← TERMINAL: 2nd LINE
```

**Terminal mein dono lines:**
```
[2026-04-28 14:30:00.123] GET /tasks - started
[2026-04-28 14:30:00.125] GET /tasks - completed in 0.002s
```

Pehli line `yield` se **PEHLE** — request aate hi.
Doosri line `yield` ke **BAAD** — response jane ke baad.

---

## 15. Key Takeaways — Request Logger

| Cheez | Matlab |
|-------|--------|
| `request: Request` | FastAPI khud HTTP request object inject karta hai — aapko kuch pass nahi karna |
| `datetime.now()` | Is waqt ka exact time |
| `request.method` | GET / POST / DELETE etc |
| `request.url.path` | /tasks ya /data etc |
| `yield` se pehle | Route chalane se PEHLE kaam — logging start |
| `yield` se baad | Route khatam hone ke BAAD kaam — duration calculate + logging end |
| `{value:.3f}` | Float ko teen decimal places tak format karo |
| Same dependency, 2 routes | Code ek jagah likho — kai routes mein reuse karo |

---

---

# Try With AI — Teeno Prompts ke Concepts

---

## 16. Dependency Chain — Dependency ke andar Dependency

### Real-Life Analogy

Restaurant mein:
- **Chef** ko pehle **Recipe Book** chahiye
- **Waiter** ko pehle **Chef** chahiye (jo already Recipe Book le chuka hai)

Waiter seedha Recipe Book nahi maangta — Chef se kaam karta hai. **Yehi Dependency Chain hai.**

---

### Problem — Bina Chain ke

```python
def get_config():
    return {"db_url": "sqlite:///tasks.db", "debug": True}

def get_logger():
    config = get_config()   # manually call — DI ka faida nahi, tight coupling
    return {"level": "DEBUG" if config["debug"] else "INFO"}
```

---

### Solution — `Depends()` ke andar `Depends()`

```python
from fastapi import FastAPI, Depends

app = FastAPI()

# Step 1: Pehli dependency — config
def get_config():
    print("Config load ho rahi hai...")
    return {"db_url": "sqlite:///tasks.db", "debug": True}

# Step 2: Doosri dependency — logger jo config pe depend karti hai
def get_logger(config: dict = Depends(get_config)):   # chain yahan bani
    level = "DEBUG" if config["debug"] else "INFO"
    print(f"Logger bana — level: {level}")
    return {"level": level, "db": config["db_url"]}

# Step 3: Route jo logger pe depend karta hai
@app.get("/status")
def get_status(log: dict = Depends(get_logger)):
    return {"logger_level": log["level"], "db": log["db"]}
```

---

### Chain ka Flow

```
User → GET /status

FastAPI: "get_status ko get_logger chahiye"
    ↓
FastAPI: "get_logger ko get_config chahiye"
    ↓
FastAPI pehle get_config() chalata hai:
    → {"db_url": "sqlite:///tasks.db", "debug": True}
    ↓
FastAPI us result ko get_logger(config=...) mein deta hai:
    → level = "DEBUG"
    → {"level": "DEBUG", "db": "sqlite:///tasks.db"}
    ↓
FastAPI us result ko get_status(log=...) mein deta hai:
    → return {"logger_level": "DEBUG", "db": "sqlite:///tasks.db"}
    ↓
Response user ko milta hai
```

**FastAPI khud puri chain resolve karta hai — aapko manually kuch call nahi karna.**

---

### Key Rules

| Rule | Detail |
|------|--------|
| Kitni bhi gehri chain ho sakti hai | A → B → C → D — FastAPI handle karta hai |
| Order automatic | FastAPI sab se andar wali dependency pehle chalata hai |
| Reuse | `get_config` ek jagah likhi — kai dependencies use kar sakti hain |

---

## 17. Testing Dependencies — `app.dependency_overrides`

### Real-Life Analogy

Exam mein **mock test** hota hai — real exam jaisi setting lekin asli marks nahi lagte. Testing mein bhi **real database ya real config** use nahi karte — **fake (mock) version** use karte hain.

---

### Problem — Real Dependency Testing mein kyun buri hai?

```python
def get_config():
    with open("config.json") as f:   # real file se padhta hai
        return json.load(f)          # test mein file nahi hogi — test fail
```

Ya agar database connection ho — test mein real DB hit hogi — slow aur risky.

---

### Solution — `app.dependency_overrides`

FastAPI mein ek built-in dictionary hai: `app.dependency_overrides`

Iska kaam: **"is dependency ki jagah TEST mein ye fake function use karo"**

```python
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

app = FastAPI()

# Original dependency (real config)
def get_config():
    return {"db_url": "sqlite:///real.db", "debug": False}

@app.get("/info")
def get_info(config: dict = Depends(get_config)):
    return {"db": config["db_url"]}


# ══ TEST FILE ══

# Fake dependency — test ke liye
def fake_config():
    return {"db_url": "sqlite:///test.db", "debug": True}

def test_get_info():
    # Real get_config ki jagah fake_config lagao
    app.dependency_overrides[get_config] = fake_config

    client = TestClient(app)
    response = client.get("/info")

    assert response.json() == {"db": "sqlite:///test.db"}

    # Test khatam — override hatao
    app.dependency_overrides.clear()
```

---

### `dependency_overrides` ka Flow

```
Normal Request:
    /info → FastAPI → get_config() chalta hai → real config

Test Request:
    /info → FastAPI → dependency_overrides check karta hai
                ↓
         "get_config ka override hai — fake_config use karo"
                ↓
         fake_config() chalta hai → test config
                ↓
         get_info(config=fake config) → response
```

---

### Simple Breakdown

```python
app.dependency_overrides[get_config] = fake_config
#        ↑                   ↑              ↑
#   ye dictionary      original      iski jagah
#                      dependency    ye use karo
```

| Cheez | Matlab |
|-------|--------|
| `dependency_overrides` | FastAPI ki dictionary — override store hoti hain |
| Key | Original dependency function |
| Value | Fake/mock function jo test mein use hogi |
| `.clear()` | Test ke baad sab overrides hatao |

---

## 18. Class as Dependency — `TaskService` Class

### Real-Life Analogy

Abhi tak hum **single kaam wale functions** use kar rahe the — ek worker jo sirf ek kaam karta hai. Ab socho ek **poora department** — jisme alag alag capability hai: list karo, create karo, delete karo. Ye department ek **Class** hai.

---

### Functions vs Class

```python
# Function — sirf ek cheez return karta hai
def get_config():
    return {"debug": True}

# Class — multiple methods, state rakh sakta hai
class TaskService:
    def list(self):
        return [{"id": 1, "title": "Task 1"}]

    def create(self, title: str):
        return {"id": 2, "title": title}
```

---

### Class ko Dependency kaise banate hain?

```python
from fastapi import FastAPI, Depends

app = FastAPI()

class TaskService:
    def __init__(self, db_url: str = "sqlite:///tasks.db"):   # constructor
        self.db_url = db_url
        print(f"TaskService bana — DB: {self.db_url}")

    def list(self):
        return [{"id": 1, "title": "Homework"}, {"id": 2, "title": "Study"}]

    def create(self, title: str):
        return {"id": 3, "title": title, "db": self.db_url}


@app.get("/tasks")
def get_tasks(service: TaskService = Depends(TaskService)):   # Class seedha Depends mein
    return service.list()

@app.post("/tasks")
def add_task(title: str, service: TaskService = Depends(TaskService)):
    return service.create(title)
```

---

### `Depends(TaskService)` kaise kaam karta hai?

```
FastAPI: "TaskService ek class hai"
    ↓
FastAPI: "__init__" parameters check karta hai
    → __init__(self, db_url: str = "sqlite:///tasks.db")
    ↓
FastAPI: "db_url ka default value hai — khud inject karo"
    ↓
FastAPI: TaskService(db_url="sqlite:///tasks.db") object banata hai
    ↓
Wo object route function ko milta hai
    ↓
service.list() ya service.create() call ho sakta hai
```

---

### `__init__` mein doosri Dependency bhi ho sakti hai (Chain + Class)

```python
def get_db_url():
    return "sqlite:///tasks.db"

class TaskService:
    def __init__(self, db_url: str = Depends(get_db_url)):   # chain class ke andar
        self.db_url = db_url

    def list(self):
        return [{"id": 1, "db": self.db_url}]

@app.get("/tasks")
def get_tasks(service: TaskService = Depends(TaskService)):
    return service.list()
```

---

### Poora Flow — Class Dependency

```
User → GET /tasks

FastAPI: "get_tasks ko TaskService chahiye"
    ↓
FastAPI: TaskService.__init__ dekhta hai
    ↓
FastAPI: db_url ka default value hai
    → TaskService("sqlite:///tasks.db") object banta hai
    ↓
TaskService object → service variable mein aata hai
    ↓
service.list() chalta hai
    ↓
Response return
```

---

### Common Confusion — Default Value vs `Depends()`

**Confusion:** "TaskService ke `__init__` mein `db_url` already default hai — FastAPI isko kaise call karta hai?"

**Answer:** FastAPI `__init__` ke parameters scan karta hai aur do cases handle karta hai:

```python
# Case 1 — Simple default value
class TaskService:
    def __init__(self, db_url: str = "sqlite:///tasks.db"):
        #                              ↑ simple string
        # FastAPI: TaskService() seedha call — Python default lagata hai

# Case 2 — Depends() as default
class TaskService:
    def __init__(self, db_url: str = Depends(get_db_url)):
        #                              ↑ Depends() hai
        # FastAPI: pehle get_db_url() chalata hai, phir TaskService(result) call
```

Ye dono bilkul same result dete hain jab default string ho:

```python
TaskService()                             # FastAPI yehi call karta hai
TaskService(db_url="sqlite:///tasks.db")  # Python internally yehi karta hai
```

| `__init__` mein | FastAPI kya karta hai |
|-----------------|----------------------|
| `db_url = "sqlite:///tasks.db"` | Direct `TaskService()` — default Python khud lagata hai |
| `db_url = Depends(get_db_url)` | Pehle `get_db_url()` chalata hai, phir `TaskService(result)` |

> **Simple Rule:** FastAPI `__init__` scan karta hai — `Depends()` mile toh resolve karo, simple default mile toh Python pe chhod do.

---

### Functions vs Classes — Kab kya use karo?

| Situation | Use karo |
|-----------|----------|
| Sirf ek value/config return karni ho | Function |
| Multiple related operations (list, create, delete) | Class |
| State rakhni ho (db connection, settings) | Class |
| Simple aur ek kaam | Function |

---

## 19. Teeno Prompts — Final Summary

| Prompt | Concept | Short Matlab |
|--------|---------|--------------|
| Dependency Chain | `Depends()` ke andar `Depends()` | FastAPI puri chain khud resolve karta hai — andar se bahar |
| Testing Override | `app.dependency_overrides` | Test mein real dependency ki jagah fake lagao — `.clear()` se hatao |
| Class Dependency | `Depends(ClassName)` | FastAPI `__init__` resolve karta hai, object inject karta hai, methods available hote hain |
