from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import pyotp

from common.db.mysql import Base, engine, get_session
from common.security.jwt import create_access_token, decode_token, TokenError
from common.i18n import get_locale, t

from services.auth.schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    EmailTokenRequest,
    EmailResendRequest,
    RefreshRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest,
    ChangePasswordRequest,
    MfaVerifyRequest,
    MfaSetupResponse,
)
from services.auth.repository import (
    get_user_by_email,
    get_user_by_id,
    create_user,
    verify_password,
    create_refresh_token,
    revoke_refresh_tokens_for_user,
    get_valid_refresh_token,
    create_verification_token,
    mark_verification_used,
    create_password_reset_token,
    consume_password_reset_token,
    change_password,
)

app = FastAPI(title="SalahkaarPro Auth Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:8000",
        "http://localhost:8001",
        "http://localhost:8081",
        "null"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api/v1")

# Create tables on startup
Base.metadata.create_all(bind=engine)

@router.get("/health")
def health(request: Request):
    locale = get_locale(request)
    return {"status": "ok", "message": t(locale, "health_ok", "OK")}

# Helpers

def as_user_response(user) -> UserResponse:
    return UserResponse(
        id=user.id,
        user_type=user.user_type,
        name=user.name,
        email=user.email,
        mobile=user.mobile,
        organization=user.organization,
        role=user.role,
        city=user.city,
        tier=user.tier,
        verified=user.verified,
        mfa_enabled=user.mfa_enabled,
    )

# Auth endpoints

@router.post("/auth/register")
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_session)):
    locale = get_locale(request)
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail=t(locale, "email_exists", "Email exists"))

    user = create_user(
        db,
        user_type=payload.user_type or "advisor",
        name=payload.name,
        email=payload.email,
        password=payload.password,
        mobile=payload.mobile,
        organization=payload.organization,
        role=payload.role,
        city=payload.city,
        tier=payload.tier or "Starter",
        terms_accepted=payload.terms_accepted,
    )
    v = create_verification_token(db, user.id)
    return {"user_id": str(user.id), "email": user.email, "verification_sent": True, "token": v.token}

@router.post("/auth/verify-email")
def verify_email(payload: EmailTokenRequest, request: Request, db: Session = Depends(get_session)):
    user = mark_verification_used(db, payload.token)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")
    return {"email": user.email, "is_verified": True}

@router.post("/auth/resend-verification")
def resend_verification(payload: EmailResendRequest, request: Request, db: Session = Depends(get_session)):
    user = get_user_by_email(db, payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    v = create_verification_token(db, user.id)
    return {"message": "Verification email resent", "token": v.token}

@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_session)):
    locale = get_locale(request)
    user = get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail=t(locale, "invalid_credentials", "Invalid credentials"))
    # MFA check (if enabled, the client should separately call /mfa/verify)
    token = create_access_token({"sub": str(user.id), "email": user.email, "tier": user.tier})
    rt = create_refresh_token(db, user.id)
    return TokenResponse(access_token=token, refresh_token=rt.token, user=as_user_response(user).model_dump())

# Dependency to get current user from token

def get_current_user(request: Request, db: Session = Depends(get_session)) -> UserResponse:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth.split(" ", 1)[1]
    try:
        data = decode_token(token)
    except TokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user_by_email(db, data.get("email"))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return as_user_response(user)

@router.post("/auth/logout")
def logout(current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_session)):
    revoke_refresh_tokens_for_user(db, current_user.id)
    return {"message": "Logged out"}

@router.post("/auth/refresh")
def refresh(payload: RefreshRequest, db: Session = Depends(get_session)):
    rt = get_valid_refresh_token(db, payload.refresh_token)
    if not rt:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = get_user_by_id(db, rt.user_id)
    token = create_access_token({"sub": str(user.id), "email": user.email, "tier": user.tier})
    return {"access_token": token, "expires_in": 60 * 60}

@router.post("/auth/password-reset/request")
def password_reset_request(payload: PasswordResetRequest, db: Session = Depends(get_session)):
    user = get_user_by_email(db, payload.email)
    if not user:
        # For security, do not reveal user existence
        return {"message": "If the email exists, a reset link is sent"}
    pr = create_password_reset_token(db, user.id)
    return {"message": "Password reset email sent", "token": pr.token}

@router.post("/auth/password-reset/confirm")
def password_reset_confirm(payload: PasswordResetConfirmRequest, db: Session = Depends(get_session)):
    ok = consume_password_reset_token(db, payload.token, payload.new_password)
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid or used token")
    return {"message": "Password updated"}

@router.post("/auth/change-password")
def change_password_endpoint(payload: ChangePasswordRequest, current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_session)):
    ok = change_password(db, current_user.id, payload.old_password, payload.new_password)
    if not ok:
        raise HTTPException(status_code=400, detail="Old password incorrect")
    return {"message": "Password changed"}

# MFA endpoints

def require_admin(user: UserResponse):
    if (user.role or "").lower() != "admin" and user.user_type != "admin":
        raise HTTPException(status_code=403, detail="Admin required")

@router.post("/auth/mfa/setup", response_model=MfaSetupResponse)
def mfa_setup(current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_session)):
    # Admin only per spec
    require_admin(current_user)
    # generate secret
    secret = pyotp.random_base32()
    # Save secret; do not enable until verified
    # direct fetch real user
    from services.auth.models import User
    user = db.get(User, current_user.id)
    user.mfa_secret = secret
    db.commit()
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=current_user.email, issuer_name="SalahkaarPro")
    backup_codes = ["".join([str(i), token]) for i, token in enumerate(["A1B2C3", "D4E5F6", "G7H8I9", "J1K2L3", "M4N5O6"]) ]
    return MfaSetupResponse(qr_code_url=uri, secret=secret, backup_codes=backup_codes)

@router.post("/auth/mfa/verify")
def mfa_verify(payload: MfaVerifyRequest, current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_session)):
    from services.auth.models import User
    user = db.get(User, current_user.id)
    if not user.mfa_secret:
        raise HTTPException(status_code=400, detail="MFA not setup")
    totp = pyotp.TOTP(user.mfa_secret)
    if not totp.verify(payload.code):
        raise HTTPException(status_code=400, detail="Invalid code")
    user.mfa_enabled = True
    db.commit()
    return {"mfa_verified": True}

@router.post("/auth/mfa/disable")
def mfa_disable(payload: MfaVerifyRequest, current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_session)):
    require_admin(current_user)
    from services.auth.models import User
    user = db.get(User, current_user.id)
    user.mfa_enabled = False
    user.mfa_secret = None
    db.commit()
    return {"message": "MFA disabled"}

@router.get("/auth/me", response_model=UserResponse)
def me(current_user: UserResponse = Depends(get_current_user)):
    return current_user

@router.get("/auth/check-email")
def check_email(email: str, db: Session = Depends(get_session)):
    exists = get_user_by_email(db, email) is not None
    return {"exists": exists}

app.include_router(router)