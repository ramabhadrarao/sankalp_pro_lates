from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from common.db.mysql import get_session, Base, engine
from common.security.jwt import decode_token

from services.auth.models import User
from .models import Payment, PaymentOrder, RefundRequest
from .schemas import (
    CreateOrderRequest,
    CreateOrderResponse,
    VerifyRequest,
    VerifyResponse,
    PaymentItem,
    PaymentDetailResponse,
    RefundRequestPayload,
    RefundRequestResponse,
    RefundEligibilityResponse,
    AdminRefundItem,
    AnalyticsResponse,
    RetryResponse,
)
from .repository import (
    create_order,
    verify_payment,
    record_webhook,
    get_payments_for_user,
    count_payments_for_user,
    get_payment_by_id,
    request_refund,
    check_refund_eligibility,
    list_refunds_admin,
    approve_refund,
    reject_refund,
    process_refund,
    get_analytics,
    get_failed_payments_admin,
    retry_failed_payment,
)

app = FastAPI(title="Payment Service", version="1.0.0")
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
    return {"status": "ok", "service": "payment"}

# 53: Create payment order
@router.post("/payments/create-order", response_model=CreateOrderResponse)
def create_payment_order(payload: CreateOrderRequest, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    order = create_order(db, user_id=user.id, amount=payload.amount, subscription_id=payload.subscription_id, tier_id=payload.tier_id, gateway=payload.gateway or "razorpay")
    return CreateOrderResponse(order_id=order.id, payment_url=order.payment_url or "")

# 54: Verify payment
@router.post("/payments/verify", response_model=VerifyResponse)
def verify(payload: VerifyRequest, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    ok, pay = verify_payment(db, payload.order_id, payload.payment_id, payload.signature)
    if not ok:
        raise HTTPException(status_code=400, detail="Verification failed")
    return VerifyResponse(verified=True, transaction_id=pay.transaction_id if pay else None)

# 55: Razorpay webhook
@router.post("/payments/webhook/razorpay")
async def webhook_razorpay(request: Request, db: Session = Depends(get_session)):
    payload = await request.json()
    record_webhook(db, "razorpay", payload)
    return {"received": True}

# 56: Stripe webhook
@router.post("/payments/webhook/stripe")
async def webhook_stripe(request: Request, db: Session = Depends(get_session)):
    payload = await request.json()
    record_webhook(db, "stripe", payload)
    return {"received": True}

# 57: My payments
@router.get("/payments/my-payments", response_model=List[PaymentItem])
def my_payments(page: int = 1, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    items = get_payments_for_user(db, user.id, page=page)
    return [
        PaymentItem(
            id=p.id,
            order_id=p.order_id,
            amount=p.amount,
            currency=p.currency,
            status=p.status,
            gateway=p.gateway,
            created_at=p.created_at,
        )
        for p in items
    ]

# 58: Payment details
@router.get("/payments/{payment_id}", response_model=PaymentDetailResponse)
def payment_detail(payment_id: int, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    p = get_payment_by_id(db, payment_id)
    if not p or p.user_id != user.id:
        raise HTTPException(status_code=404, detail="Payment not found")
    return PaymentDetailResponse(
        id=p.id,
        order_id=p.order_id,
        amount=p.amount,
        currency=p.currency,
        status=p.status,
        gateway=p.gateway,
        created_at=p.created_at,
        transaction_id=p.transaction_id,
        invoice_path=p.invoice_path,
    )

# 59: Invoice download (stubbed text stream)
@router.get("/payments/{payment_id}/invoice")
def download_invoice(payment_id: int, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    p = get_payment_by_id(db, payment_id)
    if not p or p.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    content = f"Invoice for payment #{p.id} - Amount: {p.amount} {p.currency}\nStatus: {p.status}\nGateway: {p.gateway}\n".encode()
    return StreamingResponse(iter([content]), media_type="application/pdf")

# 60: Request refund
@router.post("/payments/refund/request", response_model=RefundRequestResponse)
def refund_request(payload: RefundRequestPayload, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    rr = request_refund(db, user.id, payload.payment_id, payload.reason)
    return RefundRequestResponse(refund_request_id=rr.id)

# 61: Refund eligibility
@router.get("/payments/refund/eligibility", response_model=RefundEligibilityResponse)
def refund_eligibility(payment_id: int, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    eligible, reason = check_refund_eligibility(db, payment_id)
    if not eligible:
        return RefundEligibilityResponse(eligible=False, reason=reason)
    return RefundEligibilityResponse(eligible=True, reason=None)

# 62: Admin refunds list
@router.get("/payments/refunds", response_model=List[AdminRefundItem])
def admin_refunds(status: Optional[str] = None, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    items = list_refunds_admin(db, status)
    return [AdminRefundItem(id=i.id, user_id=i.user_id, payment_id=i.payment_id, reason=i.reason, status=i.status, created_at=i.created_at) for i in items]

# 63: Approve refund
@router.post("/payments/refund/{refund_id}/approve")
def admin_refund_approve(refund_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    rr = approve_refund(db, refund_id)
    if not rr:
        raise HTTPException(status_code=404, detail="Refund not found")
    return {"refund_id": rr.id, "status": rr.status}

# 64: Reject refund
@router.post("/payments/refund/{refund_id}/reject")
def admin_refund_reject(refund_id: int, reason: Optional[str] = None, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    rr = reject_refund(db, refund_id, reason)
    if not rr:
        raise HTTPException(status_code=404, detail="Refund not found")
    return {"refund_id": rr.id, "status": rr.status}

# 65: Process refund
@router.post("/payments/refund/{refund_id}/process")
def admin_refund_process(refund_id: int, gateway_refund_id: str, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    rr = process_refund(db, refund_id, gateway_refund_id)
    if not rr:
        raise HTTPException(status_code=404, detail="Refund not found")
    return {"refund_id": rr.id, "processed": True}

# 66: Payment analytics
@router.get("/payments/analytics", response_model=AnalyticsResponse)
def admin_analytics(frm: Optional[str] = None, to: Optional[str] = None, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    since = datetime.fromisoformat(frm) if frm else None
    until = datetime.fromisoformat(to) if to else None
    revenue, txns = get_analytics(db, since, until)
    return AnalyticsResponse(revenue=revenue, transactions=txns)

# 67: Failed payments
@router.get("/payments/failed")
def admin_failed(admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    orders = get_failed_payments_admin(db)
    return [{"order_id": o.id, "user_id": o.user_id, "amount": o.amount, "gateway": o.gateway, "status": o.status} for o in orders]

# 68: Retry failed payment
@router.post("/payments/{payment_id}/retry", response_model=RetryResponse)
def retry(payment_id: int, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    url = retry_failed_payment(db, payment_id)
    if not url:
        raise HTTPException(status_code=404, detail="Order not found")
    return RetryResponse(payment_url=url)

app.include_router(router)