from pydantic import BaseModel, EmailStr
from typing import Optional, List

class RegisterRequest(BaseModel):
    user_type: Optional[str] = "advisor"
    name: str
    email: EmailStr
    password: str
    mobile: Optional[str] = None
    organization: Optional[str] = None
    role: Optional[str] = None
    city: Optional[str] = None
    tier: Optional[str] = "Starter"
    terms_accepted: bool = False

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: Optional[dict] = None

class EmailTokenRequest(BaseModel):
    token: str

class EmailResendRequest(BaseModel):
    email: EmailStr

class RefreshRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class MfaVerifyRequest(BaseModel):
    code: str

class MfaSetupResponse(BaseModel):
    qr_code_url: str
    secret: str
    backup_codes: List[str]

class UserResponse(BaseModel):
    id: int
    user_type: str
    name: str
    email: EmailStr
    mobile: Optional[str]
    organization: Optional[str]
    role: Optional[str]
    city: Optional[str]
    tier: str
    verified: bool
    mfa_enabled: bool