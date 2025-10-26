from typing import Optional, List
from pydantic import BaseModel


class ApplyRequest(BaseModel):
    company_name: Optional[str] = None
    bio: Optional[str] = None
    why_join: Optional[str] = None


class ApplicationStatusResponse(BaseModel):
    status: str
    review_notes: Optional[str] = None
    application_id: Optional[int] = None


class LandingPageUpdateRequest(BaseModel):
    headline: Optional[str] = None
    offer: Optional[str] = None
    custom_message: Optional[str] = None
    cta_text: Optional[str] = None


class LandingPageResponse(BaseModel):
    affiliate_id: int
    name: Optional[str] = None
    photo_url: Optional[str] = None
    logo_url: Optional[str] = None
    custom_headline: Optional[str] = None
    special_offer: Optional[str] = None
    bio: Optional[str] = None
    custom_message: Optional[str] = None
    cta_text: Optional[str] = None
    landing_page_url: Optional[str] = None
    referral_link: Optional[str] = None
    qr_code: Optional[str] = None


class MyLinksResponse(BaseModel):
    referral_link: str
    landing_page_url: str
    qr_code: Optional[str] = None


class DashboardResponse(BaseModel):
    total_referrals: int
    active_advisors: int
    pending_commission: float
    approved_commission: float
    paid_commission: float
    this_month_performance: Optional[dict] = None


class ReferralItem(BaseModel):
    id: str
    advisor_user_id: Optional[int] = None
    signup_date: Optional[str] = None
    status: str


class ReferralListResponse(BaseModel):
    referrals: List[ReferralItem]
    page: int
    limit: int


class CommissionItem(BaseModel):
    id: str
    advisor_user_id: int
    transaction_type: str
    subscription_tier: Optional[str]
    gross_amount: float
    net_amount: float
    commission_rate: float
    commission_amount: float
    status: str
    payout_status: str
    created_at: Optional[str] = None


class CommissionListResponse(BaseModel):
    commissions: List[CommissionItem]
    page: int
    limit: int


class PayoutItem(BaseModel):
    id: str
    amount: float
    payment_method: Optional[str]
    transaction_id: Optional[str]
    processed_at: Optional[str]


class PayoutListResponse(BaseModel):
    payouts: List[PayoutItem]


class PerformanceResponse(BaseModel):
    conversion_rate: float
    revenue_generated: float
    over_time: Optional[List[dict]] = None


class BankAccountCreateRequest(BaseModel):
    account_holder: str
    bank_name: str
    account_number: str
    ifsc: str
    account_type: Optional[str] = None


class BankAccountItem(BaseModel):
    id: int
    account_holder: str
    bank_name: str
    account_number: str
    ifsc: str
    account_type: Optional[str] = None


class BankAccountListResponse(BaseModel):
    items: List[BankAccountItem]


class BankAccountUpdateRequest(BaseModel):
    account_holder: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc: Optional[str] = None
    account_type: Optional[str] = None


class MarketingAssetItem(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    asset_type: str  # image/banner/text
    url: str


class MarketingAssetsResponse(BaseModel):
    items: List[MarketingAssetItem]


class AdminApplicationItem(BaseModel):
    id: int
    user_id: int
    company_name: Optional[str] = None
    bio: Optional[str] = None
    why_join: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None

class AdminApplicationListResponse(BaseModel):
    items: List[AdminApplicationItem]

class ApplicationReviewRequest(BaseModel):
    review_notes: Optional[str] = None

class AdminCommissionApproveRequest(BaseModel):
    commission_rate: Optional[float] = None
    commission_amount: Optional[float] = None

class AdminPayoutMarkPaidRequest(BaseModel):
    transaction_id: str