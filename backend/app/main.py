import uuid
import hashlib
import redis
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from rq import Queue
from app.config import settings
from app.services.pdf_store import store_pdf
from app.services.job_store import create_job, get_job
from app.workers.tasks import process_pdf_job
from app.routers import jobs
from app.services.pdf_parser import combine_page_content
from app.services.ai_extractor import extract_equipment
from app.services.rules_engine import run_r_rules, run_h_rules
from app.services.bom_builder import build_bom
from app.services.revision_compare import compare_boms

app = FastAPI(title="HVAC BOM Extractor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)

redis_conn = redis.from_url(settings.REDIS_URL)
r = redis.from_url(settings.REDIS_URL, decode_responses=True)
q = Queue(connection=redis_conn)

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

    q.enqueue(process_pdf_job, job_id)

    return {"job_id": job_id, "status": "queued", "filename": file.filename, "document_hash": document_hash}

@app.post("/compare")
async def compare_pdfs(file_old: UploadFile = File(...), file_new: UploadFile = File(...)):
    old_bytes = await file_old.read()
    new_bytes = await file_new.read()

    def process(pdf_bytes):
        pages = combine_page_content(pdf_bytes)
        all_items = []
        for page in pages[:3]:
            content = page["content"].strip()
            if len(content) < 50:
                continue
            items = extract_equipment(content, page["page_number"])
            all_items += items
        r_issues = run_r_rules(all_items)
        h_issues = run_h_rules(all_items)
        bom = build_bom(all_items, r_issues + h_issues)
        return bom

    old_bom = process(old_bytes)
    new_bom = process(new_bytes)
    changes = compare_boms(old_bom, new_bom)

    return {"changes": changes, "total_changes": len(changes)}
