from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from common.db.mysql import get_session, Base, engine
from common.security.jwt import decode_token

from services.auth.models import User
from typing import List, Optional
from .schemas import (
    SubscriptionStatusResponse,
    ChangeTierRequest,
    TrialStartResponse,
    RenewalUpdateRequest,
    ReportLimitsResponse,
    AdminTierUpdateRequest,
    TierItem,
    TierDetailResponse,
    SubscribeResponse,
    TrialStatusResponse,
    CheckLimitResponse,
    DeductResponse,
    FormsSelectionResponse,
    AvailableFormsResponse,
    AnalyticsAdminResponse,
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
    consume_report_count,
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

# Catalog for tiers (placeholder data)
TIERS_CATALOG = {
    "free": {"price": 0, "features": ["Basic access", "Limited reports"]},
    "starter": {"price": 3499, "features": ["Core form", "Basic branding"]},
    "starter+": {"price": 4499, "features": ["Two forms", "Tax planning"]},
    "specialist": {"price": 5999, "features": ["Two forms", "Tax planning"]},
    "specialist+": {"price": 7999, "features": ["Three forms", "Tax planning"]},
    "pro": {"price": 12499, "features": ["All forms", "Financial Horoscope", "1-on-1 interface"]},
    "enterprise": {"price": 0, "features": ["White-label", "Team management"]},
}

@router.get("/subscriptions/tiers", response_model=List[TierItem])
def list_tiers():
    return [TierItem(tier_name=name, price=info["price"], features=info["features"]) for name, info in TIERS_CATALOG.items()]

@router.get("/subscriptions/tiers/{tier_id}", response_model=TierDetailResponse)
def tier_detail(tier_id: str):
    info = TIERS_CATALOG.get(tier_id.lower())
    if not info:
        raise HTTPException(status_code=404, detail="Tier not found")
    return TierDetailResponse(tier_name=tier_id, price=info["price"], features=info["features"])

@router.get("/subscriptions/my-subscription", response_model=SubscriptionStatusResponse)
def my_subscription(user: User = Depends(require_auth), db: Session = Depends(get_session)):
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

@router.post("/subscriptions/trial/activate", response_model=TrialStartResponse)
def trial_activate(user: User = Depends(require_auth), db: Session = Depends(get_session)):
    sub = start_trial(db, user.id)
    return TrialStartResponse(trial_active=sub.trial_active(), trial_expires_at=sub.trial_expires_at)

@router.get("/subscriptions/trial/status", response_model=TrialStatusResponse)
def trial_status(user: User = Depends(require_auth), db: Session = Depends(get_session)):
    sub = get_or_create_subscription(db, user.id)
    _, used, _ = get_limits(db, user.id)
    return TrialStatusResponse(status=sub.trial_active(), reports_used=used, expires_at=sub.trial_expires_at)

@router.post("/subscriptions/subscribe", response_model=SubscribeResponse)
def subscribe(tier_id: str, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    # Placeholder: change tier and return a stub payment URL
    sub = change_tier(db, user.id, tier_id)
    return SubscribeResponse(subscription_id=sub.id, payment_url="")

@router.post("/subscriptions/upgrade", response_model=SubscriptionStatusResponse)
def upgrade(new_tier_id: str, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    sub = change_tier(db, user.id, new_tier_id)
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

@router.post("/subscriptions/downgrade", response_model=SubscriptionStatusResponse)
def downgrade(new_tier_id: str, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    sub = change_tier(db, user.id, new_tier_id)
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

@router.post("/subscriptions/renew")
def renew(tier_id: Optional[str] = None, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    # Placeholder: toggle renewal and return payment URL
    set_renewal(db, user.id, True)
    return {"payment_url": ""}

@router.post("/subscriptions/cancel")
def cancel(reason: Optional[str] = None, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    set_renewal(db, user.id, False)
    return {"cancellation_date": datetime.utcnow().isoformat()}

@router.put("/subscriptions/auto-renew")
def auto_renew(req: RenewalUpdateRequest, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    sub = set_renewal(db, user.id, req.enabled)
    monthly_limit, used, remaining = get_limits(db, user.id)
    return {
        "auto_renew_status": sub.renewal_enabled,
        "tier": sub.tier,
        "reports_remaining": remaining,
    }

@router.get("/subscriptions/history")
def history(user: User = Depends(require_auth)):
    # Placeholder: history not tracked yet
    return []

@router.post("/subscriptions/forms/select", response_model=FormsSelectionResponse)
def select_forms(form_ids: List[int], user: User = Depends(require_auth)):
    # Placeholder: selection not persisted
    return FormsSelectionResponse(selected_forms=form_ids)

@router.get("/subscriptions/forms/available", response_model=AvailableFormsResponse)
def available_forms(user: User = Depends(require_auth)):
    # Placeholder list based on tier
    return AvailableFormsResponse(available_forms=[])

@router.post("/subscriptions/reports/check-limit", response_model=CheckLimitResponse)
def reports_check_limit(user: User = Depends(require_auth), db: Session = Depends(get_session)):
    limit, used, remaining = get_limits(db, user.id)
    return CheckLimitResponse(can_generate=remaining > 0, remaining=remaining)

@router.post("/subscriptions/reports/deduct", response_model=DeductResponse)
def reports_deduct(user: User = Depends(require_auth), db: Session = Depends(get_session)):
    remaining = consume_report_count(db, user.id)
    return DeductResponse(remaining_reports=remaining)

@router.post("/subscriptions/{user_id}/extend")
def admin_extend(user_id: int, days: int, admin: User = Depends(require_admin)):
    # Placeholder: no paid expiry tracking yet
    return {"new_end_date": None}

@router.post("/subscriptions/{user_id}/add-reports")
def admin_add_reports(user_id: int, count: int, reason: Optional[str] = None, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    # Placeholder: no bonus tracking; returns current limit
    limit, used, remaining = get_limits(db, user_id)
    return {"new_limit": limit}

@router.put("/subscriptions/{user_id}/change-tier", response_model=SubscriptionStatusResponse)
def admin_change_tier(user_id: int, req: AdminTierUpdateRequest, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    sub = admin_update_subscription(db, user_id, req.tier, None)
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

@router.get("/subscriptions/analytics", response_model=AnalyticsAdminResponse)
def subs_analytics(frm: Optional[str] = None, to: Optional[str] = None, admin: User = Depends(require_admin)):
    # Placeholder data
    return AnalyticsAdminResponse(stats={"signups": 0, "upgrades": 0})
app.include_router(router)