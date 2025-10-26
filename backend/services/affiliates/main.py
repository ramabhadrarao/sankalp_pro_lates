from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Header
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, date
import uuid

from common.db.mysql import get_session, engine
from common.security.jwt import decode_token
from services.auth.models import User  # reusing User

from .models import AffiliateProfile, AffiliateApplication, Referral, Commission, Payout, AffiliateBankAccount
from .schemas import (
    ApplyRequest,
    ApplicationStatusResponse,
    LandingPageUpdateRequest,
    LandingPageResponse,
    MyLinksResponse,
    DashboardResponse,
    ReferralItem,
    ReferralListResponse,
    CommissionItem,
    CommissionListResponse,
    PayoutItem,
    PayoutListResponse,
    PerformanceResponse,
    BankAccountCreateRequest,
    BankAccountItem,
    BankAccountListResponse,
    BankAccountUpdateRequest,
    MarketingAssetsResponse,
    MarketingAssetItem,
)


app = FastAPI(title="Affiliates Service", version="1.0.0")
router = APIRouter(prefix="/api/v1/affiliates", tags=["affiliates"])


# Ensure tables exist
from common.db.mysql import Base
Base.metadata.create_all(bind=engine)


def _ensure_affiliate_profile(session: Session, user: User) -> AffiliateProfile:
    profile = session.query(AffiliateProfile).filter_by(user_id=user.id).first()
    if not profile:
        # generate a unique code
        code = f"AFF{user.id}"
        # fallback in case collision
        if session.query(AffiliateProfile).filter_by(code=code).first():
            code = f"AFF-{uuid.uuid4().hex[:8]}"
        profile = AffiliateProfile(user_id=user.id, code=code, approved=False)
        session.add(profile)
        session.flush()
    return profile


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


def require_affiliate(user: User = Depends(require_auth), session: Session = Depends(get_session)) -> User:
    # Here we treat any approved AffiliateProfile for the user as affiliate access
    profile = _ensure_affiliate_profile(session, user)
    if not profile.approved:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Affiliate access not approved yet")
    return user


@router.post("/apply", response_model=ApplicationStatusResponse)
def apply_affiliate(payload: ApplyRequest, user: User = Depends(require_auth), session: Session = Depends(get_session)):
    existing = session.query(AffiliateApplication).filter_by(user_id=user.id).order_by(AffiliateApplication.created_at.desc()).first()
    if existing and existing.status in ("pending", "approved"):
        return ApplicationStatusResponse(status=existing.status, review_notes=existing.review_notes, application_id=existing.id)
    app_row = AffiliateApplication(
        user_id=user.id,
        company_name=payload.company_name,
        bio=payload.bio,
        why_join=payload.why_join,
        status="pending",
    )
    session.add(app_row)
    session.flush()
    return ApplicationStatusResponse(status=app_row.status, application_id=app_row.id)


@router.get("/application-status", response_model=ApplicationStatusResponse)
def application_status(user: User = Depends(require_auth), session: Session = Depends(get_session)):
    existing = session.query(AffiliateApplication).filter_by(user_id=user.id).order_by(AffiliateApplication.created_at.desc()).first()
    if not existing:
        return ApplicationStatusResponse(status="not_applied")
    return ApplicationStatusResponse(status=existing.status, review_notes=existing.review_notes, application_id=existing.id)


@router.get("/my-links", response_model=MyLinksResponse, dependencies=[Depends(require_affiliate)])
def my_links(user: User = Depends(require_auth), session: Session = Depends(get_session)):
    profile = _ensure_affiliate_profile(session, user)
    base_host = "https://sankalp.pro"  # TODO: use config
    landing_slug = profile.landing_page_slug or profile.code.lower()
    landing_url = f"{base_host}/partners/{landing_slug}"
    referral_link = f"{base_host}/signup?ref={profile.code}"
    return MyLinksResponse(referral_link=referral_link, landing_page_url=landing_url, qr_code=None)


