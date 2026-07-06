# Pytest Fundamentals — Mukammal Notes (Roman Urdu)

## 1️⃣ Lesson ka Maqsad (Pytest Fundamentals — Intro)

Is lesson ka core idea ye hai: **"Testing baad mein add nahi ki jaati — ye verify karne ka tareeqa hai ke aapka code waisa kaam kar raha hai jaisa aap sochte hain."**

Sabse important baat: **is lesson mein AI use NAHI karni**. Manually tests likhna hai. Wajah ye hai ke:

> Jab tak aap khud tests nahi likhoge, aapko pata hi nahi chalega ke **achhi test** kya hoti hai aur **buri test** kya hoti hai. Agar aap ne kabhi test likhi hi nahi, to future mein jab AI aapke liye test generate karega, aap uski quality judge nahi kar paoge.

Ye "Red-Green cycle" (aage explain karunga) ko **mehsoos karna** hai, sirf theory nahi.

---

## 2️⃣ Agent APIs ke liye Testing Kyun Zaroori Hai?

Ye section specifically explain karta hai ke jab aap **AI agents ke liye APIs** banate ho (jo agents call karenge), testing aur bhi critical ho jaati hai, 4 wajuhat se:

1. **Agents guess nahi kar sakte** — Wo bilkul wahi call karenge jo aapka API expose karta hai. Agar API ka response ambiguous ya broken hai, agent confuse ho jayega.
2. **Errors cascade hoti hain** — Ek broken endpoint har us agent ko break kar dega jo use kar raha hai.
3. **Debugging mushkil hoti hai** — Agent ki failures aksar API mein hui changes se related hoti hain.
4. **Confidence se iteration milti hai** — Agar tests hain to aap bina dar ke refactor kar sakte ho (code improve kar sakte ho ye jaante hue ke agar kuch break hua to test fail ho jayegi).

Isi wajah se is course mein har endpoint ke saath test likhna sikhaya ja raha hai.

---

## 3️⃣ Your First Test (Pehli Test)

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}
```

Isko file `test_main.py` mein banate hain. Ab har line ka breakdown:

- **`TestClient`** — FastAPI ka special class jo aapki app ko "wrap" karta hai taake aap real server chalaye baghair (bina `uvicorn` run kiye) requests bhej sako testing ke liye.
- **`client = TestClient(app)`** — apni `main.py` wali `app` ko TestClient mein pass kar diya.
- **`client.get("/")`** — bilkul waisi hi request jaisi browser bhejta hai, GET request root endpoint (`/`) par.
- **`assert`** — ye Python ka keyword hai jo check karta hai ke koi condition True hai ya nahi. Agar False ho, to `AssertionError` throw hoti hai aur test **FAIL** ho jaati hai.
  - `assert response.status_code == 200` → check karo status code 200 (OK) hai.
  - `assert response.json() == {...}` → response body ko JSON mein parse karo aur match karo expected dictionary se.

**Bunyadi mechanism yehi hai**: agar koi bhi assert fail ho, poori test fail. Bas itna hi hai.

---

## 4️⃣ Tests Run Karna

Pehle pytest install karo (dev dependency ke tor pe, kyunke production mein iski zaroorat nahi):

```
uv add --dev pytest
```

Phir run karo:

```
pytest test_main.py -v
```

`-v` flag **verbose** output deta hai — matlab ye batayega konsi test chali, konsi pass hui, konsi fail:

```
========================= test session starts ==========================
collected 1 item

test_main.py::test_read_root PASSED                               [100%]
========================= 1 passed in 0.15s ============================
```

---

## 5️⃣ The Red-Green Cycle (Sabse Important Concept)

Ye **Test-Driven Development (TDD)** ka bunyadi rhythm hai, 3 steps mein:

1. **RED** — Pehle ek failing test likho, us cheez ke liye jo abhi exist hi nahi karti.
2. **GREEN** — Ab minimum code likho jo us test ko pass kara de.
3. **Refactor** — Code ko clean/improve karo, lekin tests green (passing) rehni chahiye.

### Practical Example:

**Step 1 — RED:** Pehle ek test likho us endpoint ke liye jo abhi bana hi nahi:

```python
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

