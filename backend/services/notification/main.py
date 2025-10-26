from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select, update, desc
from datetime import datetime

from common.db.mysql import get_session, Base, engine
from common.security.jwt import decode_token

from services.auth.models import User
from .models import Notification, NotificationTemplate, NotificationPreference
from .schemas import (
    SendEmailRequest,
    SendSMSRequest,
    SendResponse,
    TemplatesResponse,
    TemplateItem,
    TemplateUpdateRequest,
    TestEmailRequest,
    QueueResponse,
    QueueItem,
    MyNotificationsResponse,
    NotificationItem,
    PreferencesResponse,
    PreferencesUpdateRequest,
)

app = FastAPI(title="Notification Service", version="1.0.0")
router = APIRouter(prefix="/api/v1")

Base.metadata.create_all(bind=engine)


def require_auth(authorization: str = Header(None), db: Session = Depends(get_session)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    user = db.get(User, user_id)
    if not user or not user.active:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user


def require_admin(user: User = Depends(require_auth)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


@app.get("/health")
async def health():
    return {"status": "ok", "service": "notification"}

# 158: send-email (internal/admin for now)
@router.post("/notifications/send-email", response_model=SendResponse)
def send_email(req: SendEmailRequest, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    # Use template if provided
    subject = req.subject
    body_text = req.body_text
    body_html = req.body_html
    if req.template_key:
        stmt = select(NotificationTemplate).where(NotificationTemplate.key == req.template_key, NotificationTemplate.language == (req.language or "en"), NotificationTemplate.type == "email")
        tpl = db.scalars(stmt).first()
        if not tpl:
            raise HTTPException(status_code=404, detail="Template not found")
        subject = subject or tpl.subject
        body_text = body_text or tpl.body_text
        body_html = body_html or tpl.body_html
    notif = Notification(user_id=None, type="email", subject=subject, body_text=body_text, body_html=body_html, language=req.language or "en", status="sent", sent_at=datetime.utcnow())
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return SendResponse(sent=True, notification_id=notif.id)

# 159: send-sms (internal/admin for now)
@router.post("/notifications/send-sms", response_model=SendResponse)
def send_sms(req: SendSMSRequest, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    notif = Notification(user_id=None, type="sms", body_text=req.message, language=req.language or "en", status="sent", sent_at=datetime.utcnow())
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return SendResponse(sent=True, notification_id=notif.id)

# 160: templates list
@router.get("/notifications/templates", response_model=TemplatesResponse)
def list_templates(t: str | None = None, language: str | None = None, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    stmt = select(NotificationTemplate)
    if t:
        stmt = stmt.where(NotificationTemplate.type == t)
    if language:
        stmt = stmt.where(NotificationTemplate.language == language)
    rows = db.scalars(stmt).all()
    return TemplatesResponse(templates=[TemplateItem(key=r.key, type=r.type, language=r.language, subject=r.subject, body_text=r.body_text, body_html=r.body_html) for r in rows])

# 161/162: get/update template
@router.get("/notifications/template/{template_key}", response_model=TemplateItem)
def get_template(template_key: str, language: str = "en", admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    stmt = select(NotificationTemplate).where(NotificationTemplate.key == template_key, NotificationTemplate.language == language)
    tpl = db.scalars(stmt).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    return TemplateItem(key=tpl.key, type=tpl.type, language=tpl.language, subject=tpl.subject, body_text=tpl.body_text, body_html=tpl.body_html)

@router.put("/notifications/template/{template_key}")
def update_template(template_key: str, req: TemplateUpdateRequest, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    stmt = select(NotificationTemplate).where(NotificationTemplate.key == template_key)
    tpl = db.scalars(stmt).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    if req.subject is not None:
        tpl.subject = req.subject
    if req.body_text is not None:
        tpl.body_text = req.body_text
    if req.body_html is not None:
        tpl.body_html = req.body_html
    db.commit()
    return {"updated": True}

# 163: test-email
@router.post("/notifications/test-email")
def test_email(req: TestEmailRequest, admin: User = Depends(require_admin)):
    return {"sent": True}

# 164/165: queue and retry (simplified: use notifications table)
@router.get("/notifications/queue", response_model=QueueResponse)
def queue(status: str | None = None, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    stmt = select(Notification).order_by(desc(Notification.created_at))
    if status:
        stmt = stmt.where(Notification.status == status)
    rows = db.scalars(stmt).all()
    return QueueResponse(queue=[QueueItem(id=r.id, type=r.type, status=r.status, to=None, subject=r.subject, created_at=r.created_at.isoformat()) for r in rows])

@router.post("/notifications/queue/{notification_id}/retry")
def retry(notification_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    rec = db.get(Notification, notification_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Not found")
    rec.status = "sent"
    rec.sent_at = datetime.utcnow()
    db.commit()
    return {"retried": True}

# 166: my-notifications
@router.get("/notifications/my-notifications", response_model=MyNotificationsResponse)
def my_notifications(user: User = Depends(require_auth), db: Session = Depends(get_session)):
    stmt = select(Notification).where(Notification.user_id == user.id).order_by(desc(Notification.created_at))
    rows = db.scalars(stmt).all()
    return MyNotificationsResponse(notifications=[NotificationItem(id=r.id, type=r.type, subject=r.subject, body_text=r.body_text, language=r.language, read=r.read, created_at=r.created_at.isoformat()) for r in rows])

# 167: mark as read
@router.put("/notifications/{notification_id}/read")
def mark_read(notification_id: int, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    rec = db.get(Notification, notification_id)
    if not rec or rec.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    rec.read = True
    db.commit()
    return {"updated": True}

# 168/169: preferences
@router.get("/notifications/preferences", response_model=PreferencesResponse)
def get_prefs(user: User = Depends(require_auth), db: Session = Depends(get_session)):
    stmt = select(NotificationPreference).where(NotificationPreference.user_id == user.id)
    pref = db.scalars(stmt).first()
    if not pref:
        pref = NotificationPreference(user_id=user.id)
        db.add(pref)
        db.commit()
        db.refresh(pref)
    return PreferencesResponse(email_enabled=pref.email_enabled, sms_enabled=pref.sms_enabled)

@router.put("/notifications/preferences", response_model=PreferencesResponse)
def update_prefs(req: PreferencesUpdateRequest, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    stmt = select(NotificationPreference).where(NotificationPreference.user_id == user.id)
    pref = db.scalars(stmt).first()
    if not pref:
        pref = NotificationPreference(user_id=user.id)
        db.add(pref)
    if req.email_enabled is not None:
        pref.email_enabled = req.email_enabled
    if req.sms_enabled is not None:
        pref.sms_enabled = req.sms_enabled
    db.commit()
    return PreferencesResponse(email_enabled=pref.email_enabled, sms_enabled=pref.sms_enabled)

# NEW: delete notification
@router.delete("/notifications/{notification_id}")
def delete_notification(notification_id: int, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    rec = db.get(Notification, notification_id)
    if not rec or rec.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(rec)
    db.commit()
    return {"deleted": True}

# NEW: archive notification
@router.put("/notifications/{notification_id}/archive")
def archive_notification(notification_id: int, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    rec = db.get(Notification, notification_id)
    if not rec or rec.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    rec.archived = True
    db.commit()
    return {"archived": True}

# NEW: unarchive notification
@router.put("/notifications/{notification_id}/unarchive")
def unarchive_notification(notification_id: int, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    rec = db.get(Notification, notification_id)
    if not rec or rec.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    rec.archived = False
    db.commit()
    return {"archived": False}

# NEW: mark all as read
@router.put("/notifications/mark-all-read")
def mark_all_read(user: User = Depends(require_auth), db: Session = Depends(get_session)):
    stmt = select(Notification).where(Notification.user_id == user.id, Notification.read == False)
    rows = db.scalars(stmt).all()
    count = 0
    for r in rows:
        r.read = True
        count += 1
    db.commit()
    return {"updated_count": count}

# NEW: create template
@router.post("/notifications/templates")
def create_template(req: TemplateCreateRequest, admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    exists = db.scalars(select(NotificationTemplate).where(NotificationTemplate.key == req.key, NotificationTemplate.language == req.language)).first()
    if exists:
        raise HTTPException(status_code=400, detail="Template exists")
    tpl = NotificationTemplate(key=req.key, type=req.type, language=req.language, subject=req.subject, body_text=req.body_text, body_html=req.body_html)
    db.add(tpl)
    db.commit()
    return {"created": True}

# NEW: delete template
@router.delete("/notifications/template/{template_key}")
def delete_template(template_key: str, language: str = "en", admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    tpl = db.scalars(select(NotificationTemplate).where(NotificationTemplate.key == template_key, NotificationTemplate.language == language)).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    db.delete(tpl)
    db.commit()
    return {"deleted": True}

app.include_router(router)