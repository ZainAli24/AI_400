from fastapi import FastAPI, HTTPException
from pydantic import Field, BaseModel
from typing import Literal


app = FastAPI(title="Task Manager App", description="Manage your tasks")





class Task(BaseModel):
    id:int
    title : str
    description : str | None = Field(default=None)


class UpdateTask(BaseModel):
    id: int | None = Field(default=None)
    title : str | None = Field(default=None)
    description : str | None = Field(default=None)



class TaskResponse(BaseModel):
    id:int
    title : str
    description : str | None = Field(default=None)
    status : Literal["Completed", "Pending"] = Field(default="Pending")


class TaskUpdateResponse(BaseModel):
    status: str = Field(default="Updated Successfully")
    Updated_task: TaskResponse





Tasks = [
    {"id": 1, "title": "Go for Walk", "description": "Go for a walk in the park"},
    {"id": 2, "title": "Coding", "description": "Work on the FastAPI project"},
    {"id": 3, "title": "Ai-400 class", "description": "Attend the AI-400 class"},
]


@app.get("/tasks")
async def get_tasks():
    return Tasks


@app.get("/task/{task_id}")
async def get_one_task(task_id: int):
    if task_id >=1:
        for task in Tasks:
            if task["id"] == task_id:
                return task
        raise HTTPException(status_code=404, detail="Task not Found!")
    raise HTTPException(status_code=401, detail="Please enter number that is greater than 0")




@app.post("/add")
async def add_task(task: Task) -> TaskResponse:
    Tasks.append(task.model_dump())  # convert the Pydantic model to a dictionary and append it to the list.
    Task_Response = TaskResponse(id=task.id, title=task.title, description=task.description)
    return Task_Response



@app.patch("/update/{task_id}")
async def update_task(task_id: int, updated_task: UpdateTask) -> TaskUpdateResponse:
    if task_id >=1:
        for task in Tasks:
            if task["id"] == task_id:
                if updated_task.title:
                    task["title"] = updated_task.title
                if updated_task.description:
                    task["description"] = updated_task.description
                if updated_task.id:
                    task["id"] = updated_task.id
                res = TaskUpdateResponse(Updated_task=task)
                return res
        raise HTTPException(status_code=404, detail="Task not Found!")
    raise HTTPException(status_code=401, detail="Please Enter Valid id that is greater than 0!")



@app.put("/update/{task_id}")
async def update_task(task_id: int, updated_task: TaskResponse) -> TaskUpdateResponse:
    if task_id >=1:
        for task in Tasks:
            if task["id"] == task_id:
                task.update(updated_task.model_dump())
                res = TaskUpdateResponse(Updated_task=task)
                return res
        raise HTTPException(status_code=404, detail="Task not Found!")
    raise HTTPException(status_code=401, detail="Please Enter Valid id that is greater than 0!")



@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    if task_id >=1:
        for task in Tasks:
            if task["id"] == task_id:
                Tasks.remove(task)
                print(Tasks)    
                return {"status": "Deleted Successfully", "Deleted task": task}
        raise HTTPException(status_code=404, detail="Task not Found!")
    raise HTTPException(status_code=401, detail="Please Enter Valid id that is greater than 0!")