Run karo:
```
pytest test_main.py::test_health_check -v
```

Output — **FAIL** hoga kyunke `/health` route exist hi nahi karta:
```
test_main.py::test_health_check FAILED                            [100%]
========================= FAILURES =========================
_________________ test_health_check _________________
    def test_health_check():
        response = client.get("/health")
>       assert response.status_code == 200
E       assert 404 == 200
========================= 1 failed in 0.12s ============================
```

Ye **RED** state hai — test batati hai `/health` exist nahi karta (404 aa raha hai, expected tha 200).

**Step 2 — GREEN:** Ab `main.py` mein ye endpoint add karo:

```python
@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

Test dobara run karo:
```
pytest test_main.py::test_health_check -v
```

Output:
```
test_main.py::test_health_check PASSED                            [100%]
========================= 1 passed in 0.14s ============================
```

Ye **GREEN** state hai. Ek complete red-green cycle mukammal hua.

> **Idea ye hai**: pehle failing test likho (ye batati hai kya banana hai), phir sirf itna code likho jo usko pass karaye — na kam, na zyada.

---

## 6️⃣ POST Requests Test Karna

POST request data (body) bhejti hai server ko. Test karne ka tareeqa:

```python
def test_create_item():
    response = client.post(
        "/items",
        json={"name": "Widget", "price": 9.99}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Widget"
    assert "id" in response.json()
```

Key point: **`json=` parameter** — ye Python dictionary ko automatically JSON mein serialize karke request body mein bhej deta hai. FastAPI ka `TestClient` khud handle karta hai serialization (aapko manually `json.dumps()` karne ki zaroorat nahi).

Note: `201` status code use hota hai jab koi **naya resource create** ho (POST ka standard response), `200` ke bajaye.

---

## 7️⃣ Response Ki Details Check Karna

Test sirf status code nahi, response ka **har hissa** check kar sakti hai:

```python
def test_response_structure():
    response = client.get("/items/1")
    # Status code
    assert response.status_code == 200
    # Response body
    data = response.json()
    assert "id" in data
    assert "name" in data
    assert isinstance(data["price"], float)
    # Headers
    assert response.headers["content-type"] == "application/json"
```

Yahan 3 tarah ki checks ho rahi hain:
1. **Status code** — request successful thi ya nahi.
2. **Body content** — kya keys mojood hain (`"id" in data`), aur kya data type sahi hai (`isinstance(data["price"], float)`).
3. **Headers** — response ke metadata, jaise `content-type`.

---

## 8️⃣ Error Responses Test Karna

Sirf "success case" test karna kafi nahi — **error cases** (jinhe "unhappy path" kaha jata hai) bhi utni hi important hain:

```python
def test_item_not_found():
    response = client.get("/items/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_invalid_input():
    response = client.post(
        "/items",
        json={"name": ""}  # Empty name should fail
    )
    assert response.status_code == 422  # Validation error
```

- **404** — jab koi resource exist nahi karta (yahan item id `99999` nahi mila).
- **422** — jab validation fail ho (jaise `name` khali string di, jo FastAPI/Pydantic ki validation rules ke khilaf hai).

`.lower()` istemal isliye kiya taake case-insensitive comparison ho (chahe message "Not Found" ho ya "not found").

---

## 9️⃣ Complete Test Example — Task API

Ye ek pura example hai jo aap course mein banayenge (Task API). File: `test_tasks.py`:

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestTaskAPI:
    """Tests for task endpoints."""
    
    def test_create_task(self):
        """POST /tasks creates a new task."""
        response = client.post(
            "/tasks",
            json={"title": "Learn testing", "description": "Write tests first"}
        )
        assert response.status_code == 201
        assert response.json()["title"] == "Learn testing"
        assert response.json()["status"] == "pending"
    
    def test_list_tasks(self):
        """GET /tasks returns all tasks."""
        response = client.get("/tasks")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_task(self):
        """GET /tasks/{id} returns single task."""
        # First create a task
        create_response = client.post(
            "/tasks",
            json={"title": "Fetch me"}
        )
        task_id = create_response.json()["id"]
        # Then fetch it
        response = client.get(f"/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Fetch me"
    
    def test_task_not_found(self):
        """GET /tasks/{id} returns 404 for missing task."""
        response = client.get("/tasks/99999")
        assert response.status_code == 404
    
    def test_create_task_without_title(self):
        """POST /tasks without title returns 422."""
        response = client.post(
            "/tasks",
            json={"description": "Missing title"}
        )
        assert response.status_code == 422
```

**Important cheez notice karo:** class ka naam `TestTaskAPI` hai — **pytest sirf un classes ko test class samajhta hai jinke naam `Test` se shuru hote hain**, aur sirf un methods ko test samajhta hai jo `test_` se shuru hote hain. Isi tarah `self` parameter har method mein hai kyunke ye class ke methods hain.

`test_get_task` mein dhyan do: pehle `client.post()` se ek task banaya, uski `id` nikali, phir usi `id` se `GET` request ki. Ye pattern isliye zaroori hai kyunke **har test independent honi chahiye** — kisi fixed/hardcoded ID pe depend nahi karni chahiye (ye "Common Mistakes" section mein bhi discuss hoga).

Output run karne pe:
```
$ pytest test_tasks.py -v
========================= test session starts ==========================
test_tasks.py::TestTaskAPI::test_create_task PASSED
test_tasks.py::TestTaskAPI::test_list_tasks PASSED
test_tasks.py::TestTaskAPI::test_get_task PASSED
test_tasks.py::TestTaskAPI::test_task_not_found PASSED
test_tasks.py::TestTaskAPI::test_create_task_without_title PASSED
========================= 5 passed in 0.23s ============================
```

---

## 🔟 Test Organization Tips (Best Practices)

**a) Naam clear rakho:**
```python
# Good - describes what's being tested
def test_create_task_with_description():

# Bad - vague
def test_task():
```
Test ka naam khud explain karna chahiye ke wo kya test kar rahi hai — bina code padhe.

**b) Ek concept ke liye ek assertion (jab mumkin ho):**
```python
# Good - focused
def test_create_returns_201():
    response = client.post("/tasks", json={"title": "Test"})
    assert response.status_code == 201

def test_create_returns_task_with_id():
    response = client.post("/tasks", json={"title": "Test"})
    assert "id" in response.json()

# Acceptable - related assertions
def test_create_task():
    response = client.post("/tasks", json={"title": "Test"})
    assert response.status_code == 201
    assert "id" in response.json()
```
Idea: agar test fail ho, to failure message se turant pata chalna chahiye ke **exactly kya galat hai**. Lekin closely related assertions ek saath rakhna bhi theek hai (over-splitting zaroori nahi).

