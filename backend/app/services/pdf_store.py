import hashlib
import redis
from app.config import settings

r = redis.from_url(settings.REDIS_URL, decode_responses=False)

def store_pdf(job_id: str, pdf_bytes: bytes) -> str:
    document_hash = "sha256:" + hashlib.sha256(pdf_bytes).hexdigest()
    r.setex(f"pdf:{job_id}", settings.PDF_TTL_SECONDS, pdf_bytes)
    return document_hash

def read_pdf(job_id: str) -> bytes:
    return r.get(f"pdf:{job_id}")

def delete_pdf(job_id: str):
    r.delete(f"pdf:{job_id}")
