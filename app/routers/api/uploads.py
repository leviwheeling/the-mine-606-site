# app/routers/api/uploads.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from ...services.media import save_upload

router = APIRouter(tags=["Uploads"])

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    data = await file.read()
    ok, res = save_upload(file.filename, file.content_type or "", data)
    if not ok:
        raise HTTPException(status_code=400, detail=res)
    return JSONResponse({"ok": True, "url": res})
