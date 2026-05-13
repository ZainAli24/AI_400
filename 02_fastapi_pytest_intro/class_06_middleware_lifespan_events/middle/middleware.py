from fastapi import FastAPI, Request, Response
import json


app = FastAPI()


@app.middleware("http")
async def request_logs(request: Request, call_next):
    print(f"\n\n ----> Request Innn A-1{request.method} {request.url.path}")
    body = b""
    response = await call_next(request)
    async for chucks in response.body_iterator:
        body += chucks

    print(f"\n\n ----> Response OUT A-1 {response.status_code} {body.decode()}")
    # update header:
    response.headers["X-My-Header"] = "Zain"
    return Response(
        content=body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type
    )



@app.middleware("http")
async def request_logs_2(request: Request, call_next):
    print(f"\n\n ----> Request Innn A-2 {request.method} {request.url.path}")
    body = b""
    response: Response = await call_next(request)
    async for chucks in response.body_iterator:
        body += chucks
    
    print(f"\n\n ----> Response OUT A-2 {response.status_code} {body.decode()}")
    # byte to str:
    body_str = body.decode()
    # str to dict
    body_dict = json.loads(body_str)
    # update dict:
    body_dict.update({"name": "Zain"})
    # convrt dict to again byte:
    new_body = json.dumps(body_dict).encode()

    header = dict(response.headers)
    header.pop("content-length", None) # purana size hatao, Starlette naya calculate karega


    return Response(
    content=new_body,
    status_code=response.status_code,
    headers=header,
    media_type=response.media_type
    )


@app.get("/hello")
def greet():
    return {"message": "<----- ALL GOOD ----->"}


