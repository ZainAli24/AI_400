from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException

class loginResponseData(BaseModel):
    id: int
    name: str
    email:str
    age:int
    
class loginResponseDataReturn(BaseModel):
    id: int 
    name: str
    email:str
    age:int
    is_active: bool = True

app = FastAPI()


@app.get("/login")
def login_data(id: int, name:str, email:str, age:int) -> loginResponseDataReturn:
    return loginResponseDataReturn(id=id, name=name, email=email, age=age)


@app.post("/register")
def register_data(data:loginResponseData) -> loginResponseDataReturn:
    if data.id == 0:
        raise HTTPException(status_code=400, detail="ID 0 is not allowed! 😫, error created by Zain 🤞🏼")
    return loginResponseDataReturn(**data.model_dump())


# Response body with return loginResponseData:

# {
#   "name": "zain",
#   "email": "ali",
#   "age": 21
# }


# Response body with return loginResponseDataReturn:
	
# Response body

# {
#   "name": "zain",
#   "email": "ali",
#   "age": 21,
#   "is_active": true
# }


@app.delete("/delete_user/{user_id}")
def delete_user(user_id: int):
    return {"message": f"User with ID {user_id} has been deleted."}



@app.put("/update_user/{user_id}")
def update_user(user_id: int, data: loginResponseData):
    return {"message": f"User with ID {user_id} has been updated.", "data": data}
# In PUT, the entire resource is replaced with the new data provided.


@app.patch("/minor_update_user/{user_id}")
def minor_update_user(user_id: int, name: str = None, email: str = None):
    updates = {}
    if name:
        updates["name"] = name
    if email:
        updates["email"] = email
    return {"message": f"User with ID {user_id} has been partially updated.", "updates": updates}
# partially means updating only specific fields of a resource without replacing the entire resource.

