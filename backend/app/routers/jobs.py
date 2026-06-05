from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.services.job_store import get_job
from app.services.excel_exporter import build_excel
import redis
import json
import io
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

@router.get("/jobs/{job_id}/download")
def download_excel(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.get("status") != "complete":
        raise HTTPException(status_code=202, detail="Job not complete yet")
    result_raw = r.get(f"result:{job_id}")
    if not result_raw:
        raise HTTPException(status_code=404, detail="Result not found")
    result = json.loads(result_raw)
    filename = job.get("filename", "bom_export")
    excel_bytes = build_excel(result, filename)
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=bom_{job_id}.xlsx"}
    )
