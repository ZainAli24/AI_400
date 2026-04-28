from fastapi import FastAPI, Depends


# def greet():
#     print("greet func call first -----------> 1..------------------")
#     return {"message": "Hello, World!", "name": "Sameer"}


app = FastAPI()



# @app.get("/hello")
# def hello(res: dict = Depends(greet)):
#     # res = greet()
#     print("hello func call second -------------2. -----------")
#     return {"message": "Hello", "name": res["name"]}



# ----------

# In fastApi, Depends is used for dependency injection.
# dependencies means any function or class or packages that provides some resources/data/services.
# dependency injection means injecting those dependencies into your functions or classes where you need them.

# ----------


# Example of dependency injection with file handling (open and close file):

import tempfile
import os


def get_file_open_close():

    fd, path = tempfile.mkstemp()
    file = os.fdopen(fd, "w")

    try:
        yield file

    finally:
        file.close()
        os.unlink(path)



@app.post("/depends")
def temp_file(temp = Depends(get_file_open_close)):
    temp.write("Data Zain ... descriptive ...")
    return {"sucess": "processed"}


# ----------


# understanding Environment Variables:

from dotenv import load_dotenv
import os

load_dotenv()


def env_variables():
    print("...................... First execute this env 1 .............................")
    return {"message": "Here is Environment Variables:", "Environment_Variable": os.getenv("ZAIN_API_KEY")}



@app.get("/env")
def env(env_var= Depends(env_variables)):
    print("......................Second execute env 2 ....................")
    return {"message": "All Goods! Env Variables is here", "API_KEY": env_var["Environment_Variable"]}


# --------------------------------


