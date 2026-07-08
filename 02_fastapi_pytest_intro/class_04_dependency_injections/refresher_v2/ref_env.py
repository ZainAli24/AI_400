from fastapi import FastAPI, Depends
from dotenv import load_dotenv
import os

load_dotenv()


app = FastAPI()


def config():
    return {"db-status": "success", "gemini-key": os.getenv("GEMINI_API_KEY")}


@app.get("/env")
def secure(config: dict = Depends(config)):
    return {"config_states": config}




# Second Recommended way:
from pydantic_settings import BaseSettings
from fastapi import FastAPI, Depends
from functools import lru_cache


app = FastAPI()


class Settings(BaseSettings):
    GEMINI_API_KEY: str 
    is_verifiied: bool = False
    max_connection: int = 14

    class Config:
        env_file= ".env"
        extra="ignore"


@lru_cache
def get_setting():
    return Settings()




@app.get("/new")
def pydantic_secure(setting: Settings = Depends(get_setting)):
    return {"gemini_key": setting.GEMINI_API_KEY, "is_verified": setting.is_verifiied, "max_conn": setting.max_connection}




# -------
