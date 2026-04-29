# Environment Variables — Complete Concept Notes

---

## Problem: Secret Values Code Mein Kyun Nahi Likhte?

Agar tum directly code mein secret key likh do:

```python
GEMINI_API_KEY = "AIzaSy-abc123-real-secret-key"  # GALAT TARIKA
```

**Nuksaan:**
- GitHub pe upload hote hi sari duniya key dekh leti hai
- Hacker key chura ke free mein use karta hai
- Tumhara account ban ya bhari bill aa sakta hai

**Solution:** Secret values ko code se bahar, ek alag file mein rakhna

---

## .env File Kya Hai?

`.env` ek simple text file hai jisme secret values store hoti hain.

```
# .env file ka andar
GEMINI_API_KEY=AIzaSy-abc123-real-secret-key
DATABASE_URL=postgresql://localhost/mydb
```

**Rules:**
- Har line: `VARIABLE_NAME=value`
- Yeh file **kabhi GitHub pe nahi jaati**
- Local machine pe sirf tumhare paas hoti hai

---

## python-dotenv Library

`dotenv` ek Python library hai jo `.env` files ko handle karti hai.

```bash
pip install python-dotenv
```

Is library se hum `load_dotenv` function import karte hain:

```python
from dotenv import load_dotenv
```

---

## `load_dotenv()` — Kaam Kya Hai?

`.env` file ko parhta hai aur us mein likhi values ko **OS ki memory (environment)** mein daal deta hai.

```python
load_dotenv()  # default: sirf .env file dhundta aur load karta hai
```

**Simple analogy:**
> `.env` file ek **locked drawer** hai. `load_dotenv()` us drawer ki **chaabi** hai —
> jo use khol ke sab values OS ki memory mein daal deti hai.

**Flow:**
```
.env file:   GEMINI_API_KEY=abc123
                    ↓
             load_dotenv()
                    ↓
OS Memory:   GEMINI_API_KEY = "abc123"  ✓
```

---

## load_dotenv() — Konsi File Load Hogi?

### Default: Sirf `.env`
```python
load_dotenv()           # ← sirf .env file load hogi, .env.local NAHI
```

### Specific File Load Karna
```python
load_dotenv(".env.local")                  # sirf .env.local
load_dotenv(dotenv_path=".env.local")      # same, dono tarike sahi
```

### Dono Files Ek Saath Load Karna
```python
load_dotenv(".env")        # pehle .env load karo
load_dotenv(".env.local")  # phir .env.local load karo
```

---

## Override Rule — Important!

Jab dono files load karo toh ek rule hota hai:

```python
load_dotenv(".env")        # GEMINI_API_KEY = "key-from-env"
load_dotenv(".env.local")  # GEMINI_API_KEY = "key-from-local"  ← yeh NAHI chalega
```

**Default:** Jo variable **pehle load hua**, woh jeetat hai — baad wala override nahi karta.

Agar baad wala override karna ho:
```python
load_dotenv(".env.local", override=True)  # ab .env.local ki value chalegi
```

---

## `os.getenv()` — Kaam Kya Hai?

`os` Python ka built-in module hai jo Operating System se baat karta hai.

```python
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
```

`os.getenv()` OS ki memory mein jaata hai aur us naam ki value uthata hai.

**Important:** `os.getenv()` ko **files se koi matlab nahi** — woh sirf OS memory se parhta hai.

```
.env file  →  load_dotenv()  →  OS Memory  →  os.getenv()  →  Value
```

`os.getenv()` ko pata nahi ke value `.env` se aayi ya `.env.local` se — usse sirf OS memory dikhti hai.

---

## Puri Flow Ek Baar Mein

```
[.env file]           [.env.local file]
GEMINI_API_KEY=abc      (agar chahiye toh)
      ↓                        ↓
  load_dotenv()      load_dotenv(".env.local")
      ↓                        ↓
            [OS Memory]
      GEMINI_API_KEY = "abc123"
            ↓
  os.getenv("GEMINI_API_KEY")
            ↓
         "abc123"  ✓
```

---

## Tumhara Code — Line by Line

