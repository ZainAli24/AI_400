from fastapi import FastAPI, Depends, Request
import os, tempfile
from functools import lru_cache
import time
from datetime import datetime

app = FastAPI()


def get_config():
    print("get config dependency - 1")
    return {"app_name": "Task Api", "app_details": "Manage your tasks here!"}


@app.get("/hello")
def hello(config: dict = Depends(get_config)):
    print("hello from App - 2")
    # config = get_config()
    return {"message": f"Hello {config["app_name"]}", "configuratoin": config}



def get_tem_file():
    fd, path = tempfile.mkstemp()

    file = os.fdopen(fd=fd, mode="w")

    try:
        yield file
    finally:
        print("\n -- Hello from finally block of dependency func!")
        file.close()
        os.unlink(path=path)



@app.post("/file")
def create_file(temp = Depends(get_tem_file)):
    temp.write("data")
    print("\n -- Hello from Business logic !")
    return {"status": "Success", "message": "Temp file created & closed successfully!"}




# @lru_cache:
@lru_cache
def call_db():
    print("Calling db to fetch data ....")
    time.sleep(10)
    return {"user_name": "Zain Ali", "status": "success"}


@app.get("/db")
def get_data(db_res: dict = Depends(call_db)):
    return db_res



# Request logger complete example:
def request_logger(request: Request):
    start = datetime.now()
    method = request.method
    path = request.url.path

    print(f"Request {path}: {method} . starting time: {start}")
    yield {"start": start, "method": method, "path": path}

    end = datetime.now()
    duration =  f"{(end - start).total_seconds():.3f}"   

    print(f"[Total Time of request]: {duration}, {method}")




@app.get("/log")
def log_req(log: dict = Depends(request_logger)):
    time.sleep(5)
    return {"logggin_INFO": log["start"], "method": log["method"]}



@app.get("/tasks")
def list_tasks(log: dict = Depends(request_logger)):
    return {"tasks": [], "logged_path": log["path"]}


@app.post("/tasks")
def create_task(log: dict = Depends(request_logger)):
    return {"id": 1, "logged_method": log["method"]}






# Hand-on:
class TaskCounter():
    def __init__(self):
        self.count = 0

    def incrementor(self):
        self.count += 1
        return self.count
    

counter = TaskCounter()

def get_count():
    count = counter.incrementor()
    return count



@app.get("/count")
def req_count(count= Depends(get_count)):
    return {f"[INFO]-->[TOTAL REQUEST]: {count}"}




# dependancy chain:
def get_username() -> str:
    print("USERNAME CALL HOWA")
    username : str = "ZainAli"
    return username


def get_email(data: str = Depends(get_username)):
    user = data.lower()
    email = f"{user}@gmail.com"
    return email



@app.get("/user")
def user_info(username: str = Depends(get_username), email: str = Depends(get_email)):
    return {"name": username, "email": email}





# Dependency Ovveride:
def connect_db():
    print("Connecting DB ......")
    time.sleep(5)
    return {"message": "Connected DB successfully!", "db_status": "OK"}


@app.get("/connect")
def start_db(db: dict = Depends(connect_db)):
    return {"DB_LOGS": db}




# class
def url():
    return "https://localhost:8050/todo"


class TaskFire:
    def __init__(self, urler: str = Depends(url)):
        self.urler = urler

    def get_list(self):
        return {"List Info": [
            {"id":1, "title": "Gym"},
            {"id":2, "title": "Code"},
            {"id":3, "title": "Football"}
        ],
        "URL_INFO": f"Tasks available at {self.urler}"
        }
    

    def create_task(self, title: str):
        return {"id": 9843, "title": title}
    



@app.get("/list")
def get_list(obj: TaskFire = Depends(TaskFire)):
    return obj.get_list()

@app.get("/create")
def create_task(obj: TaskFire = Depends(TaskFire)):
    return obj.create_task(title="Cricket")

