from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Header
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from common.db.mysql import get_session, Base, engine
from common.security.jwt import decode_token
from common.i18n import t, get_locale

from services.auth.models import User
from .models import ProfileImage, ProfileUpdateRequest, ActivityLog
from .schemas import (
    ProfileResponse,
    UpdateProfileRequest,
    UploadType,
    GraceStatusResponse,
    ProfileLockResponse,
    CriticalUpdateRequest,
    CriticalUpdateItem,
    ActivityItem,
    DashboardStatsResponse,
    UserSearchItem,
    ReferralInfoResponse,
)
from .repository import (
    get_profile_images,
    save_upload,
    delete_upload,
    update_allowed_fields,
    is_in_grace_period,
    lock_profile_fields,
    create_critical_update,
    get_pending_updates,
    log_action,
    list_activity,
    admin_search_users,
    admin_get_user,
    admin_update_user,
    set_user_active,
)

app = FastAPI(title="User Service", version="1.0.0")
router = APIRouter(prefix="/api/v1")

# Ensure tables exist
Base.metadata.create_all(bind=engine)


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


def as_profile_response(user: User, images: dict) -> ProfileResponse:
    return ProfileResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        mobile=user.mobile,
        organization=user.organization,
        role=user.role,
        tier=user.tier,
        verified=user.verified,
        user_type=user.user_type,
        city=user.city,
        terms_accepted=user.terms_accepted,
        mfa_enabled=user.mfa_enabled,
        active=user.active,
        photo_path=(images.get("photo").path if images.get("photo") else None),
        logo_path=(images.get("logo").path if images.get("logo") else None),
        locked_fields_after=user.locked_fields_after,
    )

@router.get("/health")
async def health():
    return {"status": "ok", "service": "user"}

# 15: GET profile
@router.get("/users/profile", response_model=ProfileResponse)
def get_profile(user: User = Depends(require_auth), db: Session = Depends(get_session)):
    images = get_profile_images(db, user.id)
    return as_profile_response(user, images)

