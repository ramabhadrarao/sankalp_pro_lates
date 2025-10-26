import os
from fastapi import FastAPI, Depends, HTTPException, Header, UploadFile, File
from fastapi.routing import APIRouter
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from datetime import datetime, timedelta

from common.db.mysql import get_session, Base, engine
from common.security.jwt import decode_token

from services.auth.models import User
from .models import StorageFile
from .schemas import (
    UploadResponse,
    FileUrlResponse,
    PresignedRequest,
    PresignedResponse,
    FileItem,
    FilesResponse,
)

app = FastAPI(title="Storage Service", version="1.0.0")
router = APIRouter(prefix="/api/v1")

Base.metadata.create_all(bind=engine)

# Reuse existing storage root used by user uploads
BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
STORAGE_ROOT = os.path.join(BACKEND_ROOT, "storage")
os.makedirs(STORAGE_ROOT, exist_ok=True)


def require_auth(authorization: str = Header(None), db: Session = Depends(get_session)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    user = db.get(User, user_id)
    if not user or not user.active:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user


def require_admin(user: User = Depends(require_auth)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


@app.get("/health")
async def health():
    return {"status": "ok", "service": "storage"}

# 170: Upload file
@router.post("/storage/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...), user: User = Depends(require_auth), db: Session = Depends(get_session)):
    content = await file.read()
    user_dir = os.path.join(STORAGE_ROOT, str(user.id))
    os.makedirs(user_dir, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    safe_name = f"{ts}_{file.filename}"
    path = os.path.join(user_dir, safe_name)
    with open(path, "wb") as f:
        f.write(content)
    rec = StorageFile(user_id=user.id, filename=file.filename, file_type=file.content_type or None, path=path, url=None)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return UploadResponse(file_id=rec.id, url=None)

# 171: Get file URL
@router.get("/storage/file/{file_id}", response_model=FileUrlResponse)
def file_url(file_id: int, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    rec = db.get(StorageFile, file_id)
    if not rec or rec.user_id != user.id or rec.deleted:
        raise HTTPException(status_code=404, detail="Not found")
    # For local storage, return pseudo URL path
    return FileUrlResponse(url=rec.path, expires_in=3600)

# 172: Download file
@router.get("/storage/download/{file_id}")
def download(file_id: int, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    rec = db.get(StorageFile, file_id)
    if not rec or rec.user_id != user.id or rec.deleted:
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(rec.path, filename=rec.filename, media_type=rec.file_type or "application/octet-stream")

# 173: Delete file
@router.delete("/storage/file/{file_id}")
def delete(file_id: int, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    rec = db.get(StorageFile, file_id)
    if not rec or rec.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    try:
        if os.path.exists(rec.path):
            os.remove(rec.path)
    except Exception:
        pass
    rec.deleted = True
    db.commit()
    return {"deleted": True}

# 174: Generate presigned URL (simulated)
@router.post("/storage/generate-presigned-url", response_model=PresignedResponse)
def presign(req: PresignedRequest, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    # Simulate presigned by creating a record with an expected filename
    user_dir = os.path.join(STORAGE_ROOT, str(user.id))
    os.makedirs(user_dir, exist_ok=True)
    future_path = os.path.join(user_dir, f"presigned_{req.filename}")
    rec = StorageFile(user_id=user.id, filename=req.filename, file_type=req.file_type or None, path=future_path, url=None, expires_at=datetime.utcnow() + timedelta(hours=1))
    db.add(rec)
    db.commit()
    db.refresh(rec)
    upload_url = f"file://{future_path}"
    return PresignedResponse(upload_url=upload_url, file_id=rec.id)

# 175: Get user files
@router.get("/storage/my-files", response_model=FilesResponse)
def my_files(type: str | None = None, page: int = 1, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    stmt = select(StorageFile).where(StorageFile.user_id == user.id, StorageFile.deleted == False).order_by(desc(StorageFile.created_at)).offset((page-1)*20).limit(20)
    if type:
        stmt = stmt.where(StorageFile.file_type == type)
    rows = db.scalars(stmt).all()
    return FilesResponse(files=[FileItem(id=r.id, filename=r.filename, file_type=r.file_type, url=r.url, created_at=r.created_at.isoformat()) for r in rows])

# 176: Cleanup expired (internal/admin)
@router.post("/storage/cleanup-expired")
def cleanup_expired(admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    now = datetime.utcnow()
    stmt = select(StorageFile).where(StorageFile.expires_at != None)
    rows = db.scalars(stmt).all()
    count = 0
    for r in rows:
        if r.expires_at and r.expires_at < now:
            r.deleted = True
            try:
                if os.path.exists(r.path):
                    os.remove(r.path)
            except Exception:
                pass
            count += 1
    db.commit()
    return {"deleted_count": count}

# NEW: List deleted files
@router.get("/storage/my-deleted", response_model=FilesResponse)
def my_deleted(type: str | None = None, page: int = 1, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    stmt = select(StorageFile).where(StorageFile.user_id == user.id, StorageFile.deleted == True).order_by(desc(StorageFile.created_at)).offset((page-1)*20).limit(20)
    if type:
        stmt = stmt.where(StorageFile.file_type == type)
    rows = db.scalars(stmt).all()
    return FilesResponse(files=[FileItem(id=r.id, filename=r.filename, file_type=r.file_type, url=r.url, created_at=r.created_at.isoformat()) for r in rows])

# NEW: Restore deleted file
@router.post("/storage/restore/{file_id}")
def restore(file_id: int, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    rec = db.get(StorageFile, file_id)
    if not rec or rec.user_id != user.id or not rec.deleted:
        raise HTTPException(status_code=404, detail="Not found")
    if not os.path.exists(rec.path):
        raise HTTPException(status_code=409, detail="File missing on disk")
    rec.deleted = False
    db.commit()
    return {"restored": True}

# NEW: Purge deleted file permanently
@router.delete("/storage/purge/{file_id}")
def purge(file_id: int, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    rec = db.get(StorageFile, file_id)
    if not rec or rec.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    try:
        if os.path.exists(rec.path):
            os.remove(rec.path)
    except Exception:
        pass
    db.delete(rec)
    db.commit()
    return {"purged": True}

# NEW: Rename a file
@router.post("/storage/rename/{file_id}")
def rename(file_id: int, new_name: str, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    rec = db.get(StorageFile, file_id)
    if not rec or rec.user_id != user.id or rec.deleted:
        raise HTTPException(status_code=404, detail="Not found")
    if not os.path.exists(rec.path):
        raise HTTPException(status_code=409, detail="File missing on disk")
    dir_path = os.path.dirname(rec.path)
    ts_prefix = os.path.basename(rec.path).split("_", 1)[0]
    new_path = os.path.join(dir_path, f"{ts_prefix}_{new_name}")
    try:
        os.rename(rec.path, new_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rename failed: {str(e)}")
    rec.path = new_path
    rec.filename = new_name
    db.commit()
    return {"renamed": True, "filename": rec.filename}

app.include_router(router)