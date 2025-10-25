from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text
from datetime import datetime

from common.db.mysql import Base

class PaymentOrder(Base):
    __tablename__ = "payment_orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    subscription_id = Column(Integer, nullable=True)
    tier_id = Column(String(50), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    gateway = Column(String(20), default="razorpay")
    status = Column(String(20), default="created")  # created|processing|paid|failed|expired|cancelled
    payment_url = Column(Text, nullable=True)
    order_ref = Column(String(100), nullable=True)  # gateway order id
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    order_id = Column(Integer, ForeignKey("payment_orders.id"), nullable=True)
    gateway = Column(String(20), default="razorpay")
    payment_id = Column(String(100), index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    status = Column(String(20), default="success")  # success|failed|refunded
    signature = Column(String(255), nullable=True)
    transaction_id = Column(String(100), nullable=True)
    invoice_path = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class RefundRequest(Base):
    __tablename__ = "refund_requests"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(String(20), default="requested")  # requested|eligible|approved|rejected|processed
    gateway_refund_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)