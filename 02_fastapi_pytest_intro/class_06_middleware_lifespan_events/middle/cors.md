# CORS — Cross Origin Resource Sharing

---

## 1. CORS Kya Hai — Mera Concept

CORS ek **Guard** hai jo backend mein hota hai aur har aane wali request ko check karta hai:

- Kya ye **origin** (address) allow hai?
- Kya ye jo **method** laya hai allow hai?
- Kya ye jo **headers** laya hai allow hai?
- Kya isse **credentials** (Auth token/cookies) allow hain?

Ye sab backend ki CORS config se check karta hai. Agar allow hai toh request aane deta hai. Isi tarah **response ko bhi guard karta hai** — jaate waqt CORS headers response mein add karta hai taake browser bhi jaane ke kya allow hai.

---

## 2. Origin Kya Hota Hai — Exactly

Origin teen cheezoon se milta hai:

```
http://localhost:3000
↑        ↑         ↑
Protocol  Domain   Port
```

Agar in teenon mein se **ek bhi alag** ho — alag origin hai:

```
http://localhost:3000   ← frontend
http://localhost:8000   ← backend (port alag!) → CORS lagega

http://localhost:3000   ← frontend
https://localhost:3000  ← (protocol alag!) → CORS lagega
```

---

## 3. CORS Guard Kaise Kaam Karta Hai — 2 Types

### Type 1 — Complex Requests (DELETE, PUT, custom headers):

Yahaan CORS guard **request aane se pehle** rok leta hai:

```
Browser → DELETE /user → CORS Guard (Preflight Check)

Step 1: Browser pehle OPTIONS request bhejta hai:
   "Server! Kya mujhe DELETE karne doge? Mera origin ye hai..."

Step 2: CORS Guard backend config se check karta hai:
   "Nahi, ye origin allow nahi" ❌

Step 3: Actual DELETE request jaati hi nahi ✅
   Server surakshit raha
```

### Type 2 — Simple Requests (GET):

GET "safe" request hai — sirf data padhti hai, kuch modify nahi karti. Isliye:

```
Browser → GET /data → CORS Guard → Server tak jaane deta hai
                                        ↓
                                   Server response deta hai
                                        ↓
                              CORS Guard response mein headers add karta hai:
                              "Allow-Origin: localhost:3000"
                                        ↓
                              Browser ye headers padhta hai:
                              Allow hai → JS ko data milta hai ✅
                              Allow nahi → Browser JS ko data nahi deta ❌
```

---

## 4. CORS Kya Kya Check Karta Hai

### Allow Origins — Kaun Sa Address Allow Hai

```python
allow_origins=["http://localhost:3000", "https://myapp.com"]
```

Sirf ye origins backend se data le sakti hain.

### Allow Methods — Kaun Sa Method Allow Hai

```python
allow_methods=["GET", "POST", "DELETE", "PUT"]
```

- `GET` → sirf data padhna
- `POST` → naya data banana
- `PUT/PATCH` → data update karna
- `DELETE` → data hatana

### Allow Headers — Kaun Se Headers Allow Hain

```python
allow_headers=["Authorization", "Content-Type"]
```

Request ke saath jo headers aate hain — `Authorization` (token), `Content-Type` (application/json) etc.

### Allow Credentials — Auth Token Aur Cookies Allow Karna

```python
allow_credentials=True
```

Jab cookies ya Authorization token request ke saath bhejna ho tab ye `True` karte hain.

**Important Security Rule:** Agar `allow_credentials=True` hai toh `allow_origins=["*"]` **nahi** likh sakte — explicitly domains dene padte hain:

```python
# ❌ Ye combination nahi chalta
allow_origins=["*"],
allow_credentials=True

# ✅ Sahi tarika
allow_origins=["http://localhost:3000"],
allow_credentials=True
```

---

