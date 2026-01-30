from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "http://localhost:8000",
    "http://localhost:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"],
)


@app.middleware("http")
async def first_func(request: Request, call_next):
    print("\n [+] [--A-- ] Before request processing: ", request.method, request.url.path)
    response = await call_next(request)
    print("\n [+] [ --A-- ] After request processing: ", response.status_code)
    return response



@app.middleware("http")
async def Bhi(request: Request, call_next):
    print("\n [-] [--B--] Before request processing: ", request.method, request.url.path)
    response = await call_next(request)  # fastapi do this: call_next(first_func).
    print("\n [-] [ --B-- ] After request processing: ", response.status_code)
    return response


@app.middleware("http")
async def timer_middleware(request: Request, call_next):
    import time

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    # Exect human readable format
    process_time = f"{process_time:.4f} sec"
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/hello")
def hello():
    return {"message": "Hello World"}
