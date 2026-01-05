from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# In-memory job storage (use Redis or DB in production)
jobs_db = {}
job_id_counter = 1


class JobCreate(BaseModel):
    task_type: str
    parameters: Optional[dict] = None


class JobStatus(BaseModel):
    job_id: int
    task_type: str
    status: str
    result: Optional[dict] = None


@router.post("/", response_model=JobStatus, status_code=201)
def create_job(job: JobCreate):
    """Create a new job"""
    global job_id_counter
    job_status = JobStatus(
        job_id=job_id_counter,
        task_type=job.task_type,
        status="pending",
    )
    jobs_db[job_id_counter] = job_status
    job_id_counter += 1

    # In production, trigger actual background task here
    # For Celery: send_email_celery.delay(...)

    return job_status


@router.get("/{job_id}", response_model=JobStatus)
def get_job_status(job_id: int):
    """Get job status"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs_db[job_id]


@router.get("/")
def list_jobs(skip: int = 0, limit: int = 10):
    """List all jobs"""
    jobs = list(jobs_db.values())
    return jobs[skip : skip + limit]
