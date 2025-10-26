from typing import List, Optional
from pydantic import BaseModel

class LanguageItem(BaseModel):
    code: str
    name: str
    enabled: bool
    is_default: bool

class LanguagesResponse(BaseModel):
    languages: List[LanguageItem]

class LanguageUpdateRequest(BaseModel):
    name: Optional[str] = None
    enabled: Optional[bool] = None
    is_default: Optional[bool] = None

class TranslateRequest(BaseModel):
    text: str
    target_language: str

class TranslateResponse(BaseModel):
    text: str
    language: str

class StringResponse(BaseModel):
    key: str
    language: str
    text: str

class UpsertTranslationRequest(BaseModel):
    key: str
    language: str
    text: str

class LanguageCreateRequest(BaseModel):
    code: str
    name: str
    enabled: bool = True
    is_default: bool = False

class TranslationListItem(BaseModel):
    key: str
    language: str
    text: str

class TranslationListResponse(BaseModel):
    strings: List[TranslationListItem]