```python
from fastapi import FastAPI
from dotenv import load_dotenv   # dotenv library se load_dotenv import kiya
import os                         # OS se baat karne ke liye

load_dotenv()                     # .env file parh ke OS memory mein daal do

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # OS memory se value nikalo

app = FastAPI()

@app.get("/key")
def get_key():
    return {"Gemini key": GEMINI_API_KEY}
```

**Note:** Is code mein `load_dotenv()` sirf `.env` file load karta hai — `.env.local` load **nahi** hogi jab tak explicitly `load_dotenv(".env.local")` na likho.

---

<br>

# **2. `pydantic-settings` — Recommended Tarika**

### Pehle Samjho: `os.getenv()` Mein Kya Problem Hai?

```python
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY")   # agar missing → None milega
DEBUG           = os.getenv("DEBUG")             # "true" string milegi, boolean nahi
MAX_CONNECTIONS = os.getenv("MAX_CONNECTIONS")   # "10" string milegi, number nahi
```

**3 Problems:**

| Problem | Kya Hota Hai |
|---------|-------------|
| Har cheez string milti hai | `"10"` milta hai, `10` nahi — manually convert karna padta |
| Koi validation nahi | Typo ho toh bhi chup chap galat value chali jaati hai |
| Required variables ka pata nahi | Missing variable pe `None` milta, app baad mein crash hoti hai |

---

### Solution: `pydantic-settings`

Install karo:
```bash
uv add pydantic-settings
# ya
pip install pydantic-settings
```

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str           # required — koi default nahi
    debug: bool = False           # optional — default: False
    max_connections: int = 10     # optional — default: 10

    class Config:
        env_file = ".env"         # is file se parhna
```

Bas `Settings()` object banao — yeh class **khud** `.env` file parhegi, types convert karegi, aur validate karegi.

---

### Feature 1 — Automatic Type Conversion

```
.env:   MAX_CONNECTIONS=5    ← string hai
              ↓
    BaseSettings ne convert kiya
              ↓
settings.max_connections = 5  ← ab integer hai  ✓
```

Tumhe manually `int(os.getenv("MAX_CONNECTIONS"))` nahi likhna padta.

---

### Feature 2 — Validation (Galat Value Pe Startup Error)

```
.env:   MAX_CONNECTIONS=abc   ← number nahi
              ↓
        Settings()  ← object banate waqt
              ↓
ERROR at startup:
  max_connections
    Input should be a valid integer  ✗
```

App start hote hi crash — request ke time nahi. **Yeh acha hai** — pehle hi pata chal gaya.

---

### Feature 3 — Default Values

```python
class Settings(BaseSettings):
    gemini_api_key: str       # koi default nahi → REQUIRED
    debug: bool = False       # .env mein nahi → False use hoga
    max_connections: int = 10 # .env mein nahi → 10 use hoga
```

```
.env mein DEBUG nahi likha  →  settings.debug = False       ✓ default
.env mein GEMINI_API_KEY nahi  →  ERROR! Field required     ✗
```

---

### Feature 4 — Self-Documenting

```python
class Settings(BaseSettings):
    gemini_api_key: str        # string chahiye, required
    debug: bool = False        # bool chahiye, default False
    max_connections: int = 10  # int chahiye, default 10
```

Sirf yeh class dekh ke koi bhi samajh sakta hai ke app ko konse variables chahiye aur kis type ke. `os.getenv()` mein yeh sab scattered hota tha.

---

### Pura Comparison

**Purana tarika:**
```python
from dotenv import load_dotenv
import os

load_dotenv(".env")

GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY")  # None agar missing
DEBUG           = os.getenv("DEBUG")            # "true" string
MAX_CONNECTIONS = os.getenv("MAX_CONNECTIONS")  # "10" string
# manually convert karna padega, validate karna padega
```

**Naya tarika:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    debug: bool = False
    max_connections: int = 10

    class Config:
        env_file = ".env"

settings = Settings()  # ek line mein sab ho gaya
# settings.debug           = True   (boolean, string nahi)
# settings.max_connections = 10     (integer, string nahi)
# gemini_api_key missing   → startup pe clear error  ✓
```

---

### os.getenv vs pydantic-settings — Final Table

