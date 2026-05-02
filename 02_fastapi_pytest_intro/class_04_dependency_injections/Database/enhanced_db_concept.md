# Mere Concepts — PostgreSQL, Neon, ORM, Driver & SQLModel

---

## 1. PostgreSQL — Database Software

PostgreSQL ik **database software** hai jahan data rakha jata hai. Agar hum chahe toh isse **local ya kisi server pe install** karke khud manage kar sakte hai. Yani phir humein sab kuch **khud manage** karna hoga:

- Security
- Performance
- Collections / Backups
- Server maintenance

Matlab poora database ka management humari zimmedari hogi.

---

## 2. Neon — Database Managed Service

Neon kya karta hai? Neon apne paas **cloud pe PostgreSQL database ko host** karta hai aur kehta hai ke:

> "Database management mein khud kar loon ga — security, performance, backup, server — sab kuch mein manage kar loon ga. Tum bus database use karo."

Toh Neon **khud koi database nahi hai**, ye **database ki managed service provide karta hai**. Yani Neon tumhein PostgreSQL database deta hai lekin uska management Neon khud karta hai.

---

## 3. SQL — Database Ki Language

Database se baat karne ke liye koi na koi **language** hoti hai jaise **SQL (Structured Query Language)** — is ke through hum database se baat karte hai.

**Problem:** Humein database se baat karne ke liye pehle us ki language (SQL) ko seekhna hoga.

---

## 4. ORM — Apni Language Mein Database Se Baat Karo

Jab bhi hum **TypeScript ya Python** mein kaam kar rahe ho toh hum **apni hi language mein database se baat** kar sakte hai — bina koi SQL language likhe. Ye kaam **ORM** karta hai.

**Different languages mein different ORM hote hai:**

- **Python** mein → **SQLAlchemy** (ye ik ORM hai)
- Hum Python mein query likhte hai aur ORM hamari **Python language ko SQL (database language) mein convert** karta hai

SQLAlchemy mein ye option bhi hai ke hum **direct SQL language** bhi use kar sakte hai database se baat karne ke liye.

---

## 5. Database Driver — Database Tak Query Le Jaana

ORM toh hamari Python query ko SQL mein convert kar deta hai — bus **iska kaam khatam**.

Ab is query ko **database tak le jaana**, database se **connection karna**, baat karna — ye sab kaam **PostgreSQL database ka driver** karta hai jis ka naam hai:

### `psycopg2-binary`

Ye driver:

- Database se **connect** karta hai
- Password, URL maangta hai
- Database tak **query le kar jaata** hai
- Aur **response waapis laata** hai database se

---

## 6. SQLModel — ORM + Data Validation

Hum jo ORM use kar rahe hai woh **SQLModel** hai. Ye **SQLAlchemy aur Pydantic ka combination** se bana hai, yani is mein humein:

- **ORM** bhi milta hai (SQLAlchemy ki wajah se)
- **Data Validation** bhi milti hai (Pydantic ki wajah se)

---

## 7. SQLModel Class — Python Class + Database Table

Hum code mein jo **class bana rahe hai** ye Python class hai. Is mein hum ne **SQLModel class ko pass (inherit)** kiya hai — jis tarah hum Pydantic mein class mein `BaseModel` pass karte hai, isi tarah hum ne **SQLModel ki class pass ki** hai apni class mein.

SQLModel ki class:

- **Data validation** bhi karti hai
- **ORM ki saari power** bhi hoti hai is mein

---

## 8. `table=True` — Class Ka Database Mein Table Banega

Jab hum `table=True` likhte hai toh iska matlab ye hai ke:

> Is class ka **database mein table banega**.

Jab hum `table=True` likhte hai toh SQLModel ki class dekhti hai ke ye class database mein table banegi — toh wo is ko **database table ki tarah handle** karta hai.

---

## 9. `primary_key=True` — Unique Pehchaan

Jab hum class ki kisi property ko `primary_key=True` karte hai toh iska matlab ye hai ke:

- Jo is class ka table banega, us mein ye property yani ye **database ka column PRIMARY KEY** hoga
- **Primary Key** matlab **unique pehchaan** — yani unique hoga, is ki ik **unique ID** hogi
- **Hamesha jo primary key hoti hai woh system ya database dete hai** — koi user apni marzi se koi primary key nahi deta
- Is liye hum ne primary key mein koi **default value nahi pass ki** — is ko primary key **database dega**

