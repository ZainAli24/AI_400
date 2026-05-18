# Lifespan Events — Mera Concept

---

## 1. Pehle Kya Hota Tha — `on_event` (Deprecated)

Pehle FastAPI mein `on_event("startup")` aur `on_event("shutdown")` events hote the:

- **startup** → jab bhi app start ho toh ye kaam ho jae — jaise DB connection bana lo, table bana lo
- **shutdown** → jab bhi app band ho toh clean kar do, connection close kar do

```python
# Purana tarika — ab ye DEPRECATED hai (expire/old ho gya hai)
@app.on_event("startup")
def create_user_table():
    create_table()
```

Ye kaam karta tha lekin FastAPI ne ise **deprecated** kar diya — yani ab ye old ho gya hai, future mein hata bhi sakte hain. Isliye naya tarika seekhna padega.

---

## 2. Naya Tarika — `asynccontextmanager` (Modern)

Ab FastAPI mein lifespan events ke liye hum `contextlib` library se `asynccontextmanager` function lete hain aur ise decorator ki tarah apne lifespan function pe lagate hain:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP — ye sab jab app start ho tab chale ga
    print("Starting up...")
    create_table()

    yield   # ← yahan tak startup, yahan se shutdown

    # SHUTDOWN — ye sab jab app band ho tab chale ga
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)
```

---

## 3. `yield` Ka Kaam — Line jo Startup aur Shutdown Alag Kare

```
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --------- STARTUP ----------
    create_table()       ← app start hone pe chalega
    yield                ← YE LINE boundary hai
    # --------- SHUTDOWN ---------
    print("Bye!")        ← app band hone pe chalega
```

- `yield` se **upar** = Startup (server requests lene se pehle)
- `yield` ke **neeche** = Shutdown (server band hone ke baad)

---

## 4. FastAPI Ko Batana — `lifespan=lifespan`

Sirf function banana kaafi nahi — FastAPI ko bhi batana padta hai ke "bhai, meri app ke liye ye lifespan events hain":

```python
app = FastAPI(lifespan=lifespan)
#             ↑
#    function pass kar diya — ab FastAPI janata hai
```

Agar `lifespan=lifespan` nahi diya toh function bana rahega lekin chalega nahi — startup/shutdown hoga hi nahi.

---

## 5. `async def` Zaroori Hai — Regular `def` Nahi Chalega

```python
# ❌ Ye kaam nahi karta — asynccontextmanager async function chahta hai
@asynccontextmanager
def lifespan(app: FastAPI):
    ...

# ✅ Sahi tarika
@asynccontextmanager
async def lifespan(app: FastAPI):
    ...
```

`@asynccontextmanager` decorator sirf **async** functions ke saath kaam karta hai — regular `def` pe lagaoge toh server start hote waqt error aayega.

---

## 6. Purana vs Naya — Comparison

| Cheez | Purana (`on_event`) | Naya (`lifespan`) |
|-------|--------------------|--------------------|
| Status | ❌ Deprecated (old) | ✅ Modern (recommended) |
| Startup | `@app.on_event("startup")` | `yield` se upar wala code |
| Shutdown | `@app.on_event("shutdown")` | `yield` ke neeche wala code |
| Import | kuch nahi | `from contextlib import asynccontextmanager` |
| FastAPI ko batana | automatic | `FastAPI(lifespan=lifespan)` |

---

## 7. Practical Use — Task App Mein

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("[INFO] Starting up...")
    create_table()          # ← DB mein tables bana do app start hone pe
    yield
    logging.info("[INFO] Shutting down...")   # ← app band hone pe log karo

app = FastAPI(lifespan=lifespan)
```

Jab server start hoga:
1. `"[INFO] Starting up..."` log hoga
2. `create_table()` chalega — DB tables ban jayenge
3. App requests lene lagegi

Jab server band hoga (Ctrl+C):
1. `"[INFO] Shutting down..."` log hoga

---

## 9. `get_session` Mein `Request` Automatically Kahan Se Aata Hai

```python
def get_session(request: Request):   # ye parameter kahan se milega?
    with Session(request.app.state.engine) as session:
        yield session
```

Jab route mein `Depends(get_session)` likhte ho:

```python
def create_user(user: UserData, session: Session = Depends(get_session)):
```

FastAPI khud dekh leta hai ke `get_session` ko `Request` chahiye — aur **automatically inject** kar deta hai. Aapko route mein `request` parameter add nahi karna padta. Ye FastAPI ka dependency injection system karta hai.

