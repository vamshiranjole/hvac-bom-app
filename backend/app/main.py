import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(title="HVAC BOM Extractor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    pdf_bytes = await file.read()

    if len(pdf_bytes) > settings.MAX_PDF_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File is too large. Maximum size is 25MB."
        )

    if not pdf_bytes.startswith(b'%PDF'):
        raise HTTPException(
            status_code=415,
            detail="This file does not appear to be a PDF."
        )

    job_id = str(uuid.uuid4())

    return {
        "job_id": job_id,
        "status": "queued",
        "filename": file.filename
    }
