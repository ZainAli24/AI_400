from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(" [*] --------> Starting up...")
    app.state.settings = {"app_name": "FastAPI with Lifespan Events", "version": "1.0.0"}
    yield
    print(" [*] ---------> Shutting down...")


app = FastAPI(lifespan=lifespan)


@app.get("/data")
def info():
    return {"app_name": app.state.settings["app_name"], "version": app.state.settings["version"]}

    


@app.get("/goodbye")
def goodbye():
    return {"message": "Goodbye World"}



