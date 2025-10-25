from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CreateOrderRequest(BaseModel):
    subscription_id: Optional[int] = None
    tier_id: Optional[str] = None
    amount: float
    gateway: Optional[str] = "razorpay"

class CreateOrderResponse(BaseModel):
    order_id: int
    payment_url: str

class VerifyRequest(BaseModel):
    order_id: int
    payment_id: str
    signature: Optional[str] = None

class VerifyResponse(BaseModel):
    verified: bool
    transaction_id: Optional[str]

class PaymentItem(BaseModel):
    id: int
    order_id: Optional[int]
    amount: float
    currency: str
    status: str
    gateway: str
    created_at: datetime

class PaymentDetailResponse(BaseModel):
    id: int
    order_id: Optional[int]
    amount: float
    currency: str
    status: str
    gateway: str
    created_at: datetime
    transaction_id: Optional[str]
    invoice_path: Optional[str]

class RefundRequestPayload(BaseModel):
    payment_id: int
    reason: Optional[str] = None

class RefundRequestResponse(BaseModel):
    refund_request_id: int

class RefundEligibilityResponse(BaseModel):
    eligible: bool
    reason: Optional[str] = None

class AdminRefundItem(BaseModel):
    id: int
    user_id: int
    payment_id: int
    reason: Optional[str]
    status: str
    created_at: datetime

class AnalyticsResponse(BaseModel):
    revenue: float
    transactions: int

class RetryResponse(BaseModel):
    payment_url: str