| Feature | `os.getenv()` | `pydantic-settings` |
|---------|--------------|---------------------|
| Type conversion | Manual | Automatic |
| Validation | Koi nahi | Startup pe error |
| Default values | Manually likhna | Class mein directly |
| Missing variable | `None` milta, baad crash | Startup pe clear error |
| Readable | Scattered | Ek jagah organized |

---

## `pydantic-settings` — Common Confusions

### `class Config` — Naam Badal Sakta Hai?

**Nahi — `Config` naam fixed hai.**

```python
class Settings(BaseSettings):
    gemini_api_key: str

    class Config:        # ← EXACTLY "Config" hona zaroori hai
        env_file = ".env.local"
```

`BaseSettings` khud andar se `Config` naam dhundta hai — agar `class MyConfig` ya kuch aur likho toh ignore ho jaayega, `.env` file load hi nahi hogi.

**Modern Tarika (pydantic v2):**
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    gemini_api_key: str

    model_config = SettingsConfigDict(env_file=".env.local")  # naya recommended tarika
```

Dono kaam karte hain — `class Config` purana tarika, `model_config` naya.

---

### `env_file` — Naam Badal Sakta Hai?

**Nahi — `env_file` naam fixed reserved keyword hai.**

```python
class Config:
    env_file = ".env.local"    # ← fixed naam
    env_file_path = ...        # ← kaam NAHI karega
    file = ...                 # ← kaam NAHI karega
```

---

### Variable Names — UPPER ya lower — Same Hona Zaroori Hai?

**Nahi — pydantic-settings by default case-insensitive hai.**

```python
class Settings(BaseSettings):
    GEMINI_API_KEY: str    # UPPER
    gemini_api_key: str    # lower  — dono match karenge!
    Gemini_Api_Key: str    # mixed  — yeh bhi match karega
```

`.env.local` mein `GEMINI_API_KEY=abc123` ho toh teeno match ho jaate hain.

**Convention:** Environment variables uppercase likhna industry standard hai — isliye `.env` mein bhi UPPER aur class mein bhi UPPER likhna best practice hai, technically zaroori nahi.

---

### Behind the Scenes — `Settings()` Call Hone Pe Kya Hota Hai?

```python
settings = Settings()   # ← yeh ek line likhne se andar kya kya hua?
```

**Step 1 — Config check:**
```
BaseSettings ne Config dekha → env_file = ".env.local" mila
→ disk pe .env.local file dhundhi aur parhi
```

**Step 2 — File parse hui (sab strings):**
```
GEMINI_API_KEY=AIzaSy-abc123  →  {"GEMINI_API_KEY": "AIzaSy-abc123"}
MAX_CONNECTIONS=5              →  {"MAX_CONNECTIONS": "5"}
DEBUG=true                     →  {"DEBUG": "true"}
```

**Step 3 — Har field ke liye matching + type conversion:**
```
Field: GEMINI_API_KEY (str)
    → value mili: "AIzaSy-abc123"
    → type str chahiye → convert: "AIzaSy-abc123"  ✓

Field: MAX_CONNECTIONS (int)
    → value mili: "5"
    → type int chahiye → convert: 5  ✓  (string → integer)

Field: DEBUG (bool)
    → value mili: "true"
    → type bool chahiye → convert: True  ✓  (string → boolean)
```

**Step 4 — Validation:**
```
Required field missing?  → ERROR at startup  ✗
Galat type?              → ERROR at startup  ✗
Sab theek?               → settings object ready  ✓
```

**Step 5 — Object ready:**
```python
settings.GEMINI_API_KEY  = "AIzaSy-abc123"  # str
settings.MAX_CONNECTIONS = 5                 # int   (string nahi)
settings.DEBUG           = True              # bool  (string nahi)
```

**Error cases:**
```
GEMINI_API_KEY .env mein nahi + koi default nahi:
    → "Field required [GEMINI_API_KEY]"  ✗

MAX_CONNECTIONS=abc likha:
    → "Input should be a valid integer"  ✗
```

**Puri Flow:**
```
Settings()
    ↓
Config → env_file = ".env.local" → file parhi
    ↓