---

## 10. Key Use Cases — Agent APIs Ke Liye Kyun Zaroori Hai

---

### Use Case 1 — DB Connection Pool

#### Connection Pool Kya Hota Hai?

Socho ek restaurant hai. Customers aate hain, waiter unhe serve karta hai, phir waiter free hota hai agle customer ke liye.

Database ke saath bhi aisa hi hota hai:

- **Bina pool ke:** Har request pe naya DB connection banao, kaam karo, connection band karo. Phir agle request pe phir se naya banao.
- **Pool ke saath:** Pehle se 5-10 connections banake rakh do (pool). Request aaye — pool se ek connection lo, kaam karo, wapas pool mein daalo.

```
Bina Pool:
Request 1 → [connect] → [query] → [disconnect]   ← slow, har baar naya
Request 2 → [connect] → [query] → [disconnect]   ← slow, har baar naya

Pool ke saath:
Startup → [conn1, conn2, conn3, conn4, conn5]     ← ek baar banao
Request 1 → conn1 le lo → [query] → conn1 wapas  ← fast!
Request 2 → conn2 le lo → [query] → conn2 wapas  ← fast!
```

#### Task App Mein Kaise Ho Raha Hai

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP — ek baar engine banao (ye automatically pool manage karta hai)
    app.state.engine = create_engine(os.getenv("DATABASE_URL"), echo=True)
    SQLModel.metadata.create_all(app.state.engine)
    yield
    # SHUTDOWN — engine dispose karo (sare connections band)
    app.state.engine.dispose()
```

`create_engine()` SQLAlchemy ka function hai — ye automatically **connection pool** banata hai. Aapko alag se kuch nahi karna — bas `create_engine` hi pool deta hai.

**`dispose()` kyun zaroori hai shutdown pe?**

Agar `dispose()` nahi kiya toh server band hone ke baad bhi DB connections open rehte hain — ye **resource leak** hai. Theek se band karo taake DB pe load na pade.

---

### Use Case 2 — ML Model Loading

#### Pehle Samjho — ML Model Kya Hota Hai?

ML Model ek trained AI hai — jaise:
- Text ko vector mein convert karne wala (Embedding model)
- Image pehchanne wala (Image classifier)
- Text generate karne wala (Language model)

Ye models **files hoti hain** — disk pe stored. Use karne se pehle **memory (RAM) mein load** karni padti hain.

#### Problem — Lazy Loading (Galat Tarika)

```
User → Request bheja → "mujhe similar tasks dhundo"
                              ↓
                    Model load karo disk se... (2-3 seconds)
                              ↓
                    Ab query process karo... (0.1 seconds)
                              ↓
                    Response bhejo
```

**Pehli request pe 2-3 second delay** — ye Agent API ke liye bilkul nahi chalta. User sochega kuch toot gaya.

Aur agar 100 users ek saath request karein — 100 baar model load hoga — server crash!

#### Solution — Startup Pe Load Karo (Sahi Tarika)

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP — model ek baar load karo, state mein rakho
    app.state.embedder = SentenceTransformer("all-MiniLM-L6-v2")
    yield
    # SHUTDOWN — memory se hata do
    del app.state.embedder
```

```
Server Start → Model load karo (2-3 seconds) ← sirf ek baar

User 1 → Request → model already RAM mein hai → 0.1 sec ✅
User 2 → Request → model already RAM mein hai → 0.1 sec ✅
User 3 → Request → model already RAM mein hai → 0.1 sec ✅
```

#### Route Mein Kaise Use Karein

```python
@app.get("/search")
async def search_tasks(query: str, request: Request):
    embedder = request.app.state.embedder    # state se lo
    result = embedder.encode(query)          # use karo
    return {"result": result.tolist()}
```

#### `del` Kyun Karte Hain Shutdown Pe?

```python
del app.state.embedder
```

ML models bahut badi hoti hain — GB mein. Agar server band hone pe memory free nahi ki toh:
- RAM waste hoti rehti hai
- Agle restart pe problem ho sakti hai

`del` se Python ko pata chalta hai — "ye cheez ab chahiye nahi, memory free karo."

#### Real World Mein Kab Use Hota Hai

| Situation | Example |
|-----------|---------|
| Task search | User ke tasks mein similar text dhundna |
| Agent API | User ke query ko samajhna (NLP) |
| Recommendation | Similar content suggest karna |

---

