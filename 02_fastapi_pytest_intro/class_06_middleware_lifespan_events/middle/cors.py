import time
import logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


origins = [
    "http://localhost:3000",      # React dev server
    "http://localhost:8000",      # Fastapi dev server
    "https://myapp.com",          # Production frontend
]


# Cors middleware:
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_headers=["Authorization", "Content-Type"],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    expose_headers=["X-Process-Time"],
)


# Request Time calculator Middleware:
@app.middleware("http")
async def calulate_req_time(request: Request, call_next)-> Response:
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{(time.perf_counter() - start):.4f}"
    return response


# Request Logging Middleware:
@app.middleware("http")
async def log_request(request: Request, call_next) -> Response:
    logger.info(f" --> {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f" <-- {response.headers["X-Process-Time"]} time,  {response.status_code}")
    return response


@app.get("/middle")
def middle_info():
    return {"message": "Hello Cors Middleware & Custom Middleware !!!"}


