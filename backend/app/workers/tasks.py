import sys
sys.path.insert(0, "/app")

from app.services.pdf_store import read_pdf, delete_pdf
from app.services.job_store import update_job_status, update_job_page_count, store_result
from app.services.pdf_parser import combine_page_content
from app.services.ai_extractor import extract_equipment
from app.services.rules_engine import run_r_rules, run_h_rules
from app.services.bom_builder import build_bom

MAX_PAGES_TO_PROCESS = 5

def process_pdf_job(job_id: str):
    try:
        update_job_status(job_id, "processing")

        pdf_bytes = read_pdf(job_id)
        if not pdf_bytes:
            update_job_status(job_id, "failed:pdf_not_found")
            return

        pages = combine_page_content(pdf_bytes)
        update_job_page_count(job_id, len(pages))

        all_items = []
        processed = 0
        for page in pages:
            if processed >= MAX_PAGES_TO_PROCESS:
                break
            content = page["content"].strip()
            if len(content) < 50:
                continue
            items = extract_equipment(content, page["page_number"])
            all_items += items
            processed += 1

        r_issues = run_r_rules(all_items)
        h_issues = run_h_rules(all_items)
        bom = build_bom(all_items, r_issues + h_issues)

        result = {
            "bom": bom,
            "issues": r_issues + h_issues,
            "page_count": len(pages),
            "item_count": len(bom)
        }

        store_result(job_id, result)
        update_job_status(job_id, "complete")

    except Exception as e:
        update_job_status(job_id, f"failed:{str(e)}")
    finally:
        delete_pdf(job_id)
