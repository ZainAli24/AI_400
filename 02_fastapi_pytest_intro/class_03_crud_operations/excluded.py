from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


# ──────────────────────────────────────────
# Pydantic Models
# ──────────────────────────────────────────

class UserUpdate(BaseModel):
    name: str | None = None
    age: int | None = None
    city: str | None = None

class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    city: str = "Unknown"
    country: str = "Pakistan"


# ──────────────────────────────────────────
# Fake Database — ek user already saved hai
# ──────────────────────────────────────────

fake_user = {
    "id": 1,
    "name": "Zain",
    "age": 21,
    "city": "Karachi",
    "country": "Pakistan"
}


# ──────────────────────────────────────────
# Endpoint 1 — BUG wala (exclude_unset nahi)
# ──────────────────────────────────────────

@app.patch("/users/bug")
def update_user_bug(user_update: UserUpdate):
    update_data = user_update.model_dump()
    # model_dump() → sari fields return karta hai — None bhi
    fake_user.update(update_data)
    return {"message": "Updated (BUG wala)", "user": fake_user}


# ──────────────────────────────────────────
# Endpoint 2 — CORRECT wala (exclude_unset=True)
# ──────────────────────────────────────────

@app.patch("/users/correct")
def update_user_correct(user_update: UserUpdate):
    update_data = user_update.model_dump(exclude_unset=True)
    # exclude_unset=True → sirf jo user ne bheja
    fake_user.update(update_data)
    return {"message": "Updated (Correct wala)", "user": fake_user}


# ──────────────────────────────────────────
# Endpoint 3 — response_model_exclude_unset
# ──────────────────────────────────────────

@app.get("/users/profile", response_model=UserResponse, response_model_exclude_unset=True)
def get_user_profile(full: bool = False):
    if full:
        # sari fields set hain — sab return hongi
        return {"id": 1, "name": "Zain", "age": 21, "city": "Karachi", "country": "Pakistan"}
    else:
        # city aur country set nahi — response mein nahi aayenge
        return {"id": 1, "name": "Zain", "age": 21}


# ──────────────────────────────────────────
# Reset endpoint — fake_user wapas original pe
# ──────────────────────────────────────────

@app.post("/users/reset")
def reset_user():
    fake_user.update({"id": 1, "name": "Zain", "age": 21, "city": "Karachi", "country": "Pakistan"})
    return {"message": "Reset ho gaya", "user": fake_user}