### Use Case 3 — External Clients (HTTP Client, Anthropic SDK)

#### External Client Kya Hota Hai?

Jab aapki FastAPI app kisi **bahari service** se baat kare:
- Doosri API se data maange (HTTP request)
- Anthropic ke Claude AI se baat kare
- Kisi bhi third-party service se connect kare

Ye kaam karne ke liye ek **client object** banana padta hai — jo connection manage karta hai.

#### Problem — Har Request Pe Naya Client (Galat Tarika)

```python
@app.get("/summarize")
async def summarize(task: str):
    client = httpx.AsyncClient()          # ❌ har request pe naya client
    response = await client.get("https://some-api.com/data")
    await client.aclose()                 # ❌ har baar band bhi karo
    return response.json()
```

**Kyun galat hai?**
- Har request pe naya TCP connection banana padta hai — slow
- Agar request beech mein fail ho toh `aclose()` kabhi nahi chalega — connection leak
- 1000 requests = 1000 baar connect/disconnect — server pe load

#### Solution — Startup Pe Ek Baar Banao (Sahi Tarika)

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP — clients ek baar banao
    app.state.http_client = httpx.AsyncClient(timeout=30.0)
    app.state.anthropic = AsyncAnthropic()
    yield
    # SHUTDOWN — properly band karo
    await app.state.http_client.aclose()   # HTTP client close
```

#### Route Mein Kaise Use Karein

**HTTP Client:**
```python
@app.get("/weather")
async def get_weather(request: Request):
    client = request.app.state.http_client      # state se lo
    response = await client.get("https://weather-api.com/today")
    return response.json()
```

**Anthropic SDK (Claude AI):**
```python
@app.post("/ai-summarize")
async def ai_summarize(task: str, request: Request):
    anthropic = request.app.state.anthropic     # state se lo
    message = await anthropic.messages.create(
        model="claude-sonnet-4-6",
        messages=[{"role": "user", "content": f"Summarize: {task}"}]
    )
    return {"summary": message.content}
```

#### `timeout=30.0` Kya Hai?

```python
httpx.AsyncClient(timeout=30.0)
```

Iska matlab: agar bahari API 30 seconds mein jawab nahi de toh **automatically fail** ho jao — infinitely wait mat karo. Ye production mein zaroori hai.

#### `aclose()` Kyun Zaroori Hai — `dispose()` Se Farq

| Client | Shutdown mein kya karo |
|--------|----------------------|
| DB Engine (SQLAlchemy) | `.dispose()` — connections pool band karo |
| HTTP Client (httpx) | `await .aclose()` — async hai isliye `await` lagta hai |
| Anthropic SDK | khud internally manage karta hai |

`await` isliye lagta hai kyunki HTTP connection band karna ek async operation hai — thoda waqt lagta hai properly close hone mein.

#### Agent API Mein Ye Pattern Kyun Common Hai

Agent app mein almost har request pe bahari service se baat hoti hai:

```
User → "Mera task summarize karo"
            ↓
    FastAPI → Anthropic API (Claude)  ← ek bahari service
            ↓
    FastAPI → Database                ← doosri service
            ↓
    Response user ko
```

Dono ke liye startup pe client banao — har request fast rahegi.

---

### Use Case 4 — Why for Agents (Milliseconds Ka Concept)

#### Normal App vs Agent App — Farq Samjho

**Normal web app** (jaise ek blog):
```
User → "Mujhe articles dikhao"
          ↓
    DB se data lo (10ms)
          ↓
    Response bhejo
```

Agar pehli request mein 2 second delay ho — user thoda wait karega, koi baat nahi.

**Agent App** (jaise AI assistant):
```
User → "Mera kaam karo"
          ↓
    Agent soochta hai... (AI model)
          ↓
    Tool call karta hai... (API)
          ↓
    Phir soochta hai...
          ↓
    Phir tool call...
          ↓
    Response bhejo
```

Agent **baar baar** aapki FastAPI se baat karta hai — ek kaam ke liye 10-20 requests bhi ho sakti hain. Agar har request mein 2 second delay ho:

```
10 requests × 2 second delay = 20 seconds total ❌
10 requests × 0.001 second   = 0.01 seconds total ✅
```

#### Cold Start Problem — Kya Hota Hai

**Cold Start** = pehli request pe resources load hona

```
❌ Bina lifespan ke (lazy loading):