**c) Classes se related tests ko group karo:**
```python
class TestTaskCreation:
    def test_with_title_only(self): ...
    def test_with_description(self): ...
    def test_without_title_fails(self): ...

class TestTaskRetrieval:
    def test_get_existing(self): ...
    def test_get_missing(self): ...
```
Isse bade test suites organized aur readable rehte hain.

---

## 1️⃣1️⃣ Hands-On Exercise (Practice Karne Ke Liye)

Ye exercise Lesson 1 ke `/` endpoint ke liye hai:

**Step 1** — `test_main.py` banao:
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_returns_200():
    """GET / returns 200 status."""
    response = client.get("/")
    assert response.status_code == 200

def test_root_returns_message():
    """GET / returns greeting message."""
    response = client.get("/")
    assert "message" in response.json()
```

**Step 2** — Run karo:
```
pytest test_main.py -v
```

**Step 3** — RED: Ek naya failing test add karo:
```python
def test_greeting_with_name():
    """GET /greet/{name} returns personalized greeting."""
    response = client.get("/greet/Alice")
    assert response.status_code == 200
    assert response.json()["message"] == "Hello, Alice!"
```

**Step 4** — GREEN: `main.py` mein ye endpoint add karo taake test pass ho jaye.

**Step 5** — Saari tests dobara run karo, confirm karo kuch aur break to nahi hua (**regression check**).

---

## 1️⃣2️⃣ Common Mistakes (3 Aam Ghaltiyan)

**Ghalti 1 — `app` import karna bhool jana:**
```python
# Wrong - app not imported
def test_something():
    response = client.get("/")  # client is undefined

