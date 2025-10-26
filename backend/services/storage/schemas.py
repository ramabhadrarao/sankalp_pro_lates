from typing import Optional, List
from pydantic import BaseModel

class UploadResponse(BaseModel):
    file_id: int
    url: Optional[str] = None

class FileUrlResponse(BaseModel):
    url: str
    expires_in: int

class PresignedRequest(BaseModel):
    filename: str
    file_type: Optional[str] = None

class PresignedResponse(BaseModel):
    upload_url: str
    file_id: int

class FileItem(BaseModel):
    id: int
    filename: str
    file_type: Optional[str] = None
    url: Optional[str] = None
    created_at: str

class FilesResponse(BaseModel):
    files: List[FileItem]