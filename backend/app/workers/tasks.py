import sys
sys.path.insert(0, "/content/hvac-bom-app/backend")

from app.services.pdf_store import read_pdf, delete_pdf
from app.services.job_store import update_job_status, update_job_page_count, store_result
from app.services.pdf_parser import combine_page_content

def process_pdf_job(job_id: str):
    try:
        update_job_status(job_id, "processing")

        pdf_bytes = read_pdf(job_id)
        if not pdf_bytes:
            update_job_status(job_id, "failed:pdf_not_found")
            return

        pages = combine_page_content(pdf_bytes)
        update_job_page_count(job_id, len(pages))

        store_result(job_id, {
            "pages": len(pages),
            "items": [],
            "issues": []
        })

        update_job_status(job_id, "complete")

    except Exception as e:
        update_job_status(job_id, f"failed:{str(e)}")
    finally:
        delete_pdf(job_id)
