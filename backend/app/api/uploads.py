from fastapi import APIRouter, File, HTTPException, UploadFile, status
from app.ingestion.service import IngestionError, ingest_upload, list_uploads, get_upload, get_text, delete_upload

router = APIRouter(prefix="/api/v1/uploads", tags=["uploads"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)):
    try:
        return await ingest_upload(file)
    except IngestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@router.get("")
def uploads_list():
    items = list_uploads()
    return {"items": items, "count": len(items)}

@router.get("/{file_id}")
def upload_details(file_id: str):
    item = get_upload(file_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Upload not found.")
    return item

@router.get("/{file_id}/text")
def upload_text(file_id: str):
    text = get_text(file_id)
    if text is None:
        raise HTTPException(status_code=404, detail="Extracted text not found.")
    return {"file_id": file_id, "text": text}

@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_upload(file_id: str):
    if not delete_upload(file_id):
        raise HTTPException(status_code=404, detail="Upload not found.")
