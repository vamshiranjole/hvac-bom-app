import fitz
import pdfplumber
import io

def extract_text(pdf_bytes: bytes) -> list:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        pages.append({"page_number": i + 1, "text": text})
    return pages

def extract_tables(pdf_bytes: bytes) -> list:
    pages = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            clean_tables = []
            for table in tables:
                rows = [[cell or "" for cell in row] for row in table]
                clean_tables.append(rows)
            pages.append({"page_number": i + 1, "tables": clean_tables})
    return pages

def combine_page_content(pdf_bytes: bytes) -> list:
    text_pages = extract_text(pdf_bytes)
    table_pages = extract_tables(pdf_bytes)

    combined = []
    for text_page, table_page in zip(text_pages, table_pages):
        page_number = text_page["page_number"]
        tables = table_page["tables"]

        if tables:
            lines = []
            for table in tables:
                for row in table:
                    line = " | ".join(row).strip(" |")
                    if line:
                        lines.append(line)
            content = "\n".join(lines)
            table_count = len(tables)
        else:
            content = text_page["text"]
            table_count = 0

        combined.append({
            "page_number": page_number,
            "content": content,
            "table_count": table_count
        })

    return combined