Har field: naam dhundha (case-insensitive) → value li → type convert ki → validate kiya
    ↓
Sab theek?   →  settings object ready  ✓
Kuch gadbad? →  startup pe ERROR       ✗
```

---

# **3. `@lru_cache` + `Depends()` — Recommended Pattern**

### Pehle Samjho: Problem Kya Hai?

```python
settings = Settings()   # ← global variable

@app.get("/key")
def get_key():
    return {"Gemini key": settings.GEMINI_API_KEY}
```

Yeh kaam karta hai — lekin **testing mein settings change nahi kar sakte.** Test mein real `.env.local` ki jagah fake settings dena chahoge — global variable ke saath yeh mushkil hai.

---

### `@lru_cache` — Kya Hai?

`lru_cache` Python ki `functools` library mein hai — ek decorator jo function pe lagata hai.

**Rule:** Pehli baar function chale → result cache karo. Agle baar call ho → cached result do, function dobara mat chalao.

```python
from functools import lru_cache

@lru_cache
def get_settings():
    return Settings()   # ← yeh sirf ek baar chalega
```

```
Call 1: get_settings()
    → cache mein kuch nahi
    → Settings() banaya (.env.local parhi, types convert hue)
    → result cache mein rakha
    → Settings object return kiya

Call 2: get_settings()
    → cache check kiya → mila!
    → Settings() dobara NAHI banaya  (disk nahi parhi)
    → cached Settings object return kiya  ✓

Call 100: get_settings()
    → cache se same object  ✓
```

---

### `Depends()` — Kya Hai?

`Depends()` FastAPI ka Dependency Injection system hai.

Matlab: endpoint function ko batana ke "yeh cheez bahar se leke aao" — tum khud mat banao.

```python
from fastapi import Depends

@app.get("/key")
def get_key(settings: Settings = Depends(get_settings)):
    #         ↑ parameter      ↑ FastAPI khud get_settings() call karega
    return {"Gemini key": settings.GEMINI_API_KEY}
```

```
Request aai /key pe
    ↓
FastAPI ne dekha: Depends(get_settings) hai
    ↓
FastAPI ne get_settings() call kiya
    ↓
Result settings parameter mein daal diya
    ↓
Tumhara function chala
```

---

### Dono Saath — Pura Flow

```python
from fastapi import FastAPI, Depends
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    MAX_CONNECTIONS: int = 5
    DEBUG: bool = False

    class Config:
        env_file = ".env.local"

@lru_cache
def get_settings() -> Settings:
    return Settings()

app = FastAPI()

@app.get("/key")
def get_key(settings: Settings = Depends(get_settings)):
    return {
        "Gemini key": settings.GEMINI_API_KEY,
        "Max Connections": settings.MAX_CONNECTIONS,
        "debug": settings.DEBUG
    }
```

```
Request 1: GET /key
    ↓
FastAPI → Depends(get_settings) → get_settings() call karo
    ↓
@lru_cache: pehli baar → Settings() banao → cache mein rakho
    ↓
get_key() chali → response return kiya  ✓

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Request 2: GET /key
    ↓
FastAPI → Depends(get_settings) → get_settings() call karo
    ↓
@lru_cache: cache mein hai → same object do  (disk nahi parhi)
    ↓
get_key() chali → response return kiya  ✓ fast!
```

---

### Sabse Bada Fayda — Testing

```python
# test file mein — real .env ki jagah fake settings inject karo
def fake_settings():
    return Settings(
        GEMINI_API_KEY="fake-test-key",
        MAX_CONNECTIONS=1,
        DEBUG=True
    )

app.dependency_overrides[get_settings] = fake_settings
# ab tests mein fake_settings use hogi, real .env nahi
```

Global variable `settings = Settings()` ke saath yeh possible nahi tha.

---

### Purana vs Naya Tarika

**Purana:**
```python
settings = Settings()        # global — hamesha module load pe banta hai

@app.get("/key")
def get_key():
    return {"key": settings.GEMINI_API_KEY}
```

**Naya (recommended):**
```python
@lru_cache
def get_settings():
    return Settings()        # sirf tab banta hai jab pehli request aaye

