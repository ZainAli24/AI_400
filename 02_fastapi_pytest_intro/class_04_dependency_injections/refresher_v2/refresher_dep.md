# `@lru_cache` — Poori Tarah Deep Dive (Beginner Level)

## Pehle: Yeh Aata Kahan Se Hai?

`lru_cache` FastAPI ki apni cheez nahi hai — yeh Python ki built-in library `functools` se aata hai:

```python
from functools import lru_cache
```

**LRU** ka matlab hai **L**east **R**ecently **U**sed. Yeh ek general-purpose Python feature hai jo **kisi bhi function** pe laga sakte ho — FastAPI dependency ho ya na ho. FastAPI ne bas isay dependency ke saath use karna convenient bana diya hai.

---

## Working Flow — Andar Kya Ho Raha Hai (Step by Step)

Socho `lru_cache` ek chhota sa **register/khaata (dictionary)** apne paas rakhta hai, jismein woh likhta hai:

> "Agar function ko **inhi arguments** ke saath call kiya gaya, toh result yeh tha."

```python
@lru_cache
def get_settings():
    print("Loading settings...")
    return {"app_name": "Task API", "debug": True}
```

**Pehli baar `get_settings()` call hoti hai:**
1. `lru_cache` apne khaate mein dekhta hai: "kya `get_settings()` (bina kisi argument ke) pehle kabhi chali hai?"
2. Nahi chali — toh yeh **asli function body run karta hai** (`print("Loading settings...")` chalega, dictionary banegi)
3. Result ko khaate mein **save** kar leta hai: `(no arguments) → {"app_name": "Task API", "debug": True}`
4. Result caller ko return kar deta hai

**Dusri baar `get_settings()` call hoti hai (koi bhi request ho):**
1. `lru_cache` khaata check karta hai: "yeh combination pehle se hai?"
2. **Haan hai!** → function body **bilkul run nahi hoti** (isi liye `print` dobara nahi aata)
3. Seedha purana saved result wapas kar deta hai — turant, bina kaam kiye

Yehi wajah hai ke aap console mein `"Loading settings..."` sirf **ek dafa** dekhte ho, chahe `/info` endpoint 100 baar hit karo.

---

## "Kab Tak" Cache Rehta Hai? (Duration — Yeh Sabse Zaroori Point Hai)

Yahan ek **bahut common confusion** hoti hai beginners ko, isay clear karta hoon:

> ❌ `lru_cache` **time-based nahi hai** — is mein koi "5 minute ke liye cache karo" jaisi cheez nahi hoti.

✅ Yeh cache tab tak rehta hai **jab tak aapka Python process (server) zinda hai.**

Matlab:

| Scenario | Cache ka kya hota hai |
|---|---|
| Server chal raha hai, 1000 requests aayi | Sirf **1 dafa** function chalega, baaki 999 baar cached result milega |
| `uvicorn --reload` mode mein aapne code file save/edit ki | Server **restart** hota hai → naya process → cache **khali/reset** ho jata hai → agli request pe function **dobara** chalega |
| Aap manually server band kar ke phir se `uvicorn` command chalate ho | Naya process → cache reset |
| Aap khud code mein `get_settings.cache_clear()` call karo | Cache manually khali ho jata hai |

**Simple mental model:** Cache RAM (memory) mein baithta hai, kisi disk/file mein nahi. Jab tak process zinda hai, memory zinda hai, cache zinda hai. Process khatam → memory saaf → cache gaya.

---

## Ek Zaroori Twist: Cache **Arguments Ke Hisaab Se** Alag Hota Hai

Aapki `get_settings()` mein koi argument nahi hai, isliye **sirf ek hi possible entry** ban sakti hai khaate mein — isliye function poori tarah "ek dafa hi chalta hai, hamesha ke liye."

Lekin agar function **arguments leta hai**, toh har **naye combination** ke liye alag se ek dafa chalta hai:

```python
@lru_cache
def get_multiplier(x: int):
    print(f"Calculating for {x}...")
    return x * 10

get_multiplier(2)   # "Calculating for 2..." print hoga, khaate mein save: 2 -> 20
get_multiplier(3)   # naya combination! "Calculating for 3..." print hoga, save: 3 -> 30
get_multiplier(2)   # yeh combination pehle se hai -> seedha 20 return, print NAHI hoga
```