@router.get("/landing-page", response_model=LandingPageResponse, dependencies=[Depends(require_affiliate)])
def get_landing_page(user: User = Depends(require_auth), session: Session = Depends(get_session)):
    profile = _ensure_affiliate_profile(session, user)
    base_host = "https://sankalp.pro"
    landing_slug = profile.landing_page_slug or profile.code.lower()
    landing_url = f"{base_host}/partners/{landing_slug}"
    referral_link = f"{base_host}/signup?ref={profile.code}"
    return LandingPageResponse(
        affiliate_id=profile.id,
        name=user.full_name if hasattr(user, "full_name") else user.email,
        photo_url=profile.photo_url,
        logo_url=profile.logo_url,
        custom_headline=profile.custom_headline,
        special_offer=profile.special_offer,
        bio=profile.bio,
        custom_message=profile.custom_message,
        cta_text=profile.cta_text,
        landing_page_url=landing_url,
        referral_link=referral_link,
        qr_code=None,
    )


@router.put("/landing-page", response_model=LandingPageResponse, dependencies=[Depends(require_affiliate)])
def update_landing_page(payload: LandingPageUpdateRequest, user: User = Depends(require_auth), session: Session = Depends(get_session)):
    profile = _ensure_affiliate_profile(session, user)
    if payload.headline is not None:
        profile.custom_headline = payload.headline
    if payload.offer is not None:
        profile.special_offer = payload.offer
    if payload.custom_message is not None:
        profile.custom_message = payload.custom_message
    if payload.cta_text is not None:
        profile.cta_text = payload.cta_text
    profile.updated_at = datetime.utcnow()
    session.add(profile)
    session.flush()

    base_host = "https://sankalp.pro"
    landing_slug = profile.landing_page_slug or profile.code.lower()
    landing_url = f"{base_host}/partners/{landing_slug}"
    referral_link = f"{base_host}/signup?ref={profile.code}"
    return LandingPageResponse(
        affiliate_id=profile.id,
        name=user.full_name if hasattr(user, "full_name") else user.email,
        photo_url=profile.photo_url,
        logo_url=profile.logo_url,
        custom_headline=profile.custom_headline,
        special_offer=profile.special_offer,
        bio=profile.bio,
        custom_message=profile.custom_message,
        cta_text=profile.cta_text,
        landing_page_url=landing_url,
        referral_link=referral_link,
        qr_code=None,
    )


@router.post("/landing-page/photo", dependencies=[Depends(require_affiliate)])
async def upload_landing_photo(file: UploadFile = File(...), user: User = Depends(require_auth), session: Session = Depends(get_session)):
    profile = _ensure_affiliate_profile(session, user)
    # In real implementation, forward to storage service and get URL
    # For now, stub with a pseudo path
    profile.photo_url = f"/uploads/affiliates/{profile.code}/photo/{uuid.uuid4().hex}_{file.filename}"
    profile.updated_at = datetime.utcnow()
    session.add(profile)
    session.flush()
    return {"photo_url": profile.photo_url}


@router.get("/dashboard", response_model=DashboardResponse, dependencies=[Depends(require_affiliate)])
def dashboard(user: User = Depends(require_auth), session: Session = Depends(get_session)):
    total_ref = session.query(Referral).filter_by(affiliate_user_id=user.id).count()
    active_advisors = session.query(Referral).filter_by(affiliate_user_id=user.id, status="active").count()
    pending_commission = session.query(Commission).filter_by(affiliate_user_id=user.id, status="pending_approval").with_entities(Commission.commission_amount).all()
    approved_commission = session.query(Commission).filter_by(affiliate_user_id=user.id, status="approved").with_entities(Commission.commission_amount).all()
    paid_commission = session.query(Commission).filter_by(affiliate_user_id=user.id, payout_status="paid").with_entities(Commission.commission_amount).all()

    def _sum(rows):
        return float(sum(r[0] or 0.0 for r in rows))

    return DashboardResponse(
        total_referrals=total_ref,
        active_advisors=active_advisors,
        pending_commission=_sum(pending_commission),
        approved_commission=_sum(approved_commission),
        paid_commission=_sum(paid_commission),
        this_month_performance=None,
    )


