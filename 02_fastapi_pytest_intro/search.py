from fastapi import FastAPI

app = FastAPI(title="Search API", version="1.0.0")

@app.get("/")
def read_root():
    """Root endpoint that returns a welcome message"""
    return {
        "message": "Welcome to the Search API!",
        "docs": "/docs",
        "endpoints": {
            "tasks": "/tasks/{task_id}",
            "search": "/search"
        }
    }

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    """Get a task by ID using path parameter"""
    return {
        "task_id": task_id,
        "task_name": f"Task #{task_id}",
        "status": "pending"
    }

@app.get("/search")
def search(q: str, limit: int = 10):
    """Search endpoint with query parameters"""
    return {
        "query": q,
        "limit": limit,
        "results": [f"Result 1 for '{q}' with limit {limit}", f"Result 2 for '{q}' with limit {limit}"]
    }