---

## 10. Poora Flow — SQLModel Kaise Kaam Karta Hai

Jab SQLModel (jo hum ne apni class mein inherit ki hai) ye dekhta hai ke:

1. **`table=True`** hai → matlab ye class sirf Python class nahi hai, ise sirf validate nahi karna
2. **`primary_key=True`** hai → yani is class/table ke andar `id` column ko unique key deni hai database ne

Toh SQLModel class samajhti hai ke:

> Ye sirf Python class nahi hai — is ko **ORM use karke database query ke liye ready karna hai** aur is class mein jo variable/property(class is a table and its variables is a column in database) primary key true hai us **column ki unique key database generate karega**.

---


<br>

## 11. Engine — Database Connection Ka Manager

Sab se pehle humein database se **connection bnane ke liye engine ki zaroorat** hai. Engine decide karta hai:

- **Kab** database se connection banana hai
- **Kab** connection close karna hai
- **Kitne** maximum connections hone chahiye

Yani engine ik **manager** hai. Aur `psycopg2-binary` toh connection bnata hai, lekin **engine decide karta hai ke kab connection banana hai, kab close karna hai, kitne max connection hone hai** — toh engine database se baat karne ke liye `psycopg2-binary` ko use karta hai lekin decide khud karta hai ke kab database connection bnana hai kab close ye sab.


```python
engine = create_engine(os.getenv("DATABASE_URL"), echo=True)
```

---

## 12. Table Create Karna — `SQLModel.metadata.create_all(engine)`

Ab database mein connection toh ban gaya hai engine ke through, lekin database mein **table kaise create karein**?

Is line mein **SQLModel dekhta hai** ke jis class mein `table=True` hai, us class ke saare variables/properties ko leta hai, **metadata mein rakhta hai**, aur `create_all` se in saare variables ka ik table bna deta hai ye kaam wo **engine ko bolta hai** — phir engine ye kaam karta hai:

```python
SQLModel.metadata.create_all(engine)
```

Aur haan — **table sirf ik baar create karte hai**. Jab table ik baar create ho jaye, phir us pe operations perform karte hai.

---

## 13. Session — Tables Se Interact Karna

Ab table bhi create ho gaya hai. Ab hum us table se **interact Session ke through** karte hai.

Session matlab — tables mein jo bhi **operations** hote hai jaise data input diya, update kiya, ya delete kiya — ye sab kaam **Session** karta hai. Yani ik **session start hota hai**, jo bhi database mein tables se conversation hoti hai wo hoti hai, aur jab conversation khatam toh wo **session close**.

```python
def get_session():
    session = Session(engine)
    yield session
```

---

## 14. POST Request — Data Add Karna (session.add, commit, refresh)

Is line mein hum session ke through session ko bol rahe hai:

### `session.add(task)` — Yar session, ye task add kardo database table mein

### `session.commit()` — Yar session, is data ko ab save kardo table mein

### `session.refresh(task)` — Database Se Latest Data Waapis Lao Python Object Mein

Jab hum `session.add(task)` karte hai toh task object abhi sirf **Python mein** hai. Jab `session.commit()` hota hai toh ye data **database mein save** ho jata hai — aur database us task ko ik **unique id (primary key) deta hai**. Lekin hamara Python ka `task` object ko abhi bhi ye **nahi pata** ke database ne usse kya id di.

Toh `session.refresh(task)` kehta hai ke:

> "Yar database se jaake is task ka **latest data le kar aa** aur is **Python object mein update kar**."

Isi liye **refresh ke baad** return mein tumhein **poora object milta hai (id ke sath)**, aur **bina refresh ke khali object aata hai** kyunke Python object ko database wali id pata hi nahi thi.

