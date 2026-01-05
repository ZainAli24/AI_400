from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, EmailStr
from app.tasks.background_tasks import send_email_task, process_data_task

router = APIRouter()


class EmailRequest(BaseModel):
    email: EmailStr
    message: str


class DataRequest(BaseModel):
    data: dict


@router.post("/send-email")
def send_email(request: EmailRequest, background_tasks: BackgroundTasks):
    """Send email in background using FastAPI BackgroundTasks"""
    background_tasks.add_task(send_email_task, request.email, request.message)
    return {
        "message": "Email will be sent in the background",
        "email": request.email,
    }


@router.post("/process-data")
def process_data(request: DataRequest, background_tasks: BackgroundTasks):
    """Process data in background using FastAPI BackgroundTasks"""
    background_tasks.add_task(process_data_task, request.data)
    return {"message": "Data processing started in the background"}
