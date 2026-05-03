# `with` — Behind the Cover

---

## Pehle samjho: "Resource" kya hota hai?

Python mein kuch cheezein hain jo **bahar ki duniya se connect** karti hain:

- **File** — hard disk se connect
- **Database Session** — database server se connect
- **Network connection** — internet se connect

Inhe **"Resource"** kehte hain.

**Resource ki ek problem hai:**

> Jab bhi koi resource use karo — OS (operating system) us resource ko **"busy"** mark kar deta hai. Jab tak tum us resource ko band nahi karte — OS us resource ko **"busy"** hi samjhta rehta hai.

---

## Problem: OS resources limited hote hain

Socho tumhara laptop hai. OS ek saath kitni files khuli rakh sakta hai? Kitne database connections? **Limited.**

Agar tum file kholo aur band na karo — OS us slot ko rokay rakhe ga:

```python
file = open("data.txt")   # OS ne ek slot diya
# ... kaam kiya
# close() bhool gaye
# OS ka slot abhi bhi busy hai
```

100 baar aisa karo — **100 slots busy** ho jayenge. Ek waqt aayega jab OS bolega:

> *"Mujhe aur slots nahi dene — tum pehle waale band karo."*

Isliye **close() zaroori hai** — taake OS ko pata chale:

> *"Ye resource free hai, koi aur use kar sakta hai."*

---

## Manual open/close ki 2 problems

**Problem 1 — Bhool jana:**

```python
file = open("data.txt")
# kaam kiya
# close() likhna bhool gaye — OS slot hamesha busy
```

**Problem 2 — Error aa jaye:**

```python
file = open("data.txt")
# yahan koi error aa gayi — program crash
file.close()   # ye line kabhi chalegi hi nahi
```

Error aate hi program ruk gaya — `close()` ka number aaya hi nahi. Resource hamesha ke liye busy reh gaya.

---

## Python ne socha — is problem ka solution chahiye

Python ne ek system banaya jis ka naam hai **Context Manager.**

Idea simple tha:

> *"Koi aisa mechanism banao jisme resource automatically open bhi ho aur automatically close bhi — chahe error aaye ya na aaye."*

Aur is mechanism ko use karne ka syntax rakha — **`with` block.**

---

## `with` ka actual kaam

```python
with open("data.txt") as file:
    # kaam karo
# yahan automatically close() ho gaya
```

`with` block ke andar 2 cheezein automatically hoti hain:

- **Block shuru** hote hi → `open()` / `connect()` → resource ready
- **Block khatam** hote hi → `close()` → resource free — **chahe error aaye ya na aaye**

---

## `__enter__` aur `__exit__` — asli engine

Ab ye samjho ke `with` **kaise** ye karta hai.

Jab bhi tum `with` use karte ho — Python peeche 2 special methods call karta hai:

| Method | Kab chalta hai | Kya karta hai |
|---|---|---|
| `__enter__` | Block shuru hote hi | Resource open/connect karo |
| `__exit__` | Block khatam hote hi | Resource close karo — error ho ya na ho |

Ye methods **class ke andar hidden** hote hain. Tumhe inhe call nahi karna padta — `with` khud call karta hai.

File ke case mein:
```python
with open("data.txt") as file:
#    ↑
#    open() ki class mein __enter__ hai → file open karo
#    block khatam → __exit__ → file.close() automatic
```

Session ke case mein:
```python
with Session(engine) as session:
#    ↑
#    Session class mein __enter__ hai → database se connect karo
#    block khatam → __exit__ → session.close() automatic
```

---

## Without `with` vs With `with`

**Without `with` — manual, risky:**
```python
session = Session(engine)   # khud open
# kaam karo
# error aa gayi — close() kabhi nahi chala
session.close()             # khud close — bhool sakte ho
```

**With `with` — automatic, safe:**
```python
with Session(engine) as session:
    # kaam karo
    # chahe error aaye
# automatically close — guaranteed
```

---

## Ek Line Mein

> **`with` = resource ko safe use karne ka tareeqa — `__enter__` se open, `__exit__` se automatically close — chahe kuch bhi ho.**


-------


# `if` ka Behaviour — `return` ke Saath aur Bina `return` ke

---

## Case 1 — `if` ke andar `return` hai

```python
def get_task_by_filter(get_task: Update_task, ...):
    if get_task.title:
        tasks = session.exec(...).all()
        return tasks        # ← yahan function KHATAM

    if get_task.description:   # ← sirf tab chalega jab upar wala if False tha
        tasks = session.exec(...).all()
        return tasks        # ← function KHATAM

    if get_task.status:        # ← sirf tab chalega jab dono upar wale False the
        tasks = session.exec(...).all()
        return tasks
```

**`return` matlab: function wahan ruk jata hai — baaki koi bhi line nahi chalti.**

```
title diya  → pehla if True  → return → STOP (description/status if kabhi nahi chalega)
title nahi  → pehla if False → aage jao
description → doosra if True → return → STOP
status diya → teesra if True → return → STOP
```

> Ye **intentional** hai filter mein — sirf ek filter at a time check karna tha.

---

## Case 2 — `if` ke andar `return` nahi

```python
def update_task(...):
    if task.title:
        db_task.title = task.title       # koi return nahi

    if task.description:                 # ← hamesha check hoga
        db_task.description = task.description

    if task.status:                      # ← hamesha check hoga
        db_task.status = task.status

    session.add(db_task)   # ← teeno if ke baad ye chale ga
```

**`return` nahi hai — teeno `if` independently check hote hain, ek ke True/False hone se doosre pe koi asar nahi.**

```
title + status diya → pehla if True → title update → teesra if True → status update ✅
sirf status diya    → pehla if False → doosra if False → teesra if True → sirf status ✅
teeno diye          → teeno if True → teeno update ✅
```

> Ye **intentional** hai update mein — jo bhi fields bheje saari update ho jayen.

---

## Summary Table

| | `if` ke andar `return` | Baaki `if` chalenge? |
|---|---|---|
| **Filter** | ✅ Hai | ❌ Nahi — pehla match hote hi STOP |
| **Update** | ❌ Nahi | ✅ Haan — teeno independently chalte hain |

---

## Ek Line Mein

> **`if` ke andar `return` ho toh function wahan ruk jaata hai — baaki `if` blocks nahi chalte. `return` nahi ho toh saare `if` blocks apni apni condition ke mutabik independently chalte hain.**

---

