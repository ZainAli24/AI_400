# from fastapi import FastAPI
# from dotenv import load_dotenv
# import os

# load_dotenv(".env.local")

# GEMINI_API_KEY= os.getenv("GEMINI_API_KEY")


# app = FastAPI()



# @app.get("/key")
# def get_key():
#     return {"Gemini key": GEMINI_API_KEY}



#-------------------------------------------------------


# 1.pydantic-settings — Recommended Tarika env ko handle aur load karne ka:

# from fastapi import FastAPI
# from pydantic_settings import BaseSettings

# class Settings(BaseSettings):
#     GEMINI_API_KEY: str
#     MAX_CONNECTIONS: int = 5
#     DEBUG: bool = False

#     class Config:
#         env_file = ".env.local"


# settings = Settings()


# app = FastAPI()


# @app.get("/key")
# def get_key():
#     return {"Gemini key": settings.GEMINI_API_KEY, "Max Connections": settings.MAX_CONNECTIONS, "debug": settings.DEBUG}



# ---------------------------------------------------------


# 2. @lru_cache + Depends() — Recommended Pattern:

from fastapi import FastAPI, Depends
from pydantic_settings import BaseSettings
from functools import lru_cache


app =  FastAPI()

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    MAX_CONNECTIONS: int = 5
    DEBUG: bool = False 

    class Config:
        env_file = ".env.local"



@lru_cache
def get_settings()-> Settings:
    return Settings()


@app.get("/settings")
def get_config(settings: Settings = Depends(get_settings)):
    return {"Gemini Key": settings.GEMINI_API_KEY, "Max Connections": settings.MAX_CONNECTIONS, "Debug mode": settings.DEBUG}



# for test: Never use real Settings (ENV : Db keys , API KEYS) ifor testing purposes, instead use fake settings for testing purposes.

@lru_cache
def fake_settings() -> Settings:
    return Settings(
        GEMINI_API_KEY="Aliza-23-42422e203f434d98j__fake_key_for_testing_purposes",
        MAX_CONNECTIONS=50,
        DEBUG=True
    )


app.dependency_overrides[get_settings] = fake_settings




