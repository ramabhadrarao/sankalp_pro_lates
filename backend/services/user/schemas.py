from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class ProfileResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    mobile: Optional[str] = None
    organization: Optional[str] = None
    role: Optional[str] = None
    tier: Optional[str] = None
    verified: bool
    user_type: Optional[str] = None
    city: Optional[str] = None
    terms_accepted: bool
    mfa_enabled: bool
    active: bool
    photo_path: Optional[str] = None
    logo_path: Optional[str] = None
    locked_fields_after: Optional[datetime] = None

class UpdateProfileRequest(BaseModel):
    mobile: Optional[str] = None
    email: Optional[EmailStr] = None

class UploadType(BaseModel):
    type: str = Field(pattern=r"^(photo|logo)$")

class GraceStatusResponse(BaseModel):
    in_grace_period: bool
    expires_at: Optional[datetime] = None
    seconds_remaining: int

class ProfileLockResponse(BaseModel):
    locked: bool
    locked_at: datetime

class CriticalUpdateRequest(BaseModel):
    field_name: str
    new_value: str
    reason: Optional[str] = None

class CriticalUpdateItem(BaseModel):
    id: int
    field_name: str
    new_value: str
    reason: Optional[str]
    status: str
    created_at: datetime

class ActivityItem(BaseModel):
    id: int
    action: str
    meta: Optional[str]
    created_at: datetime

class DashboardStatsResponse(BaseModel):
    reports_generated: int
    reports_remaining: int
    subscription_tier: Optional[str]

class UserSearchItem(BaseModel):
    id: int
    name: str
    email: EmailStr
    mobile: Optional[str]
    active: bool
    verified: bool

class ReferralInfoResponse(BaseModel):
    referred_by: Optional[str]
    referral_link: str