```python
@app.post("/tasks")
def create_task(task: Tasks, session: Session = Depends(get_session)):
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

---

## 15. GET Request — Data Lena (select, exec, get)

### Saare Tasks Lena

Get request mein hum Tasks table ke saare data ko get karne ke liye hum phir session ko kehte hai: **session.exec** yani session yar **execute karo** aur **select karo** is Tasks table se **saari rows** yani sara data, us ko return karo:

```python
tasks = session.exec(select(Tasks)).all()
```

### Ik Specific Task Lena (By ID)

Agar humein ik task get karna ho toh hum us task ki **id pass karke** us task id ki base par us id ki row ka data le sakte hai: **session.get(Tasks, task_id)** yani is Tasks class mein se is id ki base par session yar **data le kar ao**:

```python
task = session.get(Tasks, task_id)
```

---

<br>

## 16. Session Ka "Tracking" System — `session.add()` INSERT ya UPDATE?

Jab tum ye likhte ho:

```python
tasker = session.get(Tasks, task_id)
```

Session sirf data nahi lata — **session us object ko "track" karna shuru kar deta hai.**

Matlab session ke dimagh mein yeh save ho jata hai:

> *"Ye `tasker` object — ye database mein **already exist** karta hai, iska id = 2 hai."*

---

### Ab `session.add()` Kaise Decide Karta Hai?

Session ke paas ek rule hai:

| Object ka halat | `session.add()` kya karta hai |
|---|---|
| **Naya object** — id `None` hai, session ne kabhi dekha nahi | `INSERT` — naya record banao |
| **Tracked object** — session ne pehle `get()` se liya tha | `UPDATE` — existing record update karo |

---

### Tumhara Code Step by Step

```python
tasker = session.get(Tasks, task_id)
# ✅ Session ne socha: "id=2 wala task database mein hai, main ise track kar raha hun"

tasker.title = task.title
tasker.description = task.description
# ✅ Session ne socha: "tracked object mein changes aa gaye"

session.add(tasker)
# ✅ Session ne socha: "ye wahi tracked object hai jisko main pehle se jaanta hun
#    id=2 hai — toh INSERT nahi, UPDATE karo"

session.commit()
# ✅ Database mein UPDATE query chali: WHERE id = 2
```

---

### POST vs UPDATE — Farq

**POST mein:**
```python
task = Tasks(title="New Task")  # bilkul naya object — id=None
session.add(task)               # session ne socha: "ye naya hai — INSERT karo"
```

**PUT mein:**
```python
tasker = session.get(Tasks, 2)  # session ne track kiya — id=2
tasker.title = "Updated"
session.add(tasker)             # session ne socha: "ye tracked hai — UPDATE karo"
```

---

### Ek Line Mein

> **`session.get()` se jo object aata hai wo already "tracked" hota hai — session ko pata hota hai ke ye database mein exist karta hai — isliye `session.add()` INSERT nahi, UPDATE karta hai.**

---


session.commit() ka kaam hai:

▎ "Jo bhi changes tune kiye hain — wo ab permanently database mein save kar do."

Jab tak commit() nahi hota — changes sirf session ki memory mein hain, database mein nahi gaye.

------

#### session.refresh() Refresh working:
hum ne delete request mien session.refresh add nahe kiya jab ke add karte howe task post mien hum ne resfresh karke return kiya hai toh is ka concet kiya is tarah ke post mien task jo add kiya tha woh incomplete tha yani us mien id nahe thi toh wo return mien nahe aya kue ke id nahe thi , jab ke delete mien hum ne id de kar task get kiya pehle phir us complete task id ke sath us ko delete kiya toh return mien hum ne usi task ko return kiya jo hum ne delete kiya hai ye return mien a gya hai kue ke reuturn mien ye complete hai id , title , description teeno pehle se is ke pass hai toh ye return hogya hai, kia ye concept sahi hai.  

> Refresh tab chahiye jab Python object mein koi cheez missing ho jo database ne fill ki — DELETE mein kuch missing tha hi nahi.

<br>

---

## 17. `@app.on_event("startup")` — Sahi Waqt Pe Table Create Karna

Abhi ka code:

```python
def create_table():
    SQLModel.metadata.create_all(engine)

create_table()  # file run hote hi chalta hai
```

Ye kaam karta hai — lekin ye **file run hone pe** chalta hai, **FastAPI server start hone pe nahi**. Dono alag hain.

---

### Solution — FastAPI Ka Startup Event

FastAPI ke 2 events hain:

| Event | Kab |
|---|---|
| `startup` | FastAPI server start hone pe |
| `shutdown` | FastAPI server band hone pe |

Hum `startup` event use karein ge — yani:

> *"Jab FastAPI server start ho — tab `create_table()` function call ho."*

```python
@app.on_event("startup")
def on_startup():
    create_table()  # server start hote hi ye chalega
