from fastapi import APIRouter, HTTPException
from app.services.job_store import get_job
import redis
import json
from app.config import settings

router = APIRouter()

r = redis.from_url(settings.REDIS_URL, decode_responses=True)

@router.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/jobs/{job_id}/result")
def get_job_result(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.get("status") != "complete":
        raise HTTPException(status_code=202, detail=f"Job status: {job.get('status')}")
    result = r.get(f"result:{job_id}")
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return json.loads(result)
