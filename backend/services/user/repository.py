from sqlalchemy.orm import Session
from sqlalchemy import select, update, desc
from datetime import datetime
import json
import os
from typing import Optional

from services.auth.models import User
from .models import ProfileImage, ProfileUpdateRequest, ActivityLog

# Store uploads under backend/storage/<user_id>/
BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
STORAGE_ROOT = os.path.join(BACKEND_ROOT, "storage")

os.makedirs(STORAGE_ROOT, exist_ok=True)

def get_profile_images(db: Session, user_id: int):
    stmt = select(ProfileImage).where(ProfileImage.user_id == user_id)
    rows = db.scalars(stmt).all()
    latest = {row.type: row for row in rows}
    return latest

def save_upload(db: Session, user_id: int, file_bytes: bytes, filename: str, upload_type: str) -> ProfileImage:
    user_dir = os.path.join(STORAGE_ROOT, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    safe_name = f"{upload_type}_{timestamp}_{filename}"
    path = os.path.join(user_dir, safe_name)
    with open(path, "wb") as f:
        f.write(file_bytes)
    rec = ProfileImage(user_id=user_id, type=upload_type, path=path)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

def delete_upload(db: Session, user_id: int, upload_type: str) -> bool:
    stmt = select(ProfileImage).where(ProfileImage.user_id == user_id, ProfileImage.type == upload_type).order_by(desc(ProfileImage.created_at))
    rec = db.scalars(stmt).first()
    if not rec:
        return False
    try:
        if os.path.exists(rec.path):
            os.remove(rec.path)
    except Exception:
        pass
    db.delete(rec)
    db.commit()
    return True

def update_allowed_fields(db: Session, user_id: int, mobile: Optional[str], email: Optional[str]) -> User:
    user = db.get(User, user_id)
    if mobile is not None:
        user.mobile = mobile
    if email is not None:
        user.email = email
        user.verified = False  # re-verify after email change
    db.commit()
    db.refresh(user)
    return user

def is_in_grace_period(user: User) -> tuple[bool, Optional[datetime], int]:
    if not user.locked_fields_after:
        return False, None, 0
    now = datetime.utcnow()
    in_period = now < user.locked_fields_after
    remaining = int((user.locked_fields_after - now).total_seconds()) if in_period else 0
    return in_period, user.locked_fields_after, remaining

def lock_profile_fields(db: Session, user_id: int) -> tuple[bool, datetime]:
    locked_at = datetime.utcnow()
    db.execute(update(User).where(User.id == user_id).values(locked_fields_after=locked_at))
    db.commit()
    return True, locked_at

def create_critical_update(db: Session, user_id: int, field_name: str, new_value: str, reason: Optional[str]) -> ProfileUpdateRequest:
    req = ProfileUpdateRequest(user_id=user_id, field_name=field_name, new_value=new_value, reason=reason)
    db.add(req)
    db.commit()
    db.refresh(req)
    return req

def get_pending_updates(db: Session, user_id: int):
    stmt = select(ProfileUpdateRequest).where(ProfileUpdateRequest.user_id == user_id, ProfileUpdateRequest.status == "pending").order_by(desc(ProfileUpdateRequest.created_at))
    return db.scalars(stmt).all()

def log_action(db: Session, user_id: int, action: str, meta: dict | None = None) -> ActivityLog:
    rec = ActivityLog(user_id=user_id, action=action, meta=json.dumps(meta or {}))
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

def list_activity(db: Session, user_id: int, page: int, limit: int):
    stmt = select(ActivityLog).where(ActivityLog.user_id == user_id).order_by(desc(ActivityLog.created_at)).offset((page-1)*limit).limit(limit)
    return db.scalars(stmt).all()

def admin_search_users(db: Session, q: str, page: int, limit: int):
    stmt = select(User).where((User.email.like(f"%{q}%")) | (User.name.like(f"%{q}%")) | (User.mobile.like(f"%{q}%")).self_group()).order_by(User.id).offset((page-1)*limit).limit(limit)
    return db.scalars(stmt).all()

def admin_get_user(db: Session, user_id: int) -> Optional[User]:
    return db.get(User, user_id)

def admin_update_user(db: Session, user_id: int, data: dict) -> Optional[User]:
    user = db.get(User, user_id)
    if not user:
        return None
    for k, v in data.items():
        if hasattr(user, k) and k not in {"id", "password_hash"}:
            setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user

def set_user_active(db: Session, user_id: int, active: bool) -> Optional[User]:
    user = db.get(User, user_id)
    if not user:
        return None
    user.active = active
    db.commit()
    db.refresh(user)
    return user