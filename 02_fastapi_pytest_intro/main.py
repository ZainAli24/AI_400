from fastapi import FastAPI

app = FastAPI(
    title="Zain Task API",
    description="A simple task management API created with FastAPI and tested with Pytest",
)

@app.get("/tasks")
def login_User() -> list[dict[str, int | str]]: # list[dict[str, int | str]] indicates that the return type is a list of dictionaries with string keys and values that can be either int or str:
    return [
        {"id": 1, "tasks": "Go to the grocery store"},
        {"id": 2, "tasks": "Walk the dog"},
        {"id": 3, "tasks": "Read a book"},
    ]


# Get a specific task by ID staticly

@app.get("/tasks/1")
def get_task_1() -> dict[str, int | str]:  # dict [str, int | str] indicates that the return type is a dictionary with string keys and values that can be either int or str:
    return {"id": 1, "tasks": "Go to the grocery store"}


@app.get("/tasks/2")
def get_task_2() -> dict[str, int | str]:  # dict [str, int | str] indicates that the return type is a dictionary with string keys and values that can be either int or str:
    return {"id": 2, "tasks": "Walk the dog"}

#----------------------


# Get a specific task by ID Dynamically
@app.get("/tasks/{task_id}")
def get_task(task_id: int) -> dict[str, int | str]:  # dict [str, int | str] indicates that the return type is a dictionary with string keys and values that can be either int or str:
    if task_id < 1:
        return {"error": "Task ID must be greater than 0"}
    return {"id": task_id, "tasks": f"Task number {task_id}"}


# Get a specific task by ID Dynamically with Query Parameter
# Query Parameter means that the parameter is passed in the URL after a question mark (?), it is optional and has a default value. 

@app.get("/tasks/{task_id}")
def get_task(task_id: int, included_details: bool = True) -> dict[str, int | str]:  
    if task_id < 1:
        return {"error": "Task ID must be greater than 0"}
    if included_details:
        return {"details": f"{included_details}", "id": task_id, "tasks": f"Task number {task_id}"}
    return {"id": task_id, "tasks": f"Task number {task_id}"}


# -----------------------------

# path parameters are commonly referred to as "dynamic parameters"

# Differenetiating between Path and Query Parameters:
# Path parameters are part of the URL path and are used to identify specific resources. They are required and must be provided in the URL.
# Query parameters are appended to the URL after a question mark (?) and are used to filter or modify the response. They are optional and can have default values.



# FastAPI natively handle async functions, allowing for non-blocking operations.
@app.get("/users/{user_id}/tasks/{task_id}")
async def get_user_task(user_id: int, task_id: int, include_details: bool = False) -> dict[str, int | str | bool]:
    if include_details:
        return {"user_id": user_id, "task_id": task_id, "details": f"Details included: {include_details}"}
    return {"user_id": user_id, "task_id": task_id}


# -----------------------------

