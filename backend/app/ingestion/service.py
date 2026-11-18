import json
import re
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

import fitz
import pandas as pd
from fastapi import UploadFile

from app.config import settings

ALLOWED = {".csv", ".xlsx", ".xls", ".pdf"}

class IngestionError(ValueError):
    pass

def safe_name(filename: str) -> str:
    name = Path(filename or "upload").name
    return re.sub(r"[^A-Za-z0-9._ -]", "_", name).strip(" .")[:150] or "upload"

def json_value(value):
    if hasattr(value, "item"):
        value = value.item()
    if pd.isna(value):
        return None
    if isinstance(value, (datetime,)):
        return value.isoformat()
    return value

def parse_table(path: Path, ext: str):
    try:
        if ext == ".csv":
            try:
                df = pd.read_csv(path, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(path, encoding="cp1252")
            sheets = None
        else:
            book = pd.ExcelFile(path)
            sheets = book.sheet_names
            df = pd.read_excel(path, sheet_name=sheets[0])
    except Exception as exc:
        raise IngestionError(f"Could not parse tabular file: {exc}") from exc
    if len(df.columns) == 0:
        raise IngestionError("The file contains no columns.")
    columns = []
    for name in df.columns:
        s = df[name]
        item = {"name": str(name), "dtype": str(s.dtype),
                "null_count": int(s.isna().sum()), "unique_count": int(s.nunique(dropna=True))}
        if pd.api.types.is_numeric_dtype(s):
            item["statistics"] = {"min": json_value(s.min()), "max": json_value(s.max()),
                                  "mean": json_value(s.mean())}
        columns.append(item)
    preview = [{str(k): json_value(v) for k, v in row.items()}
               for row in df.head(10).to_dict(orient="records")]
    metadata = {"row_count": int(len(df)), "column_count": int(len(df.columns)),
                "columns": columns, "preview": preview, "sheet_names": sheets,
                "analysis_sheet": sheets[0] if sheets else None}
    text = (f"Dataset has {len(df)} rows and {len(df.columns)} columns.\n"
            + "Columns: " + ", ".join(f"{c['name']} ({c['dtype']})" for c in columns)
            + "\nPreview:\n" + df.head(20).to_csv(index=False))
    return metadata, text

def parse_pdf(path: Path):
    try:
        with fitz.open(path) as pdf:
            if pdf.is_encrypted:
                raise IngestionError("Password-protected PDFs are not supported.")
            pages = [page.get_text("text") for page in pdf]
    except IngestionError:
        raise
    except Exception as exc:
        raise IngestionError(f"Could not parse PDF: {exc}") from exc
    text = "\n\n".join(f"[Page {i+1}]\n{p.strip()}" for i, p in enumerate(pages) if p.strip())
    if not text.strip():
        raise IngestionError("No selectable text found. Scanned PDFs need OCR, not included in this phase.")
    return {"page_count": len(pages), "pages_with_text": sum(bool(p.strip()) for p in pages),
            "text_character_count": len(text)}, text

async def ingest_upload(upload: UploadFile):
    filename = safe_name(upload.filename or "upload")
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED:
        raise IngestionError("Unsupported file. Allowed formats: CSV, XLSX, XLS, PDF.")
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    file_id = str(uuid.uuid4())
    folder = settings.upload_dir / file_id
    folder.mkdir()
    path = folder / f"original{ext}"
    total = 0
    try:
        with path.open("wb") as out:
            while chunk := await upload.read(1024 * 1024):
                total += len(chunk)
                if total > settings.max_upload_size_mb * 1024 * 1024:
                    raise IngestionError(f"File exceeds {settings.max_upload_size_mb} MB.")
                out.write(chunk)
        if total == 0:
            raise IngestionError("The uploaded file is empty.")
        signature = path.read_bytes()[:8]
        if ext == ".pdf" and not signature.startswith(b"%PDF-"):
            raise IngestionError("File content is not a valid PDF.")
        if ext == ".xlsx" and not signature.startswith(b"PK"):
            raise IngestionError("File content is not a valid XLSX workbook.")
        if ext == ".xls" and not signature.startswith(b"\xD0\xCF\x11\xE0"):
            raise IngestionError("File content is not a valid XLS workbook.")
        if ext == ".pdf":
            details, extracted = parse_pdf(path)
            file_type = "pdf"
        else:
            details, extracted = parse_table(path, ext)
            file_type = "tabular"
        (folder / "extracted.txt").write_text(extracted, encoding="utf-8")
        record = {"file_id": file_id, "filename": filename, "extension": ext,
                  "file_type": file_type, "size_bytes": total,
                  "uploaded_at": datetime.now(timezone.utc).isoformat(),
                  "content_metadata": details, "status": "processed"}
        (folder / "metadata.json").write_text(json.dumps(record, ensure_ascii=False, indent=2, default=str),
                                               encoding="utf-8")
        return record
    except Exception:
        shutil.rmtree(folder, ignore_errors=True)
        raise
    finally:
        await upload.close()

def list_uploads():
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    result = []
    for path in settings.upload_dir.glob("*/metadata.json"):
        try:
            result.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            pass
    return sorted(result, key=lambda x: x.get("uploaded_at", ""), reverse=True)

def resolve_id(file_id):
    try:
        return str(uuid.UUID(file_id))
    except ValueError:
        return None

def get_upload(file_id):
    parsed = resolve_id(file_id)
    path = settings.upload_dir / parsed / "metadata.json" if parsed else None
    return json.loads(path.read_text(encoding="utf-8")) if path and path.is_file() else None

def get_text(file_id):
    parsed = resolve_id(file_id)
    path = settings.upload_dir / parsed / "extracted.txt" if parsed else None
    return path.read_text(encoding="utf-8") if path and path.is_file() else None

def delete_upload(file_id):
    parsed = resolve_id(file_id)
    folder = settings.upload_dir / parsed if parsed else None
    if not folder or not folder.is_dir():
        return False
    shutil.rmtree(folder)
    return True
