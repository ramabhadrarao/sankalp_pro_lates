from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select

from common.db.mysql import get_session, Base, engine
from common.security.jwt import decode_token

from services.auth.models import User
from .models import Language, Translation
from .schemas import (
    LanguageItem,
    LanguagesResponse,
    LanguageUpdateRequest,
    TranslateRequest,
    TranslateResponse,
    StringResponse,
    UpsertTranslationRequest,
    LanguageCreateRequest,
    TranslationListItem,
    TranslationListResponse,
)

app = FastAPI(title="I18N Service", version="1.0.0")
router = APIRouter(prefix="/api/v1")

Base.metadata.create_all(bind=engine)

# Auth dependencies

def require_auth(authorization: str = Header(None)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    user = User(id=payload.get("sub"), email=payload.get("email"), role=payload.get("role", "user"))
    return user


def require_admin(user: User = Depends(require_auth)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


@app.get("/health")
async def health():
    return {"status": "ok", "service": "i18n"}

# 200: List supported languages
@router.get("/i18n/languages", response_model=LanguagesResponse)
def list_languages(db: Session = Depends(get_session)):
    rows = db.scalars(select(Language)).all()
    items = [LanguageItem(code=r.code, name=r.name, enabled=r.enabled, is_default=r.is_default) for r in rows]
    return LanguagesResponse(languages=items)

# 201: Get language
@router.get("/i18n/languages/{code}", response_model=LanguageItem)
def get_language(code: str, db: Session = Depends(get_session)):
    row = db.scalars(select(Language).where(Language.code == code)).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return LanguageItem(code=row.code, name=row.name, enabled=row.enabled, is_default=row.is_default)

# 202: Update language (admin)
@router.put("/i18n/languages/{code}", response_model=LanguageItem)
def update_language(code: str, req: LanguageUpdateRequest, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    row = db.scalars(select(Language).where(Language.code == code)).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    if req.name is not None:
        row.name = req.name
    if req.enabled is not None:
        row.enabled = req.enabled
    if req.is_default is not None:
        # ensure only one default
        if req.is_default:
            all_rows = db.scalars(select(Language)).all()
            for r in all_rows:
                r.is_default = False
        row.is_default = req.is_default
    db.commit()
    return LanguageItem(code=row.code, name=row.name, enabled=row.enabled, is_default=row.is_default)

# 203: Translate basic (stub)
@router.post("/i18n/translate", response_model=TranslateResponse)
def translate(req: TranslateRequest, db: Session = Depends(get_session)):
    lang = db.scalars(select(Language).where(Language.code == req.target_language, Language.enabled == True)).first()
    if not lang:
        raise HTTPException(status_code=400, detail="Unsupported language")
    # Stub: return same text, real implementation would integrate a translator
    return TranslateResponse(text=req.text, language=req.target_language)

# 204: Get string translation
@router.get("/i18n/strings/{key}", response_model=StringResponse)
def get_string(key: str, lang: str, db: Session = Depends(get_session)):
    row = db.scalars(select(Translation).where(Translation.key == key, Translation.language_code == lang)).first()
    if not row:
        # fallback to default language
        default_lang = db.scalars(select(Language).where(Language.is_default == True)).first()
        if default_lang:
            row = db.scalars(select(Translation).where(Translation.key == key, Translation.language_code == default_lang.code)).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return StringResponse(key=key, language=row.language_code, text=row.text)

# 205: Upsert string (admin)
@router.post("/i18n/strings")
def upsert_string(req: UpsertTranslationRequest, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    row = db.scalars(select(Translation).where(Translation.key == req.key, Translation.language_code == req.language)).first()
    if row:
        row.text = req.text
    else:
        row = Translation(key=req.key, language_code=req.language, text=req.text)
        db.add(row)
    db.commit()
    return {"ok": True}

# NEW: Create language
@router.post("/i18n/languages", response_model=LanguageItem)
def create_language(req: LanguageCreateRequest, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    if db.scalars(select(Language).where(Language.code == req.code)).first():
        raise HTTPException(status_code=400, detail="Language exists")
    if req.is_default:
        # Clear other defaults
        for r in db.scalars(select(Language)).all():
            r.is_default = False
    row = Language(code=req.code, name=req.name, enabled=req.enabled, is_default=req.is_default)
    db.add(row)
    db.commit()
    return LanguageItem(code=row.code, name=row.name, enabled=row.enabled, is_default=row.is_default)

# NEW: Delete language
@router.delete("/i18n/languages/{code}")
def delete_language(code: str, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    row = db.scalars(select(Language).where(Language.code == code)).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()
    return {"deleted": True}

# NEW: Default language
@router.get("/i18n/default-language", response_model=LanguageItem)
def default_language(db: Session = Depends(get_session)):
    row = db.scalars(select(Language).where(Language.is_default == True)).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not set")
    return LanguageItem(code=row.code, name=row.name, enabled=row.enabled, is_default=row.is_default)

# NEW: List strings
@router.get("/i18n/strings", response_model=TranslationListResponse)
def list_strings(language: str, prefix: str | None = None, db: Session = Depends(get_session)):
    stmt = select(Translation).where(Translation.language_code == language)
    if prefix:
        stmt = stmt.where(Translation.key.like(f"{prefix}%"))
    rows = db.scalars(stmt).all()
    return TranslationListResponse(strings=[TranslationListItem(key=r.key, language=r.language_code, text=r.text) for r in rows])

# NEW: Delete string
@router.delete("/i18n/strings/{key}")
def delete_string(key: str, lang: str, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    row = db.scalars(select(Translation).where(Translation.key == key, Translation.language_code == lang)).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()
    return {"deleted": True}

app.include_router(router)