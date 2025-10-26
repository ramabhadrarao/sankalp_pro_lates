from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SubscriptionStatusResponse(BaseModel):
    tier: str
    renewal_enabled: bool
    trial_active: bool
    trial_expires_at: Optional[datetime]
    reports_used: int
    monthly_limit: int
    reports_remaining: int

class ChangeTierRequest(BaseModel):
    new_tier: str

class TrialStartResponse(BaseModel):
    trial_active: bool
    trial_expires_at: datetime

class RenewalUpdateRequest(BaseModel):
    enabled: bool

class ReportLimitsResponse(BaseModel):
    tier: str
    monthly_limit: int
    reports_used: int
    reports_remaining: int

class AdminTierUpdateRequest(BaseModel):
    tier: str
    renewal_enabled: Optional[bool] = None

class TierItem(BaseModel):
    tier_name: str
    price: int
    features: list[str]

class TierDetailResponse(BaseModel):
    tier_name: str
    price: int
    features: list[str]

class SubscribeResponse(BaseModel):
    subscription_id: int
    payment_url: str

class TrialStatusResponse(BaseModel):
    status: bool
    reports_used: int
    expires_at: Optional[datetime]

class CheckLimitResponse(BaseModel):
    can_generate: bool
    remaining: int

class DeductResponse(BaseModel):
    remaining_reports: int

class FormsSelectionResponse(BaseModel):
    selected_forms: list[int]

class AvailableFormsResponse(BaseModel):
    available_forms: list[int]

class AnalyticsAdminResponse(BaseModel):
    stats: dict