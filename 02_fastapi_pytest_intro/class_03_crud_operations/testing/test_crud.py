import pytest
from fastapi.testclient import TestClient
from crud import app


client = TestClient(app)


# get tasks list:
def test_get_tasks():
    res = client.get("/tasks")
    assert res.status_code == 200
    assert res.json() == [
  {
    "id": 1,
    "title": "Go for Walk",
    "description": "Go for a walk in the park"
  },
  {
    "id": 2,
    "title": "Coding",
    "description": "Work on the FastAPI project"
  },
  {
    "id": 3,
    "title": "Ai-400 class",
    "description": "Attend the AI-400 class"
  }
]
    


# get task by id:
def test_get_one_task():
    res = client.get("/task/1")
    assert res.status_code == 200
    assert res.json() == {
  "id": 1,
  "title": "Go for Walk",
  "description": "Go for a walk in the park"
}


    res = client.get("/task/5")
    assert res.status_code == 404
    assert res.json() == {"detail": "Task not Found!"}

    res = client.get("/task/0")
    assert res.status_code == 401
    assert res.json() == {"detail": "Please enter number that is greater than 0"}
   



# add task:
def test_add_task():
    res = client.post("/add", json={
  "id": 90,
  "title": "Learning Python",
  "description": "Python Prject class 2hours 2 to 4"
}) 
    assert res.status_code == 200
    assert res.json() == {
  "id": 90,
  "title": "Learning Python",
  "description": "Python Prject class 2hours 2 to 4",
  "status": "Pending"
}
    


# update task:
def test_update_task():
    res = client.patch("/update/1", json={
  "title": "Python Projects",
  "description": "python by 50 projects"
})
    assert res.status_code == 200
    assert res.json() == {
  "status": "Updated Successfully",
  "Updated_task": {
    "id": 1,
    "title": "Python Projects",
    "description": "python by 50 projects",
    "status": "Pending"
  }
}
    


# replace updatation:
def test_update_task():
    res = client.put("/update/1", json={
  "id": 1013,
  "title": "WEB AGent",
  "description": "class on tuesday"
})
    assert res.status_code == 200
    assert res.json() == {
  "status": "Updated Successfully",
  "Updated_task": {
    "id": 1013,
    "title": "WEB AGent",
    "description": "class on tuesday",
    "status": "Pending"
  }
}
    

# delete  task:
def test_delete_task():
    res = client.delete("/tasks/90")
    assert res.status_code == 200
    assert res.json() == {"status": "Deleted Successfully", "Deleted task": {
  "id": 90,
  "title": "Learning Python",
  "description": "Python Prject class 2hours 2 to 4"
}}
    
    

    