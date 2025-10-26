from pydantic import BaseModel
from typing import List, Optional, Dict

class GenerateReportRequest(BaseModel):
    report_type: str
    parameters: Dict[str, str] = {}

class GenerateReportResponse(BaseModel):
    report_id: str
    pdf_url: str

class ReportItem(BaseModel):
    report_id: str
    report_type: str
    created_at: str
    status: str

class ReportDetailResponse(BaseModel):
    report_id: str
    report_type: str
    data: Dict[str, str]
    created_at: str
    status: str

class ShareReportRequest(BaseModel):
    emails: List[str]
    message: Optional[str] = None

class ShareReportResponse(BaseModel):
    shared: bool
    recipients: List[str]

class TemplatesResponse(BaseModel):
    templates: List[str]

class PreviewReportRequest(BaseModel):
    report_type: str
    parameters: Dict[str, str]

class PreviewReportResponse(BaseModel):
    summary: str
    charts_data: Dict[str, List[float]]

class ReportStatisticsResponse(BaseModel):
    total_reports: int
    reports_generated_today: int
    reports_remaining: int

class BulkDeleteRequest(BaseModel):
    report_ids: List[str]

class BulkDeleteResponse(BaseModel):
    deleted_count: int