Pehli Request:
  DB connect karo...     (500ms)
  Model load karo...     (2000ms)
  HTTP client banao...   (100ms)
  Ab actual kaam karo... (10ms)
  TOTAL: 2610ms ← Agent ke liye unacceptable!

Doosri Request:
  Sab already loaded...  (10ms) ✅
```

Pehli request slow — Agent is wajah se fail ho sakta hai ya timeout ho sakta hai.

#### Lifespan Se Cold Start Khatam

```
✅ Lifespan ke saath:

Server Start (ek baar):
  DB connect karo...     (500ms)  ← startup pe
  Model load karo...     (2000ms) ← startup pe
  HTTP client banao...   (100ms)  ← startup pe

Pehli Request:
  Sab already loaded...  (10ms) ✅

Doosri Request:
  Sab already loaded...  (10ms) ✅

Teesri Request:
  Sab already loaded...  (10ms) ✅
```

Startup mein ek baar time lagao — har request fast rahegi.

#### Poora Picture — Lifespan + Agent

```
[Server Start]
      ↓
  lifespan startup:
  - DB engine ready      ✅
  - AI model loaded      ✅
  - HTTP client ready    ✅
      ↓
[Agent Request 1] → 10ms response
[Agent Request 2] → 10ms response
[Agent Request 3] → 10ms response
      ↓
[Server Stop]
  lifespan shutdown:
  - DB dispose           ✅
  - Model delete         ✅
  - HTTP client close    ✅
```

#### Ek Line Mein Summary

> **Lifespan events isliye hain — "server start pe ek baar bhari tayyari karo, phir har request lightning fast hogi."**

Agent APIs ke liye ye pattern **must** hai — optional nahi.

---

## 8. `app.state` — Startup Mein Bani Cheez Poori App Mein Use Karo

### Problem — Lifespan Mein Bani Cheez Route Ko Kaise Mile?

Lifespan mein koi cheez banao — jaise DB engine:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_engine(...)   # sirf yahan hai
    yield
```

Problem: ye `engine` sirf `lifespan` function ke andar hai. Route function ke andar ye variable exist hi nahi karta — kaise milega?

`app.state` iska solution hai.

---

### `app.state` Kya Hai?

`app` object (FastAPI ka) ek **bag** ki tarah hai — usme kuch bhi rakh sakte ho `state` ke zariye:

```python
app.state.kuch_bhi = "jo chahiye rakho"
```

Ye bag poori app ki life mein exist karta hai — startup se shutdown tak. Koi bhi route is bag se cheez nikal sakta hai.

---

### Kaise Kaam Karta Hai — Step by Step

**Step 1 — Startup pe cheez banao aur `app.state` mein rakho:**

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.engine = create_engine(DATABASE_URL)   # banao aur bag mein rakho
    yield
    app.state.engine.dispose()                        # shutdown pe bag se nikalo aur clean karo
```

**Step 2 — Route mein `request.app.state` se nikalo:**

```python
@app.get("/something")
def some_route(request: Request):
    engine = request.app.state.engine    # bag se nikala
    # ab engine use karo
```

---

### `app.state` vs `request.app.state` — Farq Kya Hai?

```python
# Lifespan mein:
app.state.engine = ...       # direct app object hai — isliye app.state

# Route mein:
request.app.state.engine     # request ke andar app hota hai — isliye request.app.state
```

Dono same bag hain — bas access karne ka rasta alag hai:
- Lifespan ke andar → `app` seedha milta hai
- Route ke andar → `request` milta hai, us se `app` milta hai

---

### Real Example — HTTP Client

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient()   # startup pe HTTP client banao
    yield
    await app.state.http_client.aclose()           # shutdown pe close karo

@app.get("/fetch-data")
async def fetch_data(request: Request):
    client = request.app.state.http_client         # route mein use karo
    response = await client.get("https://api.example.com")
    return response.json()
```

Kyun acha hai? Har request pe naya HTTP client banana wasteful hai. Ek baar banao, sab routes use karein.

---

### `app.state` Bina — Kya Problem Hoti?

```python
# ❌ Ye galat tarika — har request pe naya engine banega
@app.get("/tasks")
def get_tasks():
    engine = create_engine(DATABASE_URL)   # har baar naya connection — slow + waste
```

```python
# ✅ Sahi tarika — ek baar banao, baar baar use karo
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.engine = create_engine(DATABASE_URL)   # ek baar
    yield

@app.get("/tasks")
def get_tasks(request: Request):
    engine = request.app.state.engine   # use karo
```