## 5. FastAPI Mein CORS Kaise Add Karte Hain

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=True,
)
```

---

## 6. Postman Mein CORS Kyun Nahi Lagta

Postman browser nahi hai — woh seedha request karta hai bina kisi CORS check ke. CORS sirf **browser** ke through aane wali requests pe apply hota hai.

---

## 7. Summary Table

| Check | Parameter | Matlab |
|-------|-----------|--------|
| Kaun sa origin allow hai | `allow_origins` | Domain + Protocol + Port |
| Kaun sa method allow hai | `allow_methods` | GET, POST, DELETE etc. |
| Kaun se headers allow hain | `allow_headers` | Authorization, Content-Type etc. |
| Credentials allow hain? | `allow_credentials` | Cookies, Auth tokens |
| Complex request (DELETE/PUT) | Preflight | Request jaane se pehle rokta hai |
| Simple request (GET) | Headers add karta hai | Browser response jaate waqt decide karta hai |
| Postman mein CORS? | — | Nahi lagta — browser nahi hai |

---

## 8. Development vs Production CORS

### Development CORS — Sab Kuch Allow

Jab apni machine pe kaam kar rahe ho (React localhost:3000, FastAPI localhost:8000) toh strict rules ki zaroorat nahi hoti:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # koi bhi domain — allow
    allow_methods=["*"],    # koi bhi method — allow
    allow_headers=["*"],    # koi bhi header — allow
)
```

`*` = **wildcard** = "sab kuch allow karo"

CORS guard ko bol rahe ho: "Development mein hai, kisi ko bhi andar aane do."

### Production CORS — Sirf Specific Cheezein Allow

Jab app live ho jaye toh strict rules lagane padte hain — sirf trusted domains ko allow karo:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://myapp.com"],  # sirf ye
    allow_methods=["GET", "POST", "PUT", "DELETE"],                # sirf ye methods
    allow_headers=["Authorization", "Content-Type"],               # sirf ye headers
    allow_credentials=True,
)
```

### Critical Rule — Credentials + Wildcard Nahi Chalta

```python
# ❌ Ye combination kabhi kaam nahi karta (browser reject karta hai)
allow_origins=["*"]
allow_credentials=True

# ✅ Credentials ke saath specific origins dene padte hain
allow_origins=["http://localhost:3000"]
allow_credentials=True
```

**Kyun?** Agar credentials (token, cookies) ke saath koi bhi origin allow ho toh koi bhi malicious website aapke user ka token chura ke aapke backend se data le sakti hai. Browser ye security hole allow nahi karta.

---

## 9. Step 3 — Timing Middleware + Logging + CORS — Sab Ek Saath

Pehle **nayi Python cheezein** samjhate hain jo is step mein use hongi, phir concept.

---

### Nayi Cheez 1 — `time` module aur `perf_counter()`

```python
import time

start = time.perf_counter()   # abhi ka time note karo
# ... kuch kaam hua ...
end = time.perf_counter()     # kaam ke baad ka time note karo

difference = end - start      # farq = kitna waqt laga (seconds mein)
```

**`perf_counter()` kya hai?**

Ek **stopwatch** ki tarah hai. Jab call karo toh ek number milta hai (seconds). Do baar call karo, farq nikalo — itna waqt laga beech mein.

```
start = 1000.123456   ← pehli reading
end   = 1000.123789   ← doosri reading
farq  = 0.000333      ← 0.3 milliseconds laga
```

**`:.4f` kya hai?** (f-string mein)

```python
value = 0.00033312345
print(f"{value:.4f}")    # output: 0.0003
#             ↑
#         sirf 4 decimal jagah dikhao
```

Ye sirf **display** ke liye hai — long number ko chhota dikhata hai.

---

### Nayi Cheez 2 — `logging` module

`print()` toh jaante ho — terminal pe text dikhata hai. `logging` bhi wahi karta hai **lekin professional tarike se**:

```python
import logging

logging.basicConfig(level=logging.INFO)   # setup karo
logger = logging.getLogger(__name__)      # apna logger banao

logger.info("Ye message dikhega")         # INFO level pe log karo
```

**`basicConfig(level=logging.INFO)` kya karta hai?**

Ye bol raha hai: "INFO aur usse upar ke messages show karo."

Levels hoti hain (chhoti se badi):
```
DEBUG < INFO < WARNING < ERROR < CRITICAL
```

Hum `INFO` set karte hain toh `INFO`, `WARNING`, `ERROR`, `CRITICAL` sab dikhega.

**`getLogger(__name__)` kya hai?**

`__name__` ek special Python variable hai — file ka naam store karta hai. Agar file `cors.py` hai toh `__name__` = `"cors"` hoga.

```python
logger = logging.getLogger(__name__)
# matlab: "cors" naam ka logger banao
```

Ye isliye karte hain taake pata chale **kaunsi file se log aaya**:
```
INFO:cors: → GET /hello        ← "cors" file se aaya
INFO:cors: ← GET /hello [200]
```

---

### Ab Poora Concept — Ye Teeno Sath Kaise Kaam Karte Hain

```
Request aati hai
      ↓
