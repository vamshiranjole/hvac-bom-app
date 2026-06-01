import uuid
import hashlib
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.services.pdf_store import store_pdf
from app.services.job_store import create_job, get_job
from app.routers import jobs
import redis

app = FastAPI(title="HVAC BOM Extractor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)

r = redis.from_url(settings.REDIS_URL, decode_responses=True)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    pdf_bytes = await file.read()

    if len(pdf_bytes) > settings.MAX_PDF_BYTES:
        raise HTTPException(status_code=413, detail="File is too large. Maximum size is 25MB.")

    if not pdf_bytes.startswith(b'%PDF'):
        raise HTTPException(status_code=415, detail="This file does not appear to be a PDF.")

    document_hash = "sha256:" + hashlib.sha256(pdf_bytes).hexdigest()

    cached_job_id = r.get(f"hash:{document_hash}")
    if cached_job_id:
        return {"job_id": cached_job_id, "status": "cached", "filename": file.filename}

    job_id = str(uuid.uuid4())
    store_pdf(job_id, pdf_bytes)
    create_job(job_id, file.filename, document_hash)
    r.setex(f"hash:{document_hash}", settings.RESULT_TTL_SECONDS, job_id)

    return {"job_id": job_id, "status": "queued", "filename": file.filename, "document_hash": document_hash}