Toh sahi tareeqay se kahen: **"lru_cache har unique (function + arguments) combination ke liye sirf ek dafa chalta hai, baaki har baar cached value deta hai."**

---

## `maxsize` — Khaate Ki Jagah Limited Hai (LRU ka asli matlab yahan aata hai)

`lru_cache` ka khaata **infinite** nahi hota by default — default limit hoti hai **128 alag combinations**:

```python
@lru_cache(maxsize=128)   # yeh default hai, aap likho ya na likho
```

Agar 129waan naya combination aaya, toh sabse **purana / sabse kam use hone wala (Least Recently Used)** entry khaate se **nikal diya jata hai** taake nayi entry ke liye jagah bane. Isi wajah se naam hai **LRU** cache.

- Aapke `get_settings()` jaisay **no-argument** dependencies ke liye yeh baat matter hi nahi karti — kyunke sirf 1 hi combination possible hai, kabhi full nahi hogi.
- Yeh sirf tab important hoti hai jab function **bohot saare alag arguments** ke saath call ho (jaise `get_multiplier(1)`, `get_multiplier(2)`, ... `get_multiplier(500)`).

Agar aap chahte ho khaata **kabhi purani entries delete na kare**, likh sakte ho: `@lru_cache(maxsize=None)` (unlimited).

---

## Chhota Sa Live Demo (khud try karna)

```python
from functools import lru_cache
import time

@lru_cache
def slow_config():
    print("Heavy work happening... (imagine reading a file)")
    time.sleep(2)   # jaise koi bhaari kaam ho raha ho
    return {"app_name": "Task API"}

print(slow_config())   # ~2 second lagega, print aayega
print(slow_config())   # turant aayega, print NAHI aayega
print(slow_config())   # phir turant, print NAHI aayega
```

Isay agar aap FastAPI dependency mein use karo:

```python
@app.get("/info")
def app_info(settings: dict = Depends(slow_config)):
    return settings
```

**Pehli request** `/info` pe 2 second lagega. **Har agli request** turant (milliseconds mein) response degi — kyunke `slow_config()` dobara chalti hi nahi.

---

## One-Line Summary (yaad rakhne ke liye)

> `@lru_cache` = "Is function ko sirf tab dobara chalao jab yeh **naye arguments** ke saath call ho; warna **memory se seedha purana jawab** de do — aur yeh yaadasht process khatam hone tak (ya restart tak) rehti hai, kisi time-limit tak nahi."


-------

## `lru_cache` Ka Data Asal Mein Kahan Store Hota Hai? (Confusion Clear Karna)

**Python ki us current process ki memory mein — kisi file mein nahi.**

Jab aap `@lru_cache` lagate ho, Python us function ke **upar ek wrapper object** bana deta hai jismein ek internal **dictionary (hashmap)** attached hoti hai — yeh dictionary bilkul us waqt chal rahe **Python process ki memory** mein baithti hai, jaise koi normal Python variable/list/dict hoti hai.

```python
@lru_cache
def get_settings():
    ...
```

Yahan `get_settings` ab ek **wrapped function object** ban jata hai jiske andar chhupi hui ek dictionary hai, kuch aisi:

```python
# conceptually (asli internal implementation aisi hi kaam karti hai):
_cache = {}   # yeh current process ki memory mein hai

def wrapper(*args):
    if args in _cache:
        return _cache[args]
    result = get_settings(*args)
    _cache[args] = result
    return result
```

**Key points is confusion ko clear karne ke liye:**

1. **Koi file nahi banti** — na `.json`, na `.txt`, na `.db`. Disk pe kuch bhi save nahi hota.
2. Yeh dictionary us **Python process ki memory** ka hissa hai jo `uvicorn`/`python` chala raha hai.
3. Isi liye jaise hi process khatam hota hai (server band, ya `--reload` se restart), yeh dictionary **poori tarah mit jaati hai** — kyunke process khatam hote hi uski poori memory OS wapas le leta hai.
4. Agar aapke paas **2 alag server processes** chal rahe hoon (jaise `workers=4` wala production setup), toh **har process ki apni alag, separate cache dictionary** hogi — ek process ka cache doosre ko pata nahi chalega.

**Ek line mein:** `lru_cache` ka data **us current Python process ki memory mein, function ke apne wrapper object ke andar** rehta hai — file system ka is se koi lena dena nahi.
