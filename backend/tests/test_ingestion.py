import io
import pytest
from fastapi.testclient import TestClient
from app.config import settings
from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def isolated_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "upload_dir", tmp_path / "uploads")

def test_csv_upload_and_metadata():
    response = client.post("/api/v1/uploads",
        files={"file": ("sales.csv", io.BytesIO(b"product,revenue\nA,100\nB,200\n"), "text/csv")})
    assert response.status_code == 201
    record = response.json()
    assert record["content_metadata"]["row_count"] == 2
    assert record["content_metadata"]["column_count"] == 2
    assert client.get(f"/api/v1/uploads/{record['file_id']}").status_code == 200

def test_reject_unsupported_extension():
    response = client.post("/api/v1/uploads",
        files={"file": ("notes.txt", io.BytesIO(b"hello"), "text/plain")})
    assert response.status_code == 400

def test_reject_fake_pdf():
    response = client.post("/api/v1/uploads",
        files={"file": ("fake.pdf", io.BytesIO(b"not a pdf"), "application/pdf")})
    assert response.status_code == 400

def test_list_and_delete():
    response = client.post("/api/v1/uploads",
        files={"file": ("tiny.csv", io.BytesIO(b"x\n1\n"), "text/csv")})
    file_id = response.json()["file_id"]
    assert client.get("/api/v1/uploads").json()["count"] == 1
    assert client.delete(f"/api/v1/uploads/{file_id}").status_code == 204
    assert client.get(f"/api/v1/uploads/{file_id}").status_code == 404