@app.get("/key")
def get_key(settings: Settings = Depends(get_settings)):
    return {"key": settings.GEMINI_API_KEY}
```

---

### Quick Summary

| Cheez | Kaam |
|-------|------|
| `@lru_cache` | Function ka result cache karo — dobara mat chalao |
| `Depends(get_settings)` | FastAPI ko bolo: yeh function call karke result inject karo |
| Dono saath | Settings sirf ek baar banti hai, har endpoint mein inject hoti hai |
| Testing fayda | `dependency_overrides` se fake settings daal sakte ho |

---

# **3. `pydantic-settings` — Values Ki Priority Order**

### Confusion: Kya `.env` File Direct Values Ko Replace Kar Deti Hai?

```python
Settings(GEMINI_API_KEY="fake-test-key")
# .env.local mein bhi GEMINI_API_KEY=real-key hai
# Kaunsi value chalegi?
```

**Jawab: Direct pass ki gayi value hamesha jeetti hai — `.env` file use replace nahi kar sakti.**

---

### Priority Order (Upar = Zyada Powerful)

```
1. Direct init values    Settings(KEY="value")      ← SABSE ZYADA PRIORITY
2. OS environment        export KEY=value
3. .env file             KEY=value in .env.local
4. Class defaults        key: str = "default"       ← SABSE KAM PRIORITY
```

Jo upar hai woh jeetta hai — neeche wali value usse replace nahi kar sakti.

---

### Example

```python
class Settings(BaseSettings):
    GEMINI_API_KEY: str
    MAX_CONNECTIONS: int = 5    # default
    DEBUG: bool = False         # default

    class Config:
        env_file = ".env.local"
```

```
.env.local mein:
    GEMINI_API_KEY=real-key
    MAX_CONNECTIONS=10
```

**Case 1 — Koi value pass nahi:**
```python
s = Settings()
# s.GEMINI_API_KEY  = "real-key"  ← .env.local se
# s.MAX_CONNECTIONS = 10          ← .env.local se
# s.DEBUG           = False       ← class default se
```

**Case 2 — Kuch values pass ki:**
```python
s = Settings(GEMINI_API_KEY="fake-key", MAX_CONNECTIONS=1)
# s.GEMINI_API_KEY  = "fake-key"  ← init ne override kiya  ✓
# s.MAX_CONNECTIONS = 1           ← init ne override kiya  ✓
# s.DEBUG           = False       ← .env.local mein nahi tha → class default se
```

**Case 3 — Sari values pass ki:**
```python
s = Settings(GEMINI_API_KEY="fake", MAX_CONNECTIONS=1, DEBUG=True)
# .env.local exist kare ya na kare — koi fark nahi
# sari init values use hongi  ✓
```

---

### Isliye Testing Mein Safe Hai

```python
def fake_settings():
    return Settings(
        GEMINI_API_KEY="fake-test-key",  # priority 1 → .env.local override
        MAX_CONNECTIONS=1,                # priority 1 → .env.local override
        DEBUG=True                        # priority 1 → .env.local override
    )
```

Chahe real `.env.local` mein kuch bhi likha ho — fake values hamesha jeetenge. Real keys test mein kabhi use nahi hongi.

> **Direct pass ki gayi values sabse powerful hoti hain — `.env` file unhe replace nahi kar sakti, woh khud replace ho jaati hai.**

---

# 1. point concept: `load_dotenv` aur `os.getenv` — Har Request Pe Chalta Hai Ya Sirf Ek Baar?

**Jawab: Sirf ek baar — app start hone pe.**

Tumhara code dekho:

```python
load_dotenv(".env.local")                    # ← LINE A — module level
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # ← LINE B — module level

app = FastAPI()

@app.get("/key")
def get_key():
    return {"Gemini key": GEMINI_API_KEY}    # ← LINE C — function level
```

**Line A aur Line B** function ke andar nahi hain — yeh **module level** pe hain.

Python ka rule: **Module level code sirf ek baar chalta hai** — jab app start hoti hai.

```
App start hoti hai (uvicorn chalao)
        ↓
Line A: load_dotenv(".env.local")         → ek baar .env.local parha, OS memory mein dala
        ↓
