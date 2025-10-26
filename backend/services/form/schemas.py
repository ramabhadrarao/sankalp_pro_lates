from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# 22+ supported elements (extendable)
FormElementType = str  # accept any string, validated at runtime

class FormField(BaseModel):
    id: str
    name: str
    label: str
    type: FormElementType
    required: bool = False
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    default_value: Optional[Any] = None
    options: Optional[List[Any]] = None  # for select, radio, checkbox
    validation: Optional[Dict[str, Any]] = None  # min, max, pattern, length, etc.
    condition: Optional[str] = None  # expression to show/hide field based on other values
    formula: Optional[str] = None  # calculation expression, references other fields
    dependencies: Optional[List[str]] = None  # field names this depends on

class FormSection(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    fields: List[FormField] = Field(default_factory=list)

class FormTemplate(BaseModel):
    id: Optional[str] = None
    key: str
    title: str
    description: Optional[str] = None
    sections: List[FormSection]
    is_custom: bool = False
    version: int = 1
    created_by: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# Requests/Responses

class CreateTemplateRequest(BaseModel):
    key: str
    title: str
    description: Optional[str] = None
    sections: List[FormSection]
    is_custom: bool = False

class UpdateTemplateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    sections: Optional[List[FormSection]] = None
    is_custom: Optional[bool] = None
    version: Optional[int] = None

class TemplateItem(BaseModel):
    id: str
    key: str
    title: str
    is_custom: bool
    version: int

class TemplatesResponse(BaseModel):
    items: List[TemplateItem]

class TemplateDetailResponse(BaseModel):
    template: FormTemplate

class SchemaResponse(BaseModel):
    template: FormTemplate

class SubmissionRequest(BaseModel):
    template_key: Optional[str] = None
    template_id: Optional[str] = None
    data: Dict[str, Any]
    draft: bool = False

class SubmissionResponse(BaseModel):
    id: str
    template_key: Optional[str] = None
    template_id: Optional[str] = None
    data: Dict[str, Any]
    errors: Optional[List[Dict[str, Any]]] = None

class SubmissionItem(BaseModel):
    id: str
    template_key: Optional[str] = None
    template_id: Optional[str] = None
    title: Optional[str] = None
    created_at: str

class SubmissionsResponse(BaseModel):
    items: List[SubmissionItem]

class DraftRequest(BaseModel):
    template_key: Optional[str] = None
    template_id: Optional[str] = None
    data: Dict[str, Any]

class DraftItem(BaseModel):
    id: str
    template_key: Optional[str] = None
    template_id: Optional[str] = None
    title: Optional[str] = None
    updated_at: str

class DraftsResponse(BaseModel):
    items: List[DraftItem]