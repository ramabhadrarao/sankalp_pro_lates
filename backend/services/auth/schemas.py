from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    mobile: Optional[str] = None
    organization: Optional[str] = None
    role: Optional[str] = None
    tier: Optional[str] = "Starter"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    mobile: Optional[str]
    organization: Optional[str]
    role: Optional[str]
    tier: str
    verified: bool