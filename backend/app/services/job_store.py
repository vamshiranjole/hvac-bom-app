import json
import redis
from datetime import datetime
from app.config import settings

r = redis.from_url(settings.REDIS_URL, decode_responses=True)

def create_job(job_id: str, filename: str, document_hash: str):
    job = {
        "job_id": job_id,
        "status": "queued",
        "filename": filename,
        "document_hash": document_hash,
        "created_at": datetime.utcnow().isoformat()
    }
    r.hset(f"job:{job_id}", mapping=job)
    r.expire(f"job:{job_id}", settings.RESULT_TTL_SECONDS)
    return job

def get_job(job_id: str):
    job = r.hgetall(f"job:{job_id}")
    return job if job else None

def update_job_status(job_id: str, new_status: str):
    r.hset(f"job:{job_id}", "status", new_status)