Line B: os.getenv("GEMINI_API_KEY")       → ek baar OS memory se value uthaayi
        ↓
GEMINI_API_KEY = "abc123"                 → yeh variable RAM mein store ho gaya
        ↓
App ready — requests sunne lagi

─────────────────────────────────────────────────────
Request 1:   GET /key  →  Line C: "abc123" return kiya  ✓
Request 2:   GET /key  →  Line C: "abc123" return kiya  ✓
Request 100: GET /key  →  Line C: "abc123" return kiya  ✓
─────────────────────────────────────────────────────
load_dotenv aur os.getenv dobara nahi chale — sirf stored variable return hota raha
```

### Agar Har Request Pe Fresh Load Chahiye? (Galat Practice)

```python
@app.get("/key")
def get_key():
    load_dotenv(".env.local")             # har request pe — GALAT
    key = os.getenv("GEMINI_API_KEY")     # har request pe — GALAT
    return {"Gemini key": key}
```

Yeh slow bhi hoga aur zaroorat bhi nahi — isliye kabhi mat karo.

### Module Level vs Function Level — Rule

| Code Kahan Hai | Kab Chalta Hai |
|----------------|----------------|
| Function ke **bahar** (module level) | Sirf **ek baar** — app start pe |
| Function ke **andar** | **Har baar** — jab route hit ho |

---

## Security — Zaroori Rule

`.gitignore` file mein `.env` zaroor likho:

```
# .gitignore
.env
.env.local
*.env
```

GitHub pe `.env.example` commit karo (real values nahi, sirf variable names):

```
# .env.example — copy karo aur real values bharo
GEMINI_API_KEY=your-key-here
DATABASE_URL=your-database-url-here
```

---

# **4. Common Mistakes:**

### Mistake 1 — `.env` File GitHub Pe Upload Kar Dena

```bash
git add .         # .env bhi add ho gayi
git commit -m "..."
git push          # ab sari duniya key dekh sakti hai
```

**Fix — pehle `.gitignore` mein likho:**
```
.env
.env.*
```

**Agar already commit ho gayi toh:**
```bash
git rm --cached .env    # git ki tracking se hataao (file delete nahi hogi)
git commit -m "remove .env from tracking"
```

---

### Mistake 2 — Variable Naming Galat Karna

```python
class Settings(BaseSettings):
    gemini_key: str        # naam alag
```

```
.env mein:  GEMINI_API_KEY=abc123   # naam alag
```

Naam match nahi kiya — `gemini_key` ko `GEMINI_API_KEY` nahi milega → **Field required error** at startup.

**Rule:** Class mein jo naam likho, `.env` mein wohi naam hona chahiye (case matter nahi karta, spelling matter karti hai).

---

### Mistake 3 — `class Config` Bhool Jaana

```python
class Settings(BaseSettings):
    GEMINI_API_KEY: str

    # class Config bhool gaye
```

`.env` file read hi nahi hogi → `GEMINI_API_KEY` missing → startup pe error.

**Fix:**
```python
class Settings(BaseSettings):
    GEMINI_API_KEY: str

    class Config:
        env_file = ".env"
```

---

### Mistake 4 — `@lru_cache` Na Lagana

```python
def get_settings() -> Settings:    # @lru_cache nahi lagaya
    return Settings()
```

Har request pe `Settings()` dobara banta hai → har baar disk se `.env` file parhi jaati hai.

**Fix:**
```python
@lru_cache
def get_settings() -> Settings:
    return Settings()
```

```
Bina @lru_cache:   har request → disk read  (slow, zaroorat nahi)
Ke saath:          pehli baar → disk read, baad mein → cache se  ✓
```

---

## Quick Summary

| Cheez | Kaam |
|-------|------|
| `.env` file | Secret values store karna |
| `python-dotenv` | Library jo .env files handle kare |
| `load_dotenv()` | .env file parh ke OS memory mein daalo |
| `os.getenv("NAME")` | OS memory se value nikalo |
| `override=True` | Baad wali file pehli ko override kare |
| `.gitignore` | .env file ko GitHub se chhupaao |
