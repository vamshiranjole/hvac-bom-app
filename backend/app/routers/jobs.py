from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.job_store import get_job
from app.services.excel_exporter import build_excel
import redis
import json
import io
from app.config import settings

router = APIRouter()

r = redis.from_url(settings.REDIS_URL, decode_responses=True)

class SalesforcePushRequest(BaseModel):
    job_id: str
    project_name: str
    sf_username: str
    sf_password: str
    sf_token: str
    sf_instance_url: str

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

@router.post("/salesforce/push")
def push_to_salesforce(req: SalesforcePushRequest):
    from app.services.salesforce_service import push_bom_to_salesforce
    job = get_job(req.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    result_raw = r.get(f"result:{req.job_id}")
    if not result_raw:
        raise HTTPException(status_code=404, detail="Result not found")
    result = json.loads(result_raw)
    try:
        sf_result = push_bom_to_salesforce(
            job_id=req.job_id,
            project_name=req.project_name,
            bom=result.get("bom", []),
            sf_username=req.sf_username,
            sf_password=req.sf_password,
            sf_token=req.sf_token,
            sf_instance_url=req.sf_instance_url
        )
        return sf_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
