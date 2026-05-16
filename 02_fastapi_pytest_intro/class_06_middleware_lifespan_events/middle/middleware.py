from fastapi import FastAPI, Request, Response
import json


app = FastAPI()


@app.middleware("http")
async def request_logs(request: Request, call_next):
    print(f"\n\n ----> Request Innn A-1 {request.method} {request.url.path}")
    response = await call_next(request)
    print(f"\n\n ----> Response OUT A-1 {response.status_code}")
    response.headers["X-My-Header"] = "Zain"
    return response



@app.middleware("http")
async def request_logs_2(request: Request, call_next):
    print(f"\n\n ----> Request Innn A-2 {request.method} {request.url.path}")
    body = b""
    response = await call_next(request)
    async for chucks in response.body_iterator:
        body += chucks

    body_str = body.decode()
    content_type = response.headers.get("content-type", "")

    print(f"\n\n ----> Response OUT A-2 {response.status_code} {body_str}")

    if "application/json" in content_type:
        body_dict = json.loads(body_str)
        body_dict.update({"name": "Zain"})
        new_body = json.dumps(body_dict).encode()
        headers = dict(response.headers)
        headers.pop("content-length", None)
        return Response(
            content=new_body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type
        )

    return Response(
        content=body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type
    )


@app.get("/hello")
def greet():
    return {"message": "<----- ALL GOOD ----->"}
