from typing import Optional, List, Dict
from pydantic import BaseModel

class SendEmailRequest(BaseModel):
    to: str
    template_key: Optional[str] = None
    variables: Optional[Dict[str, str]] = None
    language: Optional[str] = "en"
    subject: Optional[str] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None

class SendSMSRequest(BaseModel):
    to: str
    message: str
    language: Optional[str] = "en"

class SendResponse(BaseModel):
    sent: bool
    notification_id: int

class TemplateItem(BaseModel):
    key: str
    type: str
    language: str
    subject: Optional[str] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None

class TemplatesResponse(BaseModel):
    templates: List[TemplateItem]

class TemplateUpdateRequest(BaseModel):
    subject: Optional[str] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None

# NEW: create template request
class TemplateCreateRequest(BaseModel):
    key: str
    type: str
    language: str = "en"
    subject: Optional[str] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None

class TestEmailRequest(BaseModel):
    template_key: str
    test_email: str
    variables: Optional[Dict[str, str]] = None

class QueueItem(BaseModel):
    id: int
    type: str
    status: str
    to: Optional[str] = None
    subject: Optional[str] = None
    created_at: str

class QueueResponse(BaseModel):
    queue: List[QueueItem]

class NotificationItem(BaseModel):
    id: int
    type: str
    subject: Optional[str] = None
    body_text: Optional[str] = None
    language: str
    read: bool
    created_at: str

class MyNotificationsResponse(BaseModel):
    notifications: List[NotificationItem]

class PreferencesResponse(BaseModel):
    email_enabled: bool
    sms_enabled: bool

class PreferencesUpdateRequest(BaseModel):
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None