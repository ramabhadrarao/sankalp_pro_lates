from fastapi import FastAPI, APIRouter, Header, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
from datetime import datetime
import io

from common.security.jwt import decode_token

from .schemas import (
    GenerateReportRequest, GenerateReportResponse,
    ReportItem, ReportDetailResponse,
    ShareReportRequest, ShareReportResponse,
    TemplatesResponse,
    PreviewReportRequest, PreviewReportResponse,
    ReportStatisticsResponse,
    BulkDeleteRequest, BulkDeleteResponse,
)

app = FastAPI(title="Report Service", version="1.0.0")
router = APIRouter(prefix="/api/v1")


def require_auth(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


def require_admin(user_payload: dict):
    role = (user_payload.get("role") or "").lower()
    if role != "admin":
        # Allow tier in future; here simple check
        raise HTTPException(status_code=403, detail="Admin required")

@router.get("/health")
def health():
    return {"status": "ok", "service": "report"}

# 80: Generate report
@router.post("/reports/generate", response_model=GenerateReportResponse)
def generate_report(req: GenerateReportRequest, user= require_auth):
    rid = f"RPT-{int(datetime.utcnow().timestamp())}"
    url = f"https://cdn.salahkaarpro.com/reports/{rid}.pdf"
    return GenerateReportResponse(report_id=rid, pdf_url=url)

# 81: My reports
@router.get("/reports/my-reports", response_model=List[ReportItem])
def my_reports(page: int = 1, limit: int = 20, user= require_auth):
    # Stub: return empty list
    return []

# 82: Report detail
@router.get("/reports/{report_id}", response_model=ReportDetailResponse)
def report_detail(report_id: str, user= require_auth):
    return ReportDetailResponse(
        report_id=report_id,
        report_type="financial_plan",
        data={"summary": "Demo report"},
        created_at=datetime.utcnow().isoformat(),
        status="ready",
    )

# 83: Download report
@router.get("/reports/{report_id}/download")
def download_report(report_id: str, user= require_auth):
    # Stub pdf content
    buf = io.BytesIO()
    buf.write(b"%PDF-1.4\n% Demo PDF for report \n")
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={report_id}.pdf"})

# 84: Delete report
@router.delete("/reports/{report_id}")
def delete_report(report_id: str, user= require_auth):
    return {"deleted": True, "report_id": report_id}

# 85: Share report
@router.post("/reports/{report_id}/share", response_model=ShareReportResponse)
def share_report(report_id: str, payload: ShareReportRequest, user= require_auth):
    return ShareReportResponse(shared=True, recipients=payload.emails)

# NEW: Revoke share
@router.delete("/reports/{report_id}/share")
def revoke_share(report_id: str, user= require_auth):
    return {"revoked": True, "report_id": report_id}

# NEW: List shared recipients
@router.get("/reports/{report_id}/shared", response_model=SharedListResponse)
def list_shared(report_id: str, user= require_auth):
    # Stub: return empty list since no persistence
    return SharedListResponse(recipients=[])

# 86: Templates (admin)
@router.get("/reports/templates", response_model=TemplatesResponse)
def list_templates(user= require_auth):
    require_admin(user)
    return TemplatesResponse(templates=["financial_plan", "insurance_needs", "retirement_plan"])

# 87: Preview report
@router.post("/reports/preview", response_model=PreviewReportResponse)
def preview_report(req: PreviewReportRequest, user= require_auth):
    charts = {"growth": [100, 120, 140, 165, 190]}
    return PreviewReportResponse(summary=f"Preview of {req.report_type}", charts_data=charts)

# NEW: Duplicate report
@router.post("/reports/{report_id}/duplicate", response_model=DuplicateReportResponse)
def duplicate_report(report_id: str, user= require_auth):
    new_id = f"RPT-{int(datetime.utcnow().timestamp())}-copy"
    url = f"https://cdn.salahkaarpro.com/reports/{new_id}.pdf"
    return DuplicateReportResponse(report_id=new_id, pdf_url=url)

# NEW: Email report
@router.post("/reports/{report_id}/email", response_model=EmailReportResponse)
def email_report(report_id: str, req: EmailReportRequest, user= require_auth):
    # Stub email sending
    return EmailReportResponse(sent=True, recipients=req.emails)

# 88: Statistics
@router.get("/reports/statistics", response_model=ReportStatisticsResponse)
def stats(user= require_auth):
    return ReportStatisticsResponse(total_reports=0, reports_generated_today=0, reports_remaining=0)

# 89: Bulk delete (admin)
@router.post("/reports/bulk-delete", response_model=BulkDeleteResponse)
def bulk_delete(req: BulkDeleteRequest, user= require_auth):
    require_admin(user)
    return BulkDeleteResponse(deleted_count=len(req.report_ids))

app.include_router(router)