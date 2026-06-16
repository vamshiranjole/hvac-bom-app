import sys
sys.path.insert(0, "/content/hvac-bom-app/backend")

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

with patch("redis.from_url", return_value=MagicMock()), \
     patch("rq.Queue", return_value=MagicMock()):
    from app.main import app

client = TestClient(app)
API_KEY = "hvac2024securekey123456789abc"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_upload_no_key():
    response = client.post("/upload", files={"file": ("test.pdf", b"%PDF-fake", "application/pdf")})
    assert response.status_code in [401, 403, 422]

def test_upload_fake_pdf():
    response = client.post(
        "/upload",
        headers={"x-api-key": API_KEY},
        files={"file": ("fake.pdf", b"this is not a pdf", "application/pdf")}
    )
    assert response.status_code == 415

def test_upload_too_large():
    big_file = b"%PDF" + b"x" * (26 * 1024 * 1024)
    response = client.post(
        "/upload",
        headers={"x-api-key": API_KEY},
        files={"file": ("big.pdf", big_file, "application/pdf")}
    )
    assert response.status_code == 413

def test_get_invalid_job():
    response = client.get("/jobs/invalid-id-that-does-not-exist")
    assert response.status_code in [200, 404]
