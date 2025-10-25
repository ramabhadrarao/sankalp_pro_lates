from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from common.db.mysql import get_session, Base, engine
from common.security.jwt import decode_token

from services.auth.models import User
from .schemas import (
    SubscriptionStatusResponse,
    ChangeTierRequest,
    TrialStartResponse,
    RenewalUpdateRequest,
    ReportLimitsResponse,
    AdminTierUpdateRequest,
)
from .repository import (
    get_or_create_subscription,
    change_tier,
    start_trial,
    set_renewal,
    get_limits,
    admin_get_subscription,
    admin_update_subscription,
    TIER_LIMITS,
)

app = FastAPI(title="Subscription Service", version="1.0.0")
router = APIRouter(prefix="/api/v1")

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


@app.get("/health")
async def health():
    return {"status": "ok", "service": "subscription"}

@router.get("/subscription/status", response_model=SubscriptionStatusResponse)
def status(user: User = Depends(require_auth), db: Session = Depends(get_session)):
    sub = get_or_create_subscription(db, user.id)
    monthly_limit, used, remaining = get_limits(db, user.id)
    return SubscriptionStatusResponse(
        tier=sub.tier,
        renewal_enabled=sub.renewal_enabled,
        trial_active=sub.trial_active(),
        trial_expires_at=sub.trial_expires_at,
        reports_used=used,
        monthly_limit=monthly_limit,
        reports_remaining=remaining,
    )

@router.post("/subscription/change-tier", response_model=SubscriptionStatusResponse)
def change_tier_endpoint(req: ChangeTierRequest, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    if req.new_tier not in TIER_LIMITS:
        raise HTTPException(status_code=400, detail="Invalid tier")
    sub = change_tier(db, user.id, req.new_tier)
    monthly_limit, used, remaining = get_limits(db, user.id)
    return SubscriptionStatusResponse(
        tier=sub.tier,
        renewal_enabled=sub.renewal_enabled,
        trial_active=sub.trial_active(),
        trial_expires_at=sub.trial_expires_at,
        reports_used=used,
        monthly_limit=monthly_limit,
        reports_remaining=remaining,
    )

@router.post("/subscription/start-trial", response_model=TrialStartResponse)
def start_trial_endpoint(user: User = Depends(require_auth), db: Session = Depends(get_session)):
    sub = start_trial(db, user.id)
    return TrialStartResponse(trial_active=sub.trial_active(), trial_expires_at=sub.trial_expires_at)

@router.put("/subscription/renewal", response_model=SubscriptionStatusResponse)
def set_renewal_endpoint(req: RenewalUpdateRequest, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    sub = set_renewal(db, user.id, req.enabled)
    monthly_limit, used, remaining = get_limits(db, user.id)
    return SubscriptionStatusResponse(
        tier=sub.tier,
        renewal_enabled=sub.renewal_enabled,
        trial_active=sub.trial_active(),
        trial_expires_at=sub.trial_expires_at,
        reports_used=used,
        monthly_limit=monthly_limit,
        reports_remaining=remaining,
    )

@router.get("/subscription/report-limits", response_model=ReportLimitsResponse)
def report_limits(user: User = Depends(require_auth), db: Session = Depends(get_session)):
    monthly_limit, used, remaining = get_limits(db, user.id)
    sub = get_or_create_subscription(db, user.id)
    return ReportLimitsResponse(tier=sub.tier, monthly_limit=monthly_limit, reports_used=used, reports_remaining=remaining)

# Admin endpoints
@router.get("/admin/subscription/{user_id}", response_model=SubscriptionStatusResponse)
def admin_get(user_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    sub = admin_get_subscription(db, user_id)
    if not sub:
        sub = get_or_create_subscription(db, user_id)
    monthly_limit, used, remaining = get_limits(db, user_id)
    return SubscriptionStatusResponse(
        tier=sub.tier,
        renewal_enabled=sub.renewal_enabled,
        trial_active=sub.trial_active(),
        trial_expires_at=sub.trial_expires_at,
        reports_used=used,
        monthly_limit=monthly_limit,
        reports_remaining=remaining,
    )

@router.put("/admin/subscription/{user_id}", response_model=SubscriptionStatusResponse)
def admin_update(user_id: int, req: AdminTierUpdateRequest, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    sub = admin_update_subscription(db, user_id, req.tier, req.renewal_enabled)
    monthly_limit, used, remaining = get_limits(db, user_id)
    return SubscriptionStatusResponse(
        tier=sub.tier,
        renewal_enabled=sub.renewal_enabled,
        trial_active=sub.trial_active(),
        trial_expires_at=sub.trial_expires_at,
        reports_used=used,
        monthly_limit=monthly_limit,
        reports_remaining=remaining,
    )

app.include_router(router)