CORS Middleware (pehle check karta hai — outermost)
      ↓
Timing Middleware (stopwatch start)
      ↓
Logging Middleware (request log karta hai)
      ↓
Route Handler (/hello wala)
      ↓
Logging Middleware (response log karta hai)
      ↓
Timing Middleware (stopwatch stop, header add karta hai)
      ↓
CORS Middleware (response mein CORS headers add karta hai)
      ↓
Response browser ko jaata hai
```

**CORS ko pehle add karna kyun zaroori hai?**

CORS ko **outermost** (sabse bahar) hona chahiye taake Preflight OPTIONS request bhi CORS check se guzre. Agar CORS andar ho toh Preflight fail ho sakta hai.

FastAPI mein `add_middleware()` se add kiya hua **pehle outermost** banta hai — aur `@app.middleware("http")` wale LIFO order mein chalte hain (jo pehle likha, andar hoga).

---

## 10. Hands-On Testing — curl se Verify Karna

### Test 1 — `curl.exe -i http://localhost:8000/middle`

**Command ka matlab:**
- `curl.exe` → real curl tool
- `-i` → response mein **headers bhi dikhao** (sirf body nahi)
- `http://localhost:8000/middle` → is route pe GET request bhejo

**Output:**
```
HTTP/1.1 200 OK               ← server ne request accept ki, sab theek hai
date: ...                     ← kab response aaya
server: uvicorn               ← kaunsa server hai
content-length: 59            ← response kitne bytes ka hai
content-type: application/json ← JSON data aa raha hai
x-process-time: 0.0016        ← ✅ HAMARA custom header! 0.0016 seconds laga
                               (Timing middleware ne add kiya)

{"message":"Hello Cors Middleware & Custom Middleware !!!"}  ← route ka response
```

**Kya prove hua?** Timing middleware perfectly kaam kar raha hai — `X-Process-Time` header response mein aa gaya.

---

### Test 2 — OPTIONS (Preflight Simulate)

**Command ka matlab:**
```
curl.exe -X OPTIONS ...                          ← OPTIONS method se bhejo (Preflight)
  -H "Origin: http://localhost:3000"             ← "mera address ye hai" (browser ki tarah)
  -H "Access-Control-Request-Method: POST"       ← "kya mujhe POST karne doge?"
```

Hum **browser ki tarah behave** kar rahe hain — actual request se pehle permission maang rahe hain.

**Output:**
```
HTTP/1.1 200 OK                    ← CORS guard ne allow kar diya ✅

vary: Origin                       ← response Origin ke hisaab se alag ho sakta hai

access-control-allow-origin: http://localhost:3000   ← ✅ ye origin allow hai
access-control-allow-methods: GET, POST, PATCH, DELETE ← ✅ ye methods allowed hain
access-control-allow-headers: Authorization, Content-Type... ← ✅ ye headers allowed hain
access-control-allow-credentials: true  ← ✅ token/cookies bhi bhej sakte ho
access-control-max-age: 600        ← 600 seconds (10 min) tak Preflight dobara mat karo
                                      browser cache kar lega ye permission

x-process-time: 0.0008            ← Timing middleware OPTIONS pe bhi chala ✅

OK                                 ← Preflight successful, ab actual POST ja sakti hai
```

---

### Dono Tests Ka Conclusion

| Cheez | Status | Proof |
|-------|--------|-------|
| Timing Middleware | ✅ Kaam kar raha hai | `x-process-time` header aa raha hai |
| CORS Guard | ✅ Kaam kar raha hai | `access-control-allow-origin` header aa raha hai |
| Logging Middleware | ✅ Kaam kar raha hai | Terminal mein `-->` aur `<--` logs dikhte hain |
| Preflight | ✅ Kaam kar raha hai | `access-control-max-age: 600` — cache bhi ho raha hai |
