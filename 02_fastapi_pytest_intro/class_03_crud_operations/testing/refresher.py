from fastapi import FastAPI, HTTPException


app = FastAPI(title="Task Manager", description="Manage your daily tasks!")


Tasks = [
    {"id": 1, "description": "Make tea"},
    {"id": 2, "description": "Bring Milk"},
    {"id": 3, "description": "Code"},
]


@app.get("/tasks")
async def get_tasks() -> list[dict[str, int | str]]:
    return Tasks



# Path Parameter: get specific item from specific location:
# @app.get("/tasks/{task_id}")
# async def get_task(task_id: int) -> dict[str, int | str]:
#     if task_id >= 1:
#         for task in Tasks:
#             if task["id"] == task_id:
#                 return task
#         raise HTTPException(status_code=404, detail="Task not found!")
#     raise HTTPException(status_code=401, detail="please enter id that is greater than 0!")

# Query Parameter: filter items:
@app.get("/tasks/{task_id}")
async def get_task_with_details(task_id: int, include_details: bool = False):
    if task_id >= 1:
        for task in Tasks:
            if task["id"] == task_id:
                if include_details:
                    task_copy = task.copy()
                    task_copy["details"] = f"This {task_id} is very important Task!"
                    return task_copy
                return task
        raise HTTPException(status_code=404, detail="Task NOT Found!")
    raise HTTPException(status_code=401, detail="Please enter number that is greater than 0")