# Correct
from main import app
client = TestClient(app)
```

**Ghalti 2 — Non-JSON response par `.json()` call karna:**
```python
# Wrong - 204 has no body
def test_delete():
    response = client.delete("/items/1")
    assert response.json()["deleted"] == True  # Fails!

# Correct
def test_delete():
    response = client.delete("/items/1")
    assert response.status_code == 204
```
Wajah: **204 No Content** status ka matlab hai response mein koi body hi nahi hoti, isliye `.json()` call karna error dega.

**Ghalti 3 — Tests jo ek dusre par depend karti hain:**
```python
# Wrong - test_get assumes test_create ran first
def test_create():
    client.post("/items", json={"name": "Widget"})

def test_get():
    response = client.get("/items/1")  # Assumes ID 1 exists

# Correct - each test is self-contained
def test_get():
    # Create first
    create_response = client.post("/items", json={"name": "Widget"})
    item_id = create_response.json()["id"]
    # Then get
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
```
Ye sabse important mistake hai: **har test khud-mukhtar (self-contained) honi chahiye**. Test order pe depend nahi hona chahiye kyunke pytest tests ko kisi bhi order mein run kar sakta hai, aur agar ek test fail ho jaye to doosri bhi galat waja se fail ho sakti hai.

---

## 1️⃣3️⃣ Manually Tests Kyun Likhein?

Ye ek **skill** build karne ke baare mein hai, sirf commands run karne ke baare mein nahi. Jab aap khud haath se test likhte ho:

- Samajh aati hai ke **useful test** kya banati hai.
- Aap **edge cases** pehchan lete ho jo cover karne chahiye.
- Aap **AI-generated tests ko critically evaluate** kar sakte ho.
- Aap **failing tests ko confidently debug** kar sakte ho.

Baad ke lessons mein AI se test generate karwayenge, lekin quality ka judge **aap** honge, passive consumer nahi.

---

## 1️⃣4️⃣ Try With AI (3 Prompts)

Manual exercises complete karne ke baad, ye 3 prompts AI ke saath practice karne ke liye diye gaye hain:

**Prompt 1 — Apni Tests Review Karwao:**
```
Here are my tests for a Task API:
[paste your test_tasks.py]

What edge cases am I missing? Don't write the tests for me—just list what scenarios I should consider adding.
```
> **Seekhna ye hai:** Aap ne tests khud likhi, ab AI se sirf **gaps** poochho — AI se tests likhwao mat, sirf missing scenarios ki list mangwao.

**Prompt 2 — Failure Samajhna:**
```
My test is failing with this error:
AssertionError: assert 404 == 200

Here's my test:
def test_get_task():
    response = client.get("/tasks/1")
    assert response.status_code == 200

What's happening and how do I debug it?
```
> **Seekhna ye hai:** Test failures ko interpret karna ek core skill hai. AI error ka matlab explain kar sakta hai, lekin fix ko samajhna aapka kaam hai.

**Prompt 3 — Tests Refactor Karna:**
```
I have tests that repeat setup code:
def test_create():
    client.post("/tasks", json={"title": "Test"})
    ...
def test_get():
    client.post("/tasks", json={"title": "Test"})
    ...

How can I use pytest fixtures to reduce duplication?
Explain the concept before showing code.
```
> **Seekhna ye hai:** **Fixtures** pytest ka ek pattern hai shared setup code ke liye (repeat setup avoid karne ke liye). Ye page fixtures ko detail mein cover nahi karta — sirf naam introduce karta hai — lekin concept ye hai: agar multiple tests ko same setup chahiye (jaise ek task create karna), to har baar wahi code likhne ke bajaye ek reusable "fixture" function banate hain jo pytest automatically har test ko provide kar deta hai.

---

## 1️⃣5️⃣ Reflect on Your Skill (Apni Custom Skill Improve Karna)

Ye page ke end mein hai — course ke earlier lesson mein aap ne ek `fastapi-agent` naam ki custom AI skill banayi thi. Ab is lesson ke baad, us skill ko test aur improve karna hai:

**Test Your Skill:**
```
Using my fastapi-agent skill, help me write pytest tests for a FastAPI endpoint.