# 16: PUT profile update (allowed fields only)
@router.put("/users/profile", response_model=ProfileResponse)
def update_profile(req: UpdateProfileRequest, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    updated = update_allowed_fields(db, user.id, req.mobile, req.email)
    log_action(db, user.id, "profile_update", {"mobile": req.mobile, "email": req.email})
    images = get_profile_images(db, user.id)
    return as_profile_response(updated, images)

# 17/18: Upload photo or logo
@router.post("/users/profile/photo", response_model=ProfileResponse)
async def upload_photo(file: UploadFile = File(...), user: User = Depends(require_auth), db: Session = Depends(get_session)):
    content = await file.read()
    rec = save_upload(db, user.id, content, file.filename, "photo")
    log_action(db, user.id, "upload", {"type": "photo", "path": rec.path})
    images = get_profile_images(db, user.id)
    return as_profile_response(user, images)

@router.post("/users/profile/logo", response_model=ProfileResponse)
async def upload_logo(file: UploadFile = File(...), user: User = Depends(require_auth), db: Session = Depends(get_session)):
    content = await file.read()
    rec = save_upload(db, user.id, content, file.filename, "logo")
    log_action(db, user.id, "upload", {"type": "logo", "path": rec.path})
    images = get_profile_images(db, user.id)
    return as_profile_response(user, images)

@router.delete("/users/profile/photo")
def delete_photo(user: User = Depends(require_auth), db: Session = Depends(get_session)):
    ok = delete_upload(db, user.id, "photo")
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    log_action(db, user.id, "delete_upload", {"type": "photo"})
    return {"deleted": True}

@router.delete("/users/profile/logo")
def delete_logo(user: User = Depends(require_auth), db: Session = Depends(get_session)):
    ok = delete_upload(db, user.id, "logo")
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    log_action(db, user.id, "delete_upload", {"type": "logo"})
    return {"deleted": True}

@router.get("/users/grace-period-status", response_model=GraceStatusResponse)
def grace_period_status(user: User = Depends(require_auth)):
    in_period, expires_at, remaining = is_in_grace_period(user)
    return GraceStatusResponse(in_grace_period=in_period, expires_at=expires_at, seconds_remaining=remaining)

@router.post("/users/profile/update-request", response_model=CriticalUpdateItem)
def update_request(req: CriticalUpdateRequest, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    item = create_critical_update(db, user.id, req.field_name, req.new_value, req.reason)
    log_action(db, user.id, "critical_update_requested", {"field": req.field_name})
    return CriticalUpdateItem(id=item.id, field_name=item.field_name, new_value=item.new_value, reason=item.reason, status=item.status, created_at=item.created_at)

@router.get("/users/profile/update-requests", response_model=List[CriticalUpdateItem])
def update_requests(user: User = Depends(require_auth), db: Session = Depends(get_session)):
    items = get_pending_updates(db, user.id)
    return [CriticalUpdateItem(id=i.id, field_name=i.field_name, new_value=i.new_value, reason=i.reason, status=i.status, created_at=i.created_at) for i in items]

@router.get("/users/activity-log", response_model=List[ActivityItem])
def activity_log(page: int = 1, limit: int = 20, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    items = list_activity(db, user.id, page, limit)
    return [ActivityItem(id=i.id, action=i.action, meta=i.meta, created_at=i.created_at) for i in items]

@router.get("/users/dashboard-stats", response_model=DashboardStatsResponse)
def dashboard_stats_alias(user: User = Depends(require_auth)):
    return DashboardStatsResponse(reports_generated=0, reports_remaining=0, subscription_tier=user.tier)

@router.get("/users/search", response_model=List[UserSearchItem])
def users_search_admin(q: str, page: int = 1, limit: int = 20, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    users = admin_search_users(db, q, page, limit)
    return [UserSearchItem(id=u.id, name=u.name, email=u.email, mobile=u.mobile, active=u.active, verified=u.verified) for u in users]

@router.get("/users/{user_id}", response_model=ProfileResponse)
def users_get_admin(user_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    user = admin_get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    images = get_profile_images(db, user.id)
    return as_profile_response(user, images)

@router.put("/users/{user_id}/profile", response_model=ProfileResponse)
def users_update_admin(user_id: int, data: dict, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    user = admin_update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    log_action(db, admin.id, "admin_update_user", {"user_id": user_id})
    images = get_profile_images(db, user.id)
    return as_profile_response(user, images)

@router.post("/users/{user_id}/activate")
def users_activate_admin(user_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    user = set_user_active(db, user_id, True)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    log_action(db, admin.id, "admin_activate_user", {"user_id": user_id})
    return {"activated": True}

@router.post("/users/{user_id}/deactivate")
def users_deactivate_admin(user_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    user = set_user_active(db, user_id, False)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    log_action(db, admin.id, "admin_deactivate_user", {"user_id": user_id})
    return {"deactivated": True}

# 27: Admin search users
@router.get("/admin/users/search", response_model=List[UserSearchItem])
def admin_search(q: str, page: int = 1, limit: int = 20, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    users = admin_search_users(db, q, page, limit)
    return [UserSearchItem(id=u.id, name=u.name, email=u.email, mobile=u.mobile, active=u.active, verified=u.verified) for u in users]

# 28: Admin get user by id
@router.get("/admin/users/{user_id}", response_model=ProfileResponse)
def admin_get(user_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    user = admin_get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    images = get_profile_images(db, user.id)
    return as_profile_response(user, images)

# 29: Admin update user profile
@router.put("/admin/users/{user_id}", response_model=ProfileResponse)
def admin_update(user_id: int, data: dict, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    user = admin_update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    log_action(db, admin.id, "admin_update_user", {"user_id": user_id})
    images = get_profile_images(db, user.id)
    return as_profile_response(user, images)

# 30: Admin activate user
@router.post("/admin/users/{user_id}/activate")
def admin_activate(user_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    user = set_user_active(db, user_id, True)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    log_action(db, admin.id, "admin_activate_user", {"user_id": user_id})
    return {"activated": True}

# 31: Admin deactivate user
@router.post("/admin/users/{user_id}/deactivate")
def admin_deactivate(user_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    user = set_user_active(db, user_id, False)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    log_action(db, admin.id, "admin_deactivate_user", {"user_id": user_id})
    return {"deactivated": True}

# 32: Referral info (stub)
@router.get("/users/referral-info", response_model=ReferralInfoResponse)
def referral_info(user: User = Depends(require_auth)):
    # TODO: integrate with affiliate service
    link = f"https://salahkaarpro.com/partners/{user.id}"
    return ReferralInfoResponse(referred_by=None, referral_link=link)

@router.post("/users/profile/lock", response_model=ProfileLockResponse)
def lock_profile(user: User = Depends(require_auth), db: Session = Depends(get_session)):
    ok, locked_at = lock_profile_fields(db, user.id)
    log_action(db, user.id, "lock_profile", {"locked_at": locked_at.isoformat()})
    return ProfileLockResponse(locked=ok, locked_at=locked_at)

app.include_router(router)