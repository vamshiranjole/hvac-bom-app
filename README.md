# HVAC BOM Intelligence

An AI-powered web app that extracts a Bill of Materials (BOM) from HVAC equipment schedule PDFs, flags issues, exports to Excel, compares revisions, and pushes to Salesforce.

Built for mechanical contracting estimators — not developers.

---

## Who it is for

Estimators at mechanical contracting companies who receive HVAC equipment schedules as PDFs and need to build a BOM quickly, accurately, and without re-keying data.

---

## How to set up locally (Google Colab)

1. Go to colab.research.google.com and open a new notebook
2. Clone the repository:
   git clone https://github.com/vamshiranjole/hvac-bom-app.git
3. Install dependencies:
   pip install -r backend/requirements.txt
4. Create a .env file in backend/ with these values:
   OPENAI_API_KEY=your_groq_or_openai_key
   OPENAI_MODEL=llama-3.3-70b-versatile
   REDIS_URL=your_redis_cloud_url
   API_KEY=your_chosen_api_key
   MAX_PDF_BYTES=26214400
   PDF_TTL_SECONDS=1800
   RESULT_TTL_SECONDS=604800
   SF_INSTANCE_URL=
   SF_USERNAME=
   SF_PASSWORD=
5. Run the backend in Colab:
   cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
6. Open frontend/index.html directly in your browser

---

## How to deploy to Railway

1. Go to railway.app and create a new project from your GitHub repository
2. Set the root directory to backend/
3. Add a Redis plugin from the Railway dashboard
4. Add all environment variables in the Railway Variables tab
5. Railway deploys automatically on every GitHub push
6. Your live URL will be shown in the Deployments tab

---

## How to test with a sample PDF

1. Open the web app in your browser
2. Drag an HVAC equipment schedule PDF onto the upload zone
3. Enter a project name and click Extract BOM
4. Watch the progress bar — results appear within 60 seconds
5. Review the BOM table, download the Excel file, or push to Salesforce

---

## API endpoints reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /health | None | Server health check |
| POST | /upload | x-api-key header | Upload a PDF and start extraction |
| GET | /jobs/{job_id} | x-api-key header | Get job status |
| GET | /jobs/{job_id}/result | x-api-key header | Get full BOM result |
| GET | /jobs/{job_id}/download | x-api-key header | Download Excel file |
| POST | /compare | x-api-key header | Compare two PDF versions |
| POST | /salesforce/push | x-api-key header | Push BOM to Salesforce |

---

## Running the test suite

cd backend
OPENAI_API_KEY=test REDIS_URL=redis://localhost:6379 API_KEY=testkey python -m pytest tests/ -v

All 46 tests pass. No live API calls are made during testing.

---

## Known limitations

- Searchable PDFs only: works best on clean, software-generated equipment schedules. Scanned PDFs are not supported in this version.
- AI extraction accuracy varies: results depend on document format and layout quality. Always review flagged items before use.
- Issue warnings are advisory only: a licensed engineer makes all final engineering decisions. This tool does not replace professional judgment.
- No user accounts: one shared API key for all users. There is no per-user authentication or access control.
- Revision comparison requires consistent tagging: equipment tags must be consistent between document versions for comparison to work correctly.
- Salesforce integration requires manual credential entry: Salesforce username, password, and security token are entered per session and are not stored.
