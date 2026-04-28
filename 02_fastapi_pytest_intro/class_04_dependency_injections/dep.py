from fastapi import FastAPI, Depends, Request
from datetime import datetime
import tempfile
import os
from functools import lru_cache

app = FastAPI()

# Check which dependency is being called first
def get_app_data():
    print("\n get_app_data called  --> First")
    return {"app_name": "Task_API", "storage": "In-file"}

@app.get("/hello")
def greet(app_data: dict = Depends(get_app_data)):
    print("\n greet called --> Second")
    return {"message": "HELLO World!", "app_name": app_data["app_name"]}


# Yield dependency
def get_temp_file():
    fd, path = tempfile.mkstemp()
    file = os.fdopen(fd, "w")
    try:
        yield file
    finally:
        print("-------- UNlink File ---------")
        file.close()
        os.unlink(path)

@app.get("/fileworking")
def do_work_in_file(file=Depends(get_temp_file)):
    file.write("MY NAME IS ZAIN")
    print("----- STATUS PROCESSED -------")
    return {"Status": "Processed"}


# lru_cache
@lru_cache
def get_data_from_db():
    print("-------- call DataBase to get data ----------")
    return {
        "app_name": "Task_API",
        "debug": True
    }

@app.get("/data")
def get_data(data: dict = Depends(get_data_from_db)):
    app_name = data["app_name"]
    return f"APP_NAME IS : {app_name}"


# Request Logger
def get_logs_of_requests(request: Request):
    start = datetime.now()
    method = request.method
    path = request.url.path

    print(f"[{start}] {method} {path} - started")

    yield {"method": method, "path": path, "start": start}

    end = datetime.now()
    duration = (end - start).total_seconds()

    print(f"[{end}] {method} {path} - Duration - {duration:.3f}s")

@app.get("/logs")
def get_request_logs(logs: dict = Depends(get_logs_of_requests)):
    return {"log_path": logs["path"]}

@app.post("/loger")
def post_request_logs(log: dict = Depends(get_logs_of_requests)):
    return {"id": 1, "logged_method": log["method"]}


# 1. Dependencies Chain

# a) City greeting
def get_city():
    return "Islamabad"

def greet_with_city(city: str = Depends(get_city)):
    return f"Wellcome from {city}"

@app.get("/greet")
def greet_user(greet: dict = Depends(greet_with_city)):
    return {"message": greet}


# b) User details
def get_username():
    return "Zain Ali"

def create_user_details(username: str = Depends(get_username)):
    return {
        "username": username,
        "user_email": f"{username}@gmail.com",
        "role": "admin"
    }

@app.get("/userdetails")
def user_info(user_details: dict = Depends(create_user_details)):
    return {
        "profile": user_details
    }


# 2) Dependency Override
def connect_database():
    return {"db": "sqlite:///real.db", "connected": True}

@app.get("/db")
def connect_db(status: dict = Depends(connect_database)):
    return {"status": status}


# 3) Class Based Dependency
def get_urler():
    return "sqlite:///tasks.db"

class TaskService:
    def __init__(self, db_url: str = Depends(get_urler)):
        self.db_url = db_url

    def list(self):
        return [{"id": 1, "title": "HOMEWORK"}, {"id": 2, "title": "Study"}]

    def create(self, title):
        return {"id": 3, "title": title, "db": self.db_url}

@app.get("/info")
def get_info(get_class: TaskService = Depends(TaskService)):
    return get_class.list()

@app.post("/do")
def create_do(create_class: TaskService = Depends(TaskService)):
    return create_class.create("Cricket")
