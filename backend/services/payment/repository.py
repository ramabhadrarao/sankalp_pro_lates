from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from .models import PaymentOrder, Payment, RefundRequest

# Gateway stubs

def _make_payment_url(order: PaymentOrder) -> str:
    return f"https://pay.example.com/{order.gateway}/checkout?order_id={order.id}&amount={order.amount}&currency={order.currency}"


def create_order(db: Session, user_id: int, amount: float, subscription_id: int | None, tier_id: str | None, gateway: str = "razorpay") -> PaymentOrder:
    order = PaymentOrder(
        user_id=user_id,
        amount=amount,
        subscription_id=subscription_id,
        tier_id=tier_id,
        gateway=gateway,
        status="created",
        currency="INR",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    order.payment_url = _make_payment_url(order)
    db.commit()
    return order


def verify_payment(db: Session, order_id: int, payment_id: str, signature: str | None) -> Tuple[bool, Optional[Payment]]:
    order = db.get(PaymentOrder, order_id)
    if not order:
        return False, None
    # Simple signature stub: consider verified if provided
    verified = signature is None or len(signature) >= 10
    if verified:
        order.status = "paid"
        pay = Payment(
            user_id=order.user_id,
            order_id=order.id,
            gateway=order.gateway,
            payment_id=payment_id,
            amount=order.amount,
            currency=order.currency,
            status="success",
            signature=signature or "stub",
            transaction_id=f"TXN-{order.id}-{int(datetime.utcnow().timestamp())}",
        )
        db.add(pay)
        db.commit()
        db.refresh(pay)
        return True, pay
    else:
        order.status = "failed"
        db.commit()
        return False, None


def record_webhook(db: Session, gateway: str, payload: dict) -> bool:
    # Minimal stub: mark matching order/payment based on payload
    order_id = payload.get("order_id")
    payment_id = payload.get("payment_id")
    status = payload.get("status", "success")
    if order_id:
        order = db.get(PaymentOrder, int(order_id))
        if order:
            order.status = "paid" if status == "success" else "failed"
            db.commit()
    if payment_id and status == "success":
        pay = db.query(Payment).filter(Payment.payment_id == payment_id).first()
        if pay:
            pay.status = "success"
            db.commit()
    return True


def get_payments_for_user(db: Session, user_id: int, page: int = 1, page_size: int = 20) -> List[Payment]:
    return (
        db.query(Payment)
        .filter(Payment.user_id == user_id)
        .order_by(Payment.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )


def count_payments_for_user(db: Session, user_id: int) -> int:
    return db.query(func.count(Payment.id)).filter(Payment.user_id == user_id).scalar() or 0


def get_payment_by_id(db: Session, payment_id: int) -> Optional[Payment]:
    return db.get(Payment, payment_id)


def request_refund(db: Session, user_id: int, payment_id: int, reason: str | None) -> RefundRequest:
    rr = RefundRequest(user_id=user_id, payment_id=payment_id, reason=reason, status="requested")
    db.add(rr)
    db.commit()
    db.refresh(rr)
    return rr


def check_refund_eligibility(db: Session, payment_id: int) -> Tuple[bool, Optional[str]]:
    pay = db.get(Payment, payment_id)
    if not pay:
        return False, "Payment not found"
    if pay.status != "success":
        return False, "Only successful payments are eligible"
    if datetime.utcnow() - pay.created_at > timedelta(days=7):
        return False, "Refund window exceeded"
    return True, None


def list_refunds_admin(db: Session, status: Optional[str], page: int = 1, page_size: int = 20) -> List[RefundRequest]:
    q = db.query(RefundRequest)
    if status:
        q = q.filter(RefundRequest.status == status)
    return q.order_by(RefundRequest.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()


def approve_refund(db: Session, refund_id: int) -> Optional[RefundRequest]:
    rr = db.get(RefundRequest, refund_id)
    if not rr:
        return None
    rr.status = "approved"
    db.commit()
    db.refresh(rr)
    return rr


def reject_refund(db: Session, refund_id: int, reason: str | None) -> Optional[RefundRequest]:
    rr = db.get(RefundRequest, refund_id)
    if not rr:
        return None
    rr.status = "rejected"
    if reason:
        rr.reason = (rr.reason or "") + f"\nAdmin rejected: {reason}"
    db.commit()
    db.refresh(rr)
    return rr


def process_refund(db: Session, refund_id: int, gateway_refund_id: str) -> Optional[RefundRequest]:
    rr = db.get(RefundRequest, refund_id)
    if not rr:
        return None
    rr.status = "processed"
    rr.gateway_refund_id = gateway_refund_id
    # mark payment as refunded
    pay = db.get(Payment, rr.payment_id)
    if pay:
        pay.status = "refunded"
    db.commit()
    db.refresh(rr)
    return rr


def get_analytics(db: Session, since: Optional[datetime], until: Optional[datetime]) -> Tuple[float, int]:
    q = db.query(func.coalesce(func.sum(Payment.amount), 0.0), func.count(Payment.id)).filter(Payment.status == "success")
    if since:
        q = q.filter(Payment.created_at >= since)
    if until:
        q = q.filter(Payment.created_at <= until)
    revenue, txns = q.first()
    return float(revenue or 0.0), int(txns or 0)


def get_failed_payments_admin(db: Session) -> List[PaymentOrder]:
    return db.query(PaymentOrder).filter(PaymentOrder.status == "failed").order_by(PaymentOrder.created_at.desc()).all()


def retry_failed_payment(db: Session, payment_id: int) -> Optional[str]:
    order = db.get(PaymentOrder, payment_id)
    if not order:
        return None
    order.status = "created"
    order.payment_url = _make_payment_url(order)
    db.commit()
    return order.payment_url