Does my skill include patterns for TestClient usage, fixtures, and conftest.py setup?
```

**Gaps Identify karo, apne aap se poochho:**
- Kya meri skill mein pytest test structure aur naming conventions shamil hain?
- Kya ye fixture patterns handle karti hai (shared setup/teardown ke liye)?
- Kya ye red-green testing cycle cover karti hai?

**Skill Improve karo:**
```
My fastapi-agent skill is missing pytest testing patterns.

Update it to include TestClient usage, fixture patterns, conftest.py organization,
and the red-green testing cycle for TDD.
```

---

### Khulasa (Summary)

Is poore page ka core message: **Pytest + FastAPI TestClient** use karke aap apne endpoints ke liye tests likhte ho jo:
- Success cases (200, 201) check karte hain
- Error cases (404, 422) check karte hain
- Response body, status code, aur headers verify karte hain
- Self-contained hote hain (koi test dusri pe depend nahi karti)
- Red (fail) → Green (pass) cycle follow karte hain

---

# Pytest Fixtures — Beginner Level Explanation

## Problem Kya Hai? (Fixtures Kyun Chahiye)

Pehle wahi example yaad karo jo humne dekha tha:

```python
def test_get_task():
    create_response = client.post("/tasks", json={"title": "Fetch me"})
    task_id = create_response.json()["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200

def test_task_not_found():
    response = client.get("/tasks/99999")
    assert response.status_code == 404
```

Ab socho aapke paas **10-15 tests** hain, aur har test se pehle aapko:
- Ek task create karna hai
- Kabhi kabhi database ko clean karna hai
- Kabhi `TestClient` banana hai

Ye **same setup code** har test mein baar baar copy-paste karna padega. Ye **repetition** (DRY principle ke khilaf — "Don't Repeat Yourself") hai, aur agar setup ka tareeqa change ho jaye, to aapko **har jagah** update karna padega.

**Fixture** iska solution hai — ek **reusable setup function** jo pytest automatically aapki test mein "inject" (provide) kar deta hai.

---

## Fixture Kya Hai? (Simple Definition)

> Fixture ek **function** hai jo `@pytest.fixture` decorator ke sath likha jata hai. Ye kisi bhi cheez ko **prepare** karta hai jo test ko chahiye (jaise data, connection, ya object), aur phir wo cheez test ko "provide" kar deta hai.

Socho ise ek **waiter** ki tarah — aap (test) restaurant mein order dete ho "mujhe ek ready-made task chahiye", waiter (fixture) jaake wo taiyar kar ke aapko de deta hai.

---

## Sabse Simple Fixture Example

```python
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
```

Ab isko **line by line** samjho:

1. **`@pytest.fixture`** — ye decorator batata hai pytest ko: "ye ek normal function nahi, ek fixture hai."
2. **`def client():`** — fixture ka naam `client` hai. Ye `TestClient(app)` banata hai aur `return` kar deta hai.
3. **`def test_read_root(client):`** — dekho, test function ke parameter mein `client` likha hai. **Ye bilkul same naam hai jo fixture ka hai.**
4. Jab pytest `test_read_root` run karta hai, wo dekhta hai "isko `client` naam ka parameter chahiye" → pytest khud jaake `client` fixture ko call karta hai, uska return value leta hai, aur test ko de deta hai.

**Bohot important baat:** Aapko fixture ko khud call **nahi** karna — sirf test ke parameter mein uska naam likh do, pytest baaki khud sambhal leta hai. Ye pytest ki **"dependency injection"** system hai.

---

## Real Example — Task Create Karne Wali Fixture

Ab wapas Task API waale example pe aate hain, jahan har test ko ek task chahiye tha:

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def created_task():
    """Ek task create karta hai aur uska response return karta hai."""
    response = client.post("/tasks", json={"title": "Fetch me"})
    return response.json()

def test_get_task(created_task):
    task_id = created_task["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Fetch me"

def test_task_has_pending_status(created_task):
    assert created_task["status"] == "pending"
```

Dekho kitna clean ho gaya! Dono tests mein `created_task` parameter likha, aur pytest ne khud task create karke de diya — humein har jagah `client.post(...)` copy-paste nahi karna pada.

**Important:** Har test ke liye fixture **dobara** chalti hai (by default). Matlab `test_get_task` ke liye alag task banega, aur `test_task_has_pending_status` ke liye bilkul naya, alag task banega. Ye isliye zaroori hai taake **tests ek dusre ko affect na karein**.

---

## Setup aur Teardown — `yield` Keyword

Kabhi kabhi aapko test **khatam hone ke baad** bhi kuch karna hota hai — jaise database clean karna. Iske liye `return` ki jagah `yield` use karte hain:

```python
@pytest.fixture
def created_task():
    # --- SETUP (test se pehle) ---
    response = client.post("/tasks", json={"title": "Fetch me"})
    task = response.json()
    
    yield task   # <-- yahan test ko value milti hai, test chalti hai
    
    # --- TEARDOWN (test ke baad, cleanup) ---
    client.delete(f"/tasks/{task['id']}")
```

Yahan kya ho raha hai:
1. `yield` se **pehle** ka code = **setup** (test shuru hone se pehle chalta hai)
2. `yield task` = test ko `task` value mil jaati hai (jaise pehle `return` karta tha)
3. Test complete hone ke **baad**, code `yield` ke **neeche** wala chalta hai = **teardown/cleanup** (yahan humne task delete kar diya)

Isko yaad rakhne ka simple tareeqa: **"yield se upar = pehle, yield se neeche = baad mein."**

---

## `conftest.py` — Fixtures Ko Multiple Files Mein Share Karna

Agar aapke paas `test_main.py`, `test_tasks.py`, `test_users.py` — kayi test files hain, aur sab ko `client` fixture chahiye, to har file mein alag se likhna padega.

**Solution:** Ek special file banao naam `conftest.py` (naam bilkul yahi hona zaroori hai). Isme fixtures likho, aur pytest **automatically** har test file mein wo fixture available kar deta hai — bina import kiye!

```
testing/
├── conftest.py       ← yahan shared fixtures
├── test_main.py
├── test_tasks.py
└── test_users.py
```

`conftest.py`:
```python
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)
```

Ab `test_tasks.py` mein sirf:
```python
def test_create_task(client):   # koi import nahi chahiye 'client' ke liye!
    response = client.post("/tasks", json={"title": "Test"})
    assert response.status_code == 201
```

Pytest khud dhoondh leta hai `conftest.py` se `client` fixture, kisi import statement ki zaroorat nahi.

---

## Fixture Scope — Kitni Baar Chalti Hai?

By default, har test ke liye fixture **naye sirey se** chalti hai. Lekin aap ye control kar sakte ho `scope` parameter se:

```python
@pytest.fixture(scope="function")   # default — har test ke liye naya
def client():
    return TestClient(app)

@pytest.fixture(scope="session")    # pura test session mein sirf ek baar
def db_connection():
    conn = connect_to_database()
    yield conn
    conn.close()
```

| Scope | Kab Chalta Hai |
|---|---|
| `function` (default) | Har test function ke liye alag se |
| `class` | Har test class ke liye ek baar |
| `module` | Har test file ke liye ek baar |
| `session` | Poore test run mein sirf ek baar |

**Beginner tip:** Zyada tar cases mein `function` (default) hi theek hota hai kyunke har test independent rehna chahiye. `session` scope tab use karte hain jab koi cheez banana **mehnga/slow** ho (jaise real database connection) aur usko baar baar banane ki zaroorat na ho.

---

## Chhota Sa Khulasa (Summary)

| Concept | Matlab |
|---|---|
| `@pytest.fixture` | Function ko fixture banata hai |
| Test parameter mein fixture ka naam | Pytest automatically wo value provide karta hai |
| `return` | Simple value/object test ko de do |
| `yield` | Setup + Teardown dono karo (test se pehle aur baad mein) |
| `conftest.py` | Fixtures ko multiple test files mein share karo, bina import ke |
| `scope` | Control karo fixture kitni baar (re)chalti hai |

Yehi fixtures ka core concept hai — **repeated setup code ko ek jagah define karo, aur pytest ko wo automatically har test mein "inject" karne do.**