@router.get("/referrals", response_model=ReferralListResponse, dependencies=[Depends(require_affiliate)])
def list_referrals(
    status_filter: Optional[str] = Query(None, description="trial|active|expired|converted"),
    page: int = 1,
    limit: int = 20,
    user: User = Depends(require_auth),
    session: Session = Depends(get_session),
):
    q = session.query(Referral).filter_by(affiliate_user_id=user.id)
    if status_filter:
        q = q.filter(Referral.status == status_filter)
    q = q.order_by(Referral.created_at.desc())
    rows = q.offset((page - 1) * limit).limit(limit).all()
    items = [
        ReferralItem(
            id=str(r.id),
            advisor_user_id=r.advisor_user_id,
            signup_date=r.signup_date.isoformat() if r.signup_date else None,
            status=r.status,
        )
        for r in rows
    ]
    return ReferralListResponse(referrals=items, page=page, limit=limit)


@router.get("/referral/{referral_id}", response_model=ReferralItem, dependencies=[Depends(require_affiliate)])
def get_referral(referral_id: int, user: User = Depends(require_auth), session: Session = Depends(get_session)):
    r = session.query(Referral).filter_by(id=referral_id, affiliate_user_id=user.id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Referral not found")
    return ReferralItem(
        id=str(r.id), advisor_user_id=r.advisor_user_id, signup_date=r.signup_date.isoformat() if r.signup_date else None, status=r.status
    )


@router.get("/commissions", response_model=CommissionListResponse, dependencies=[Depends(require_affiliate)])
def list_commissions(
    status_filter: Optional[str] = Query(None, description="pending_approval|approved|rejected|modified_approved"),
    page: int = 1,
    limit: int = 20,
    user: User = Depends(require_auth),
    session: Session = Depends(get_session),
):
    q = session.query(Commission).filter_by(affiliate_user_id=user.id)
    if status_filter:
        q = q.filter(Commission.status == status_filter)
    q = q.order_by(Commission.created_at.desc())
    rows = q.offset((page - 1) * limit).limit(limit).all()
    items = [
        CommissionItem(
            id=str(c.id),
            advisor_user_id=c.advisor_user_id,
            transaction_type=c.transaction_type,
            subscription_tier=c.subscription_tier,
            gross_amount=c.gross_amount or 0.0,
            net_amount=c.net_amount or 0.0,
            commission_rate=c.commission_rate or 0.0,
            commission_amount=c.commission_amount or 0.0,
            status=c.status,
            payout_status=c.payout_status,
            created_at=c.created_at.isoformat() if c.created_at else None,
        )
        for c in rows
    ]
    return CommissionListResponse(commissions=items, page=page, limit=limit)


@router.get("/commission/{commission_id}", response_model=CommissionItem, dependencies=[Depends(require_affiliate)])
def get_commission(commission_id: int, user: User = Depends(require_auth), session: Session = Depends(get_session)):
    c = session.query(Commission).filter_by(id=commission_id, affiliate_user_id=user.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Commission not found")
    return CommissionItem(
        id=str(c.id),
        advisor_user_id=c.advisor_user_id,
        transaction_type=c.transaction_type,
        subscription_tier=c.subscription_tier,
        gross_amount=c.gross_amount or 0.0,
        net_amount=c.net_amount or 0.0,
        commission_rate=c.commission_rate or 0.0,
        commission_amount=c.commission_amount or 0.0,
        status=c.status,
        payout_status=c.payout_status,
        created_at=c.created_at.isoformat() if c.created_at else None,
    )


@router.get("/payouts", response_model=PayoutListResponse, dependencies=[Depends(require_affiliate)])
def list_payouts(user: User = Depends(require_auth), session: Session = Depends(get_session)):
    rows = session.query(Payout).filter_by(affiliate_user_id=user.id).order_by(Payout.processed_at.desc()).all()
    items = [
        PayoutItem(
            id=str(p.id),
            amount=p.amount or 0.0,
            payment_method=p.payment_method,
            transaction_id=p.transaction_id,
            processed_at=p.processed_at.isoformat() if p.processed_at else None,
        )
        for p in rows
    ]
    return PayoutListResponse(payouts=items)


@router.get("/performance", response_model=PerformanceResponse, dependencies=[Depends(require_affiliate)])
def performance(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    user: User = Depends(require_auth),
    session: Session = Depends(get_session),
):
    # Basic aggregate demo; replace with real analytics logic
    q_ref = session.query(Referral).filter_by(affiliate_user_id=user.id)
    q_comm = session.query(Commission).filter_by(affiliate_user_id=user.id)

    def _parse_date(s: Optional[str]):
        if not s:
            return None
        try:
            return datetime.fromisoformat(s).date()
        except Exception:
            return None

    sd = _parse_date(start_date)
    ed = _parse_date(end_date)
    if sd:
        q_ref = q_ref.filter(Referral.created_at >= sd)
        q_comm = q_comm.filter(Commission.created_at >= sd)
    if ed:
        q_ref = q_ref.filter(Referral.created_at <= ed)
        q_comm = q_comm.filter(Commission.created_at <= ed)

    total_ref = q_ref.count()
    approved_comm_amount = sum((c.commission_amount or 0.0) for c in q_comm.filter(Commission.status == "approved").all())
    # Conversion: active / total
    active = q_ref.filter(Referral.status == "active").count()
    conversion_rate = float(active) / float(total_ref) * 100.0 if total_ref else 0.0

    return PerformanceResponse(conversion_rate=conversion_rate, revenue_generated=approved_comm_amount, over_time=None)


@router.post("/bank-account", response_model=BankAccountItem, dependencies=[Depends(require_affiliate)])
def add_bank_account(payload: BankAccountCreateRequest, user: User = Depends(require_auth), session: Session = Depends(get_session)):
    acct = AffiliateBankAccount(
        affiliate_user_id=user.id,
        account_holder=payload.account_holder,
        bank_name=payload.bank_name,
        account_number=payload.account_number,
        ifsc=payload.ifsc,
        account_type=payload.account_type,
    )
    session.add(acct)
    session.flush()
    return BankAccountItem(
        id=acct.id,
        account_holder=acct.account_holder,
        bank_name=acct.bank_name,
        account_number=acct.account_number,
        ifsc=acct.ifsc,
        account_type=acct.account_type,
    )

@router.get("/bank-account", response_model=BankAccountListResponse, dependencies=[Depends(require_affiliate)])
def list_bank_accounts(user: User = Depends(require_auth), session: Session = Depends(get_session)):
    rows = session.query(AffiliateBankAccount).filter_by(affiliate_user_id=user.id).order_by(AffiliateBankAccount.created_at.desc()).all()
    items = [
        BankAccountItem(
            id=r.id,
            account_holder=r.account_holder,
            bank_name=r.bank_name,
            account_number=r.account_number,
            ifsc=r.ifsc,
            account_type=r.account_type,
        )
        for r in rows
    ]
    return BankAccountListResponse(items=items)

@router.put("/bank-account/{account_id}", response_model=BankAccountItem, dependencies=[Depends(require_affiliate)])
def update_bank_account(account_id: int, payload: BankAccountUpdateRequest, user: User = Depends(require_auth), session: Session = Depends(get_session)):
    acct = session.query(AffiliateBankAccount).filter_by(id=account_id, affiliate_user_id=user.id).first()
    if not acct:
        raise HTTPException(status_code=404, detail="Bank account not found")
    if payload.account_holder is not None:
        acct.account_holder = payload.account_holder
    if payload.bank_name is not None:
        acct.bank_name = payload.bank_name
    if payload.account_number is not None:
        acct.account_number = payload.account_number
    if payload.ifsc is not None:
        acct.ifsc = payload.ifsc
    if payload.account_type is not None:
        acct.account_type = payload.account_type
    acct.updated_at = datetime.utcnow()
    session.add(acct)
    session.flush()
    return BankAccountItem(
        id=acct.id,
        account_holder=acct.account_holder,
        bank_name=acct.bank_name,
        account_number=acct.account_number,
        ifsc=acct.ifsc,
        account_type=acct.account_type,
    )

@router.delete("/bank-account/{account_id}", dependencies=[Depends(require_affiliate)])
def delete_bank_account(account_id: int, user: User = Depends(require_auth), session: Session = Depends(get_session)):
    acct = session.query(AffiliateBankAccount).filter_by(id=account_id, affiliate_user_id=user.id).first()
    if not acct:
        raise HTTPException(status_code=404, detail="Bank account not found")
    session.delete(acct)
    session.flush()
    return {"deleted": True}

@router.get("/marketing-assets", response_model=MarketingAssetsResponse, dependencies=[Depends(require_affiliate)])
def marketing_assets(user: User = Depends(require_auth)):
    items = [
        MarketingAssetItem(id=1, title="Sankalp Pro Banner", description="Promote Sankalp Pro", asset_type="image", url="https://cdn.sankalp.pro/assets/banner1.png"),
        MarketingAssetItem(id=2, title="Signup CTA", description="Text snippet for CTA", asset_type="text", url="https://cdn.sankalp.pro/assets/cta.txt"),
        MarketingAssetItem(id=3, title="Referral QR", description="QR for your referral link", asset_type="image", url=f"https://sankalp.pro/qrcode?ref={user.id}"),
    ]
    return MarketingAssetsResponse(items=items)

app.include_router(router)

# Admin guard consistent with other services
def require_admin(user: User = Depends(require_auth)) -> User:
    if (getattr(user, "role", "") or "").lower() != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return user

# Admin router for affiliates domain
admin_router = APIRouter(prefix="/api/v1/admin", tags=["admin-affiliates"]) 

@admin_router.get("/affiliates/pending", response_model=AdminApplicationListResponse)
def admin_list_pending_affiliates(admin: User = Depends(require_admin), session: Session = Depends(get_session)):
    rows = session.query(AffiliateApplication).filter_by(status="pending").order_by(AffiliateApplication.created_at.desc()).all()
    items = [
        AdminApplicationItem(
            id=r.id,
            user_id=r.user_id,
            company_name=r.company_name,
            bio=r.bio,
            why_join=r.why_join,
            status=r.status,
            created_at=r.created_at,
        )
        for r in rows
    ]
    return AdminApplicationListResponse(items=items)

@admin_router.post("/affiliates/{application_id}/approve", response_model=ApplicationStatusResponse)
def admin_approve_affiliate(application_id: int, payload: ApplicationReviewRequest, admin: User = Depends(require_admin), session: Session = Depends(get_session)):
    app_row = session.query(AffiliateApplication).filter_by(id=application_id).first()
    if not app_row:
        raise HTTPException(status_code=404, detail="Application not found")
    app_row.status = "approved"
    app_row.review_notes = payload.review_notes
    # Mark profile approved
    profile = session.query(AffiliateProfile).filter_by(user_id=app_row.user_id).first()
    if not profile:
        profile = AffiliateProfile(user_id=app_row.user_id, code=f"AFF{app_row.user_id}", approved=True)
        session.add(profile)
    else:
        profile.approved = True
    session.flush()
    return ApplicationStatusResponse(status=app_row.status, review_notes=app_row.review_notes, application_id=app_row.id)

@admin_router.post("/affiliates/{application_id}/reject", response_model=ApplicationStatusResponse)
def admin_reject_affiliate(application_id: int, payload: ApplicationReviewRequest, admin: User = Depends(require_admin), session: Session = Depends(get_session)):
    app_row = session.query(AffiliateApplication).filter_by(id=application_id).first()
    if not app_row:
        raise HTTPException(status_code=404, detail="Application not found")
    app_row.status = "rejected"
    app_row.review_notes = payload.review_notes
    session.flush()
    return ApplicationStatusResponse(status=app_row.status, review_notes=app_row.review_notes, application_id=app_row.id)

@admin_router.get("/commissions/pending", response_model=CommissionListResponse)
def admin_list_pending_commissions(page: int = 1, limit: int = 20, admin: User = Depends(require_admin), session: Session = Depends(get_session)):
    q = session.query(Commission).filter_by(status="pending_approval").order_by(Commission.created_at.desc())
    rows = q.offset((page - 1) * limit).limit(limit).all()
    items = [
        CommissionItem(
            id=str(c.id),
            advisor_user_id=c.advisor_user_id,
            transaction_type=c.transaction_type,
            subscription_tier=c.subscription_tier,
            gross_amount=c.gross_amount or 0.0,
            net_amount=c.net_amount or 0.0,
            commission_rate=c.commission_rate or 0.0,
            commission_amount=c.commission_amount or 0.0,
            status=c.status,
            payout_status=c.payout_status,
            created_at=c.created_at.isoformat() if c.created_at else None,
        )
        for c in rows
    ]
    return CommissionListResponse(commissions=items, page=page, limit=limit)

@admin_router.post("/commission/{commission_id}/approve")
def admin_approve_commission(commission_id: int, payload: AdminCommissionApproveRequest, admin: User = Depends(require_admin), session: Session = Depends(get_session)):
    c = session.query(Commission).filter_by(id=commission_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Commission not found")
    # If modified values provided, mark modified_approved
    if payload.commission_rate is not None:
        c.commission_rate = payload.commission_rate
    if payload.commission_amount is not None:
        c.commission_amount = payload.commission_amount
    c.status = "modified_approved" if (payload.commission_rate is not None or payload.commission_amount is not None) else "approved"
    session.flush()
    return {"commission_id": commission_id, "status": c.status}

@admin_router.post("/commission/{commission_id}/reject")
def admin_reject_commission(commission_id: int, admin: User = Depends(require_admin), session: Session = Depends(get_session)):
    c = session.query(Commission).filter_by(id=commission_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Commission not found")
    c.status = "rejected"
    session.flush()
    return {"commission_id": commission_id, "status": c.status}

@admin_router.get("/payouts/pending", response_model=PayoutListResponse)
def admin_list_pending_payouts(admin: User = Depends(require_admin), session: Session = Depends(get_session)):
    rows = session.query(Payout).filter_by(processed_at=None).order_by(Payout.created_at.desc()).all()
    items = [
        PayoutItem(
            id=str(p.id),
            amount=p.amount or 0.0,
            payment_method=p.payment_method,
            transaction_id=p.transaction_id,
            processed_at=p.processed_at.isoformat() if p.processed_at else None,
        )
        for p in rows
    ]
    return PayoutListResponse(payouts=items)

@admin_router.post("/payouts/{payout_id}/mark-paid")
def admin_mark_payout_paid(payout_id: int, payload: AdminPayoutMarkPaidRequest, admin: User = Depends(require_admin), session: Session = Depends(get_session)):
    p = session.query(Payout).filter_by(id=payout_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Payout not found")
    p.transaction_id = payload.transaction_id
    p.processed_at = datetime.utcnow()
    # Also mark related commissions as paid
    session.query(Commission).filter_by(payout_id=payout_id).update({Commission.payout_status: "paid"})
    session.flush()
    return {"payout_id": payout_id, "processed_at": p.processed_at.isoformat(), "transaction_id": p.transaction_id}

# Include admin router
app.include_router(admin_router)