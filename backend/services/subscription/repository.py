from sqlalchemy.orm import Session
from sqlalchemy import select, update
from datetime import datetime, timedelta

from services.auth.models import User
from .models import Subscription

# Simple tier plan limits; adjust as needed
TIER_LIMITS = {
    "free": 3,
    "starter": 20,
    "pro": 100,
    "enterprise": 1000,
}

TRIAL_DAYS = 14


def get_or_create_subscription(db: Session, user_id: int) -> Subscription:
    stmt = select(Subscription).where(Subscription.user_id == user_id)
    sub = db.scalars(stmt).first()
    if sub:
        # reset monthly period if needed
        month_start = sub.month_start or datetime.utcnow()
        if month_start.month != datetime.utcnow().month or month_start.year != datetime.utcnow().year:
            sub.month_start = datetime.utcnow()
            sub.reports_used = 0
            db.commit()
        return sub
    user = db.get(User, user_id)
    sub = Subscription(user_id=user_id, tier=user.tier or "free")
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


def change_tier(db: Session, user_id: int, new_tier: str) -> Subscription:
    sub = get_or_create_subscription(db, user_id)
    sub.tier = new_tier
    user = db.get(User, user_id)
    if user:
        user.tier = new_tier
    db.commit()
    db.refresh(sub)
    return sub


def start_trial(db: Session, user_id: int) -> Subscription:
    sub = get_or_create_subscription(db, user_id)
    if sub.trial_active():
        return sub
    now = datetime.utcnow()
    sub.trial_started_at = now
    sub.trial_expires_at = now + timedelta(days=TRIAL_DAYS)
    db.commit()
    db.refresh(sub)
    return sub


def set_renewal(db: Session, user_id: int, enabled: bool) -> Subscription:
    sub = get_or_create_subscription(db, user_id)
    sub.renewal_enabled = enabled
    db.commit()
    db.refresh(sub)
    return sub


def get_limits(db: Session, user_id: int) -> tuple[int, int, int]:
    sub = get_or_create_subscription(db, user_id)
    limit = TIER_LIMITS.get(sub.tier, 3)
    used = sub.reports_used or 0
    remaining = max(0, limit - used)
    return limit, used, remaining


def admin_get_subscription(db: Session, user_id: int) -> Subscription | None:
    stmt = select(Subscription).where(Subscription.user_id == user_id)
    return db.scalars(stmt).first()


def admin_update_subscription(db: Session, user_id: int, tier: str | None, renewal_enabled: bool | None) -> Subscription:
    sub = get_or_create_subscription(db, user_id)
    if tier:
        sub.tier = tier
        user = db.get(User, user_id)
        if user:
            user.tier = tier
    if renewal_enabled is not None:
        sub.renewal_enabled = renewal_enabled
    db.commit()
    db.refresh(sub)
    return sub


def consume_report_count(db: Session, user_id: int) -> int:
    """Deduct one report from user's monthly allowance if available.
    Returns remaining reports after deduction.
    """
    sub = get_or_create_subscription(db, user_id)
    limit, used, remaining = get_limits(db, user_id)
    if remaining <= 0:
        return 0
    sub.reports_used = (sub.reports_used or 0) + 1
    db.commit()
    # recompute remaining
    _, used2, remaining2 = get_limits(db, user_id)
    return remaining2