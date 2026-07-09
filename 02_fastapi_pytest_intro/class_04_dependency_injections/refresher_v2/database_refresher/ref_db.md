## Do alag SQLModel classes ka role

Tumhare code mein do classes hain:

```python
class Task(SQLModel, table=True):      # <-- yeh asli DATABASE TABLE hai
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = Field(default=None)


class CreatTask(SQLModel):             # <-- table=True NAHI hai
    title: str
    description: str | None = Field(default=None)
```

**`table=True` ka matlab kya hota hai?**

Jab tum `table=True` likhte ho, tab SQLModel/SQLAlchemy is class ko ek **real database table** ke sath "map" kar deta hai (`ORM mapping`). Matlab yeh class ka har object database ki ek row bann sakta hai — SQLAlchemy ko pata hota hai ke isay kis table mein, kaunse columns ke sath save karna hai.

`CreatTask` mein `table=True` nahi likha, is liye yeh sirf ek **normal Pydantic-jaisi class** hai — yeh sirf data ki **shape/validation** ke liye hai (request body check karne ke liye), database se iska koi taluq (mapping) nahi hai.

## Error kyun aaya

```python
@app.post("/create")
def create_task(task: CreatTask, session: Session = Depends(get_session)):
    session.add(task)
```

Yahan `task` parameter ka type `CreatTask` hai — jab user API call karta hai, FastAPI request body ko `CreatTask` ke instance mein convert kar deta hai.

Phir tum `session.add(task)` kar rahe ho — yani tum SQLAlchemy ko keh rahe ho "is object ko database mein save karne ke liye track karo".

Lekin SQLAlchemy `session.add()` mein sirf **mapped classes ke objects** accept karta hai — yani sirf woh objects jo `table=True` wali class se bane hon (yahan sirf `Task`).

`task` variable `CreatTask` ka object hai, jo mapped nahi hai — is liye error aaya:

```
sqlalchemy.orm.exc.UnmappedInstanceError: Class 'ref_db.CreatTask' is not mapped
```

Matlab: "yeh class kisi table se linked hi nahi, mein isay save kaise karun?"

## Simple analogy

- `CreatTask` = ek **form/receipt** jisme user ne data likha (sirf kagaz, database ka hissa nahi)
- `Task` = ek **actual filing cabinet ka drawer entry** (database row)

Tum seedha "form" ko cabinet mein nahi daal sakte — pehle us form ka data lekar ek asli "cabinet entry" (`Task` object) banani parti hai, phir usay `session.add()` karo.

## `Task.model_validate(task)` ka kaam

`Task.model_validate(task)` ka kaam sirf itna hai:

Yeh ek object ke fields se doosri class ka naya object bana deta hai.

```python
db_task = Task.model_validate(task)
```

Yeh andar se `task.title` aur `task.description` ki values nikalta hai, aur unhi values se ek naya `Task` object bana deta hai — jaise tum manually likho:

```python
db_task = Task(title=task.title, description=task.description)
```

Bas itna hi. Dono lines ka result same hai — `model_validate` sirf yeh manual kaam khud-ba-khud (automatically) kar deta hai, chahe fields kitni bhi ho.



------------------------------


# Understanding concept:  `Task.model_validate(tasker)`

Yani is line mein hum keh rahe hain ke: Task.model_validate(task) — yeh jo task object hai (jo CreatTask se bana hai),
iski properties nikalo, aur inhe validate karo Task class se — yani check karo ke Task ke ander bhi yehi fields hain
(title, description) sahi type ke sath. Validate hone ke baad, unhi properties ko Task class ke ander de kar uska naya
object bana do.

Farak sirf itna: validate CreatTask se nahi, balke Task se hota hai — kyunki jis class ka model_validate call kar rahe
ho (Task.model_validate), check usi ke schema ke against hota hai.


------------------------------


# `response_model` review (Task ko response_model banana)

```python
@app.post("/create", response_model=Task)
@app.get("/tasks", response_model=list[Task])
```

**Jo sahi hai:** Yeh dono FastAPI mein valid syntax hai — `response_model` batata hai ke response is shape mein hona chahiye, aur extra/unwanted fields filter ho jayengi. Koi crash ya validation error nahi aata.

**Jo "issue" hai (best-practice ki tarah):** `response_model` ke liye `Task` use kiya gaya hai — jo table model hai (wahi class jo database se mapped hai). Yeh chalta hai, lekin recommended tareeqa yeh hai ke response ke liye ek alag "Read" class banayi jaye, jaise:

```python
class TaskRead(SQLModel):
    id: int
    title: str
    description: str | None = None
```

**Kyun?** Kyunki `Task` (table model) ko directly response_model ke tor pe use karne se risk hota hai: agar kabhi `Task` mein koi sensitive ya internal field add ho (jaise `password`, `owner_id`, `is_deleted`), to woh automatically API response mein expose ho jayegi — kyunki `response_model=Task` sab kuch dikhata hai jo `Task` mein hai.

Abhi `Task` mein sirf `id`, `title`, `description` hain — koi sensitive data nahi — is liye filhal koi practical nuksaan nahi. Lekin project barhne par table model aur response model ko separate rakhna best practice hai (jaise input ke liye `CreatTask` alag hai, waise output ke liye bhi alag class honi chahiye).

**Summary:** Abhi kaam sahi chal raha hai, koi error nahi — bas future ke liye yaad rakhna: table model ko seedha response_model mat banao, alag Read schema banao.