```

Bas itna karna hai — `create_table()` ki manual call hatao aur startup event mein daal do.

---

### `create_all()` Ka Kaam

Table exist karta hai ya nahi — ye check karna `create_all()` khud handle karta hai. Event ka kaam sirf itna hai ke **sahi waqt pe** `create_table()` ko call kare — baki sab `create_all()` dekh leta hai.

---

### Ek Line Mein

> **`create_table()` wahi hai — sirf uski call `file run` se hatake `server start` pe kar di — bas itna farq hai.**

---

### Multiple Tables — `create_all()` Ek Baar Mein Sab

Agar multiple tables banane hain toh kuch alag nahi karna — bas multiple classes `table=True` ke saath bana do:

```python
class Tasks(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str

class Users(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

class Products(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
```

`create_all()` khud dhundta hai ke kaun kaun si classes `table=True` hain — aur un sab ke tables **ek saath** bana deta hai:

```python
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)  # teeno tables ek saath ban jayenge
```

---

### Jo Table Pehle Se Exist Kare — Uska Kya?

`create_all()` andar se pehle **check** karta hai:

> *"Ye table database mein already exist karta hai kya?"*

- **Nahi hai** → table bana do ✅
- **Pehle se hai** → chodo, kuch mat karo ✅

Pehli baar `create_all()` chala → **teeno tables bane**

Doosri baar `create_all()` chala → **teeno already exist karte hain → kuch nahi hua**

> **`create_all()` sirf woh table banata hai jo exist nahi karta — jo pehle se hai usse chod deta hai.**

<br>

---

## 18. Separate Models Pattern — `TaskCreate` vs `Tasks`

### Pehle Problem Samjho

Abhi `Tasks` class ko POST request ke liye bhi use kar rahe hain — jis mein `id` field bhi hai:

```python
@app.post("/tasks")
def create_task(task: Tasks, ...):
```

Matlab user POST request mein ye bhi bhej sakta hai:

```json
{
  "id": 999,
  "title": "Learn SQL"
}
```

User khud `id` de raha hai — **ye galat hai** — id sirf database deta hai, user nahi.

---

### Solution — 2 Alag Classes

**Class 1 — `TaskCreate` — sirf user ki request ke liye:**

```python
class TaskCreate(SQLModel):  # table=True nahi — ye sirf validation ke liye hai
    title: str
    description: str | None = None
```

- `id` nahi hai — user id nahi de sakta ✅
- `table=True` nahi — database mein koi table nahi banega ✅
- Sirf ye check karta hai ke user ne `title` diya ya nahi ✅

---

**Class 2 — `Tasks` — sirf database ke liye:**

```python
class Tasks(SQLModel, table=True):  # ye database table hai
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = Field(default=None)
```

- Database mein table banta hai ✅
- `id` hai — database assign kare ga ✅

---

### Ab POST Request Mein Farq

**Pehle — galat:**
```python
@app.post("/tasks")
def create_task(task: Tasks, session: Session = Depends(get_session)):
    # user Tasks class bhej raha hai — id bhi bhej sakta hai ❌
    session.add(task)
```

**Ab — sahi:**
```python
@app.post("/tasks")
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    # user sirf title aur description bhejta hai — id nahi ✅
    db_task = Tasks(title=task.title, description=task.description)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task
```

---

### Step By Step Kya Hua

```
User ne bheja:
{ "title": "Learn SQL", "description": "ORM basics" }
        ↓
TaskCreate ne validate kiya — title hai? haan ✅
        ↓
Naya Tasks object banaya — id=None (database dega)
        ↓
Database mein save kiya — database ne id=1 di
        ↓
Return kiya poora Tasks object — id, title, description sab
```

---

### Dono Classes Ka Role

| Class | Kaam | `table=True` | `id` |
|---|---|---|---|
| `TaskCreate` | User ki request validate karna | ❌ Nahi | ❌ Nahi |
| `Tasks` | Database table | ✅ Haan | ✅ Haan |

---

### Ek Line Mein

> **`TaskCreate` user se data lene ke liye — `Tasks` database mein store karne ke liye — dono ka kaam alag hai isliye alag classes.**

---

### POST Mein Sahi Tareeqa — `Task_User` se `Tasks` object banana

**Galat — seedha `Task_User` object add karna:**
```python
def create_task(task: Task_User, session: Session = Depends(get_session)):
    session.add(task)   # ❌ Task_User mein table=True nahi — save nahi hoga
```

**Sahi — pehle `Tasks` object banao, phir add karo:**
```python
def create_task(task: Task_User, session: Session = Depends(get_session)):
    db_task = Tasks(title=task.title, description=task.description)
    session.add(db_task)    # ✅ Tasks object hai — database mein save hoga
    session.commit()
    session.refresh(db_task)
    return db_task
```

**Flow:**
```
User ne Task_User bheja → validate hua
        ↓
Tasks object banaya (id=None) — ye database wala hai
        ↓
session.add(db_task) → database mein save
        ↓
db_task return — id ke saath
```

<br>

---

## 19. `echo=True` — Database Conversation Terminal Mein Dikhao

Jab ORM Python query ko SQL mein convert karta hai aur database ko bhejta hai — ye sab **peeche hota hai**, tumhein kuch nazar nahi aata.

`echo=True` kehta hai:

> *"Jo bhi SQL query database ko bheji jaa rahi hai — aur jo bhi **response database se wapas aaya** — sab **terminal mein print** kar do."*

---

### Example

Jab tum GET request karte ho — terminal mein ye dikhta hai:

```sql
SELECT tasks.id, tasks.title, tasks.description FROM tasks
-- aur sath database ka response bhi: [(1, 'Learn SQL', 'ORM basics'), ...]
```

Jab POST karte ho:

```sql
INSERT INTO tasks (title, description) VALUES ('Learn SQL', 'ORM basics')
-- aur database ka response: INSERT 0 1 (matlab 1 row add hui)
```

---

### Faida Kya Hai?

Debugging mein kaam aata hai — tum **poori baat** dekh sakte ho jo database ke saath hui:
- ORM ne kya SQL banayi
- Database ko kya bheja
- Database ne kya response diya

---

### `echo=False` karo toh?

Koi bhi log terminal mein print nahi hoga — sab peeche chup chap hoga.

Production mein `echo=False` karte hain — development mein `echo=True` rakhte hain taake **poori database conversation** dekh sako.

---

> **`echo=True` = database ke saath jo bhi baat hui — query bhi, response bhi — sab terminal mein dikha do.**

<br>

---

## 20. `?sslmode=require` — Neon Ke Liye Secure Connection

### SSL kya hai?

**SSL (Secure Sockets Layer)** ek **encryption protocol** hai jo database server aur client ke beech **secure encrypted link** banata hai.

Matlab jo bhi baat database aur tumhare app ke beech ho — **password, data, queries** — sab **encrypted** ho jata hai. Koi beech mein pakad bhi le toh kuch samajh nahi aayega.

---

### Bina SSL Ke Kya Hota Hai?

Bina SSL ke database connection **khula** hota hai — jaise phone pe openly baat karo aur koi bhi sun sakta ho:
- Database ka **password** — koi beech mein pakad sakta hai
- Jo **data** aa ja raha hai — koi dekh sakta hai

---

### `?sslmode=require` ka matlab

```
DATABASE_URL=postgresql://user:password@ep-xxx.neon.tech/neondb?sslmode=require
```

Connection string ke end mein `?sslmode=require` kehta hai:

> *"Database se connect karo — lekin **sirf SSL encrypted connection** se. Bina SSL ke connection **allow mat karo**."*

---

### Neon Pe Specifically Kyun Zaroori Hai?

Neon ek **cloud database** hai — internet pe hai, local machine pe nahi. Neon ki policy hai ke sirf **secure SSL connection** accept kare — bina SSL ke connection **reject** kar deta hai:

```
❌ Connection refused — Neon ne reject kar diya
```

---

> **`?sslmode=require` = database aur app ke beech secure encrypted connection — Neon ke liye compulsory hai, bina iske connection reject hoga.**

<br>

---

## 21. `select().where()` — Filtered Queries

### Pehle Recall Karo — Abhi Kya Pata Hai

Abhi tumhein ye pata hai — **saare tasks lao:**

```python
session.exec(select(Tasks)).all()
```

Ye **har cheez** le aata hai — koi filter nahi.

---

### Problem — Agar Sirf Kuch Specific Data Chahiye?

Socho tumhare database mein 1000 tasks hain — lekin tumhein sirf **title mein "SQL" wale tasks** chahiye, ya sirf **koi specific description wale**.

Sab lao aur phir Python mein filter karo? — **Ye galat tareeqa hai.**

Sahi tareeqa — **database ko hi bolo ke filtered data do.**

---

### `where()` — Filter Lagao

```python
session.exec(select(Tasks).where(Tasks.title == "Learn SQL")).all()
```

Matlab:

> *"Tasks table se sirf woh rows lao jahan title = 'Learn SQL' ho."*

---

### Aur Examples

**Description se filter:**
```python
session.exec(select(Tasks).where(Tasks.description == "ORM basics")).all()
```

**ID se filter:**
```python
session.exec(select(Tasks).where(Tasks.id > 5)).all()
```
Sirf woh tasks jinka id 5 se zyada ho.

---

### `select()` vs `select().where()` — Farq

| | Kya karta hai |
|---|---|
| `select(Tasks)` | Poori table ka sara data lao |
| `select(Tasks).where(...)` | Sirf matching rows lao |

---

### Database Ke Saath Kya Hota Hai?

`where()` ke bina:
```sql
SELECT * FROM tasks          -- sab lao
```

`where()` ke saath:
```sql
SELECT * FROM tasks WHERE title = 'Learn SQL'   -- sirf matching lao
```

ORM tumhari `where()` condition ko **SQL WHERE clause** mein convert kar deta hai.

---

### Line Ka Matlab — Tumhari Wording Mein

```python
session.exec(select(Tasks).where(Tasks.description == "ORM basics")).all()
```

| Part | Matlab |
|---|---|
| `select(Tasks)` | Tasks table mein jao |
| `.where(Tasks.description == "ORM basics")` | sirf woh rows dhundo jahan description = "ORM basics" ho |
| `session.exec(...)` | ye query execute karo — database ko bhejo |
| `.all()` | jo bhi matching rows mile — **sab** le ao list mein |

> *"Session, Tasks table mein jao — jis bhi row ki description 'ORM basics' hai — us row ka data le kar ao — aur sab matching rows lao."*

---

> **`where()` = database ko bolo ke sirf filtered matching data do — poora data mat lao.**

<br>

---

## 22. `default` vs `default_factory` — Static vs Dynamic Value

### `default=datetime.utcnow()` — Static

```python
created_at: datetime = Field(default=datetime.utcnow())
```

Jab file **pehli baar load** hoti hai — `datetime.utcnow()` **ek baar** chalta hai — value aa jaati hai:

> `2026-05-02 14:49:00`

**Bas — ab ye function dobara nahi chale ga.**

Ye value **hamesha yahi rahegi** — chahe task 1 ghante baad banao, chahe 5 ghante baad — timestamp wahi purana `2026-05-02 14:49:00` hi aayega. Function ko dobara call hi nahi kiya — **static ho gayi.**

---

### `default_factory=datetime.utcnow` — Dynamic

```python
created_at: datetime = Field(default_factory=datetime.utcnow)
```

`default_factory` jo value aa jaaye — **woh nahi rakhta.**

Jab bhi **naya object bane** — jab bhi **naya request aaye** — `default_factory` `datetime.utcnow` function ko **fresh call** karta hai aur **us waqt ki nayi value** le aata hai.

Task 1 banao → function call → `2026-05-02 14:49:00` ✅
Task 2 banao 5 minute baad → function dobara call → `2026-05-02 14:54:00` ✅
Task 3 banao 1 ghante baad → function dobara call → `2026-05-02 15:49:00` ✅

Har baar **fresh value — dynamic.**

---

> **`default=` function ek baar chalata hai — value static ho jaati hai. `default_factory=` har naye object pe function dobara call karta hai — value hamesha fresh aur dynamic.**

<br>

---

## 23. `create_all()` Schema Limitation

### Pehle Yaad Karo — `create_all()` Kya Karta Hai

```python
SQLModel.metadata.create_all(engine)
```

Ye **nayi tables banata hai** — jo table exist nahi karta usse bana deta hai.

---

### Limitation — Existing Table Mein Change Nahi Karta

Socho tumne pehle ye class banayi aur table create ho gaya:

```python
class Tasks(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = Field(default=None)
```

Database mein table ban gaya — **3 columns: id, title, description.**

---

Ab tumne class mein **naya column add kiya:**

```python
class Tasks(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = Field(default=None)
    status: str = Field(default="pending")                         # naya column add kiya
    created_at: datetime = Field(default_factory=datetime.utcnow)  # ye bhi
```

Server restart kiya — `create_all()` chala —

**Database mein kuch nahi hua.** ❌

`create_all()` ne socha:

> *"Tasks table pehle se exist karta hai — mujhe kuch nahi karna."*

Naaye columns `status` aur `created_at` **database mein add nahi hue** — sirf Python class mein hain.

---

### Kya Hoga Agar Request Karo?

```
❌ Error — database mein column exist nahi karta
```

Python class mein column hai — database table mein nahi — **mismatch.**

---

### Solution — 2 Tareeqe

**Tareeqa 1 — Table drop karke dobara banao:**

Neon pe jaao — table delete karo — server restart karo — `create_all()` fresh table bana dega naaye columns ke saath.

⚠️ **Problem:** Poora data delete ho jayega.

---

**Tareeqa 2 — Alembic use karo:**

Alembic ek tool hai jo existing table mein **safely naaye columns add** karta hai — **data delete nahi hota.**

Ye advanced topic hai — abhi ke liye itna yaad rakho ke ye exist karta hai.

---

> **`create_all()` sirf nayi tables banata hai — existing table mein naaya column add karo toh `create_all()` kuch nahi karega, schema change ke liye ya table drop karo ya Alembic use karo.**

<br>

---

## 24. `datetime.utcnow` — 2 Problems

### Problem 1 — Brackets ❌

```python
created_at: datetime = Field(default_factory=datetime.utcnow())
#                                                           ^^
#                                                      brackets hai — GALAT
```

`default_factory=` ko **function reference** chahiye — brackets ke bina.

Brackets ke saath matlab: function abhi call karo aur **result do** — ye static ho jayega — bilkul wahi problem jo humne `default=` mein samjhi thi.

**Sahi:**
```python
created_at: datetime = Field(default_factory=datetime.utcnow)  # brackets nahi
```

---

### Problem 2 — `utcnow` Deprecated Hai ⚠️

`datetime.utcnow` Python 3.12 mein **deprecated** ho gaya — matlab future mein remove ho sakta hai.

**Naya sahi tareeqa:**
```python
from datetime import datetime, timezone

created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

`lambda` isliye — kyunke `datetime.now(timezone.utc)` ko argument chahiye, direct reference nahi de sakte — `lambda` ek chhota wrapper function hai jo har baar call hoga.

---

### Fixed Class:

```python
from datetime import datetime, timezone

class Tasks(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = Field(default=None)
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

---

> **`default_factory=` ko brackets ke bina function reference do — aur `utcnow` deprecated hai, naya tareeqa `lambda: datetime.now(timezone.utc)` hai.**

<br>

---

## 25. `response_model` — Response Ka Order Fix Karo

### Problem — Random Order Kyun Aata Hai?

`table=True` wali class SQLAlchemy ka database object hai — pure Pydantic model nahi. SQLAlchemy apni marzi se fields return karta hai — definition order guaranteed nahi:

```json
{
  "status": "pending",
  "title": "cricket",
  "created_at": "2026-05-02T10:19:56.366639",
  "id": 2,
  "description": "Evening play cricket"
}
```

---

### Fix — Alag `TaskResponse` Class Banao

Ek alag class **bina `table=True`** ke — sirf response ke liye — jis order mein chahiye us order mein fields likho:

```python
class TaskResponse(SQLModel):
    id: int
    title: str
    description: str | None
    status: str
    created_at: datetime
```

---

### Single Object Return — `response_model=TaskResponse`

```python
@app.post("/tasks", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
@app.get("/tasks/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskResponse)
@app.put("/tasks/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskResponse)
@app.delete("/tasks/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskResponse)
```

---

### List Return — `response_model=list[TaskResponse]`

Jahan `.all()` se array aati hai — wahan `list[TaskResponse]`:

```python
@app.get("/tasks", status_code=status.HTTP_200_OK, response_model=list[TaskResponse])
```

`list[TaskResponse]` matlab:

> *"Response mein `TaskResponse` objects ki **list** aayegi."*

---

### Poora Code — Response Model Ke Saath:

```python
class TaskResponse(SQLModel):
    id: int
    title: str
    description: str | None
    status: str
    created_at: datetime

@app.get("/tasks", status_code=status.HTTP_200_OK, response_model=list[TaskResponse])
@app.post("/tasks", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
@app.get("/tasks/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskResponse)
@app.put("/tasks/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskResponse)
@app.delete("/tasks/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskResponse)
```

---

> **Single object → `response_model=TaskResponse`, List → `response_model=list[TaskResponse]`.**

<br>

