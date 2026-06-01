import time
from app.services.pdf_store import read_pdf, delete_pdf
from app.services.job_store import update_job_status

def process_pdf_job(job_id: str):
    try:
        update_job_status(job_id, "processing")

        pdf_bytes = read_pdf(job_id)
        if not pdf_bytes:
            update_job_status(job_id, "failed:pdf_not_found")
            return

        time.sleep(3)

        update_job_status(job_id, "complete")

    except Exception as e:
        update_job_status(job_id, f"failed:{str(e)}")
    finally:
        delete_pdf(job_id)
