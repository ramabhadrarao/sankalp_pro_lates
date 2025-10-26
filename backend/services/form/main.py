from fastapi import FastAPI, APIRouter, Depends, HTTPException, Header
from typing import Optional, List, Dict, Any
from datetime import datetime
import re
import ast
import operator
import math

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

from common.config import MONGO_URI, MONGO_DB
from common.security.jwt import decode_token
from common.db.mysql import get_session, Base, engine
from services.auth.models import User

from .schemas import (
    FormTemplate,
    CreateTemplateRequest,
    UpdateTemplateRequest,
    TemplatesResponse,
    TemplateItem,
    TemplateDetailResponse,
    SchemaResponse,
    SubmissionRequest,
    SubmissionResponse,
    SubmissionItem,
    SubmissionsResponse,
    DraftRequest,
    DraftItem,
    DraftsResponse,
)

app = FastAPI(title="Form Service", version="1.0.0")
router = APIRouter(prefix="/api/v1")

# Ensure SQL tables are initialized (for user lookup)
Base.metadata.create_all(bind=engine)

# Mongo setup
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[MONGO_DB]
TEMPLATES = db["form_templates"]
SUBMISSIONS = db["form_submissions"]
DRAFTS = db["form_drafts"]

# --- Auth helpers ---

def require_auth(authorization: str = Header(None), db_session=Depends(get_session)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = int(payload.get("sub"))
    user = db_session.get(User, user_id)
    if not user or not user.active:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user


def require_admin(user: User = Depends(require_auth)) -> User:
    if (user.role or "").lower() != "admin":
        raise HTTPException(status_code=403, detail="Admin required")
    return user

# --- Utility: safe expression evaluator for formulas & conditions ---
ALLOWED_FUNCS = {
    "min": min,
    "max": max,
    "round": round,
    "sum": sum,
    "abs": abs,
}
ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
ALLOWED_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _eval_node(node, variables: Dict[str, Any]):
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return variables.get(node.id, ALLOWED_FUNCS.get(node.id))
    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left, variables)
        right = _eval_node(node.right, variables)
        op = ALLOWED_BINOPS.get(type(node.op))
        if not op:
            raise ValueError("Disallowed operator")
        return op(left, right)
    if isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand, variables)
        op = ALLOWED_UNARY.get(type(node.op))
        if not op:
            raise ValueError("Disallowed unary operator")
        return op(operand)
    if isinstance(node, ast.Call):
        func = _eval_node(node.func, variables)
        if func not in ALLOWED_FUNCS.values():
            raise ValueError("Disallowed function")
        args = [_eval_node(a, variables) for a in node.args]
        return func(*args)
    if isinstance(node, ast.Compare):
        left = _eval_node(node.left, variables)
        for op, comparator in zip(node.ops, node.comparators):
            right = _eval_node(comparator, variables)
            if isinstance(op, ast.Eq):
                if not (left == right):
                    return False
            elif isinstance(op, ast.NotEq):
                if not (left != right):
                    return False
            elif isinstance(op, ast.Gt):
                if not (left > right):
                    return False
            elif isinstance(op, ast.GtE):
                if not (left >= right):
                    return False
            elif isinstance(op, ast.Lt):
                if not (left < right):
                    return False
            elif isinstance(op, ast.LtE):
                if not (left <= right):
                    return False
            else:
                raise ValueError("Disallowed comparator")
            left = right
        return True
    if isinstance(node, ast.BoolOp):
        values = [_eval_node(v, variables) for v in node.values]
        if isinstance(node.op, ast.And):
            return all(values)
        if isinstance(node.op, ast.Or):
            return any(values)
        raise ValueError("Disallowed boolean op")
    if isinstance(node, ast.IfExp):
        test = _eval_node(node.test, variables)
        return _eval_node(node.body if test else node.orelse, variables)
    raise ValueError("Disallowed expression")


def safe_eval(expr: str, variables: Dict[str, Any]) -> Any:
    tree = ast.parse(expr, mode="eval")
    return _eval_node(tree.body, variables)

# --- Validation & calculation processing ---

def _is_truthy(x):
    return bool(x)


def validate_and_compute(template: Dict[str, Any], data: Dict[str, Any]):
    errors = []
    result = dict(data)
    # Flatten fields with section context
    fields: List[Dict[str, Any]] = []
    for sec in template.get("sections", []):
        for f in sec.get("fields", []):
            fields.append(f)

    # First pass: validate required and types (consider condition)
    for f in fields:
        name = f.get("name")
        cond = f.get("condition")
        visible = True
        if cond:
            try:
                visible = _is_truthy(safe_eval(cond, result))
            except Exception:
                visible = True  # fail-open for visibility to avoid blocking
        if not visible:
            # ignore hidden field requirements
            continue
        if f.get("required") and (name not in result or result.get(name) in (None, "")):
            errors.append({"field": name, "error": "required"})
        # basic type checks
        t = (f.get("type") or "").lower()
        val = result.get(name)
        if val is None:
            continue
        if t in {"number", "integer", "currency", "percentage"}:
            try:
                result[name] = float(val)
            except Exception:
                errors.append({"field": name, "error": "must_be_number"})
        if t in {"multiselect", "checkboxes"} and not isinstance(val, list):
            errors.append({"field": name, "error": "must_be_list"})
        # pattern validation
        v = f.get("validation", {}) or {}
        pattern = v.get("pattern")
        if pattern and isinstance(val, str):
            if not re.fullmatch(pattern, val or ""):
                errors.append({"field": name, "error": "pattern_mismatch"})
        # date/month format validation
        if t == "date" and isinstance(val, str):
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}$", val):
                errors.append({"field": name, "error": "invalid_date_format"})
        if t == "month" and isinstance(val, str):
            if not re.fullmatch(r"\d{4}-\d{2}$", val):
                errors.append({"field": name, "error": "invalid_month_format"})
        # min/max
        if isinstance(val, (int, float)):
            if v.get("min") is not None and val < v["min"]:
                errors.append({"field": name, "error": "min"})
            if v.get("max") is not None and val > v["max"]:
                errors.append({"field": name, "error": "max"})

    # Second pass: compute formulas (respect condition)
    for f in fields:
        name = f.get("name")
        formula = f.get("formula")
        if formula:
            cond = f.get("condition")
            visible = True
            if cond:
                try:
                    visible = _is_truthy(safe_eval(cond, result))
                except Exception:
                    visible = True
            if not visible:
                continue
            try:
                result[name] = safe_eval(formula, result)
            except Exception:
                errors.append({"field": name, "error": "formula_error"})

    return result, errors

# --- Routes ---

@app.get("/health")
async def health():
    return {"status": "ok", "service": "form"}

# Templates
@router.get("/forms/templates", response_model=TemplatesResponse)
async def list_templates(user: User = Depends(require_auth)):
    cursor = TEMPLATES.find({}, {"_id": 1, "key": 1, "title": 1, "is_custom": 1, "version": 1})
    items = []
    async for doc in cursor:
        items.append(TemplateItem(id=str(doc["_id"]), key=doc.get("key"), title=doc.get("title"), is_custom=doc.get("is_custom", False), version=doc.get("version", 1)))
    return TemplatesResponse(items=items)

@router.post("/forms/templates", response_model=TemplateDetailResponse)
async def create_template(payload: CreateTemplateRequest, admin: User = Depends(require_admin)):
    doc = payload.model_dump()
    now = datetime.utcnow().isoformat()
    doc.update({"created_by": admin.id, "created_at": now, "updated_at": now})
    res = await TEMPLATES.insert_one(doc)
    doc["id"] = str(res.inserted_id)
    doc["_id"] = str(res.inserted_id)
    return TemplateDetailResponse(template=FormTemplate(**doc))

@router.get("/forms/templates/{template_id}", response_model=TemplateDetailResponse)
async def get_template(template_id: str, user: User = Depends(require_auth)):
    doc = await TEMPLATES.find_one({"_id": ObjectId(template_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Template not found")
    doc["id"] = str(doc["_id"])
    return TemplateDetailResponse(template=FormTemplate(**doc))

@router.put("/forms/templates/{template_id}", response_model=TemplateDetailResponse)
async def update_template(template_id: str, payload: UpdateTemplateRequest, admin: User = Depends(require_admin)):
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    updates["updated_at"] = datetime.utcnow().isoformat()
    await TEMPLATES.update_one({"_id": ObjectId(template_id)}, {"$set": updates})
    doc = await TEMPLATES.find_one({"_id": ObjectId(template_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Template not found")
    doc["id"] = str(doc["_id"])
    return TemplateDetailResponse(template=FormTemplate(**doc))

@router.delete("/forms/templates/{template_id}")
async def delete_template(template_id: str, admin: User = Depends(require_admin)):
    await TEMPLATES.delete_one({"_id": ObjectId(template_id)})
    return {"deleted": True}

# Dynamic schema by key (for custom forms)
@router.get("/forms/schema/{key}", response_model=SchemaResponse)
async def get_schema(key: str, user: User = Depends(require_auth)):
    doc = await TEMPLATES.find_one({"key": key})
    if not doc:
        raise HTTPException(status_code=404, detail="Schema not found")
    doc["id"] = str(doc["_id"])
    return SchemaResponse(template=FormTemplate(**doc))

# Submissions
@router.post("/forms/submissions", response_model=SubmissionResponse)
async def submit(payload: SubmissionRequest, user: User = Depends(require_auth)):
    # Load template by key or id
    query = None
    if payload.template_key:
        query = {"key": payload.template_key}
    elif payload.template_id:
        query = {"_id": ObjectId(payload.template_id)}
    else:
        raise HTTPException(status_code=400, detail="template_key or template_id required")
    tpl = await TEMPLATES.find_one(query)
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")

    computed, errors = validate_and_compute(tpl, payload.data)

    rec = {
        "template_key": tpl.get("key"),
        "template_id": str(tpl.get("_id")),
        "data": computed,
        "errors": errors or None,
        "user_id": user.id,
        "created_at": datetime.utcnow().isoformat(),
    }
    res = await SUBMISSIONS.insert_one(rec)
    return SubmissionResponse(id=str(res.inserted_id), template_key=rec["template_key"], template_id=rec["template_id"], data=computed, errors=errors or None)

@router.get("/forms/submissions/my", response_model=SubmissionsResponse)
async def my_submissions(page: int = 1, limit: int = 20, user: User = Depends(require_auth)):
    cursor = SUBMISSIONS.find({"user_id": user.id}).skip((page - 1) * limit).limit(limit)
    items: List[SubmissionItem] = []
    async for d in cursor:
        items.append(SubmissionItem(id=str(d["_id"]), template_key=d.get("template_key"), template_id=d.get("template_id"), title=None, created_at=d.get("created_at")))
    return SubmissionsResponse(items=items)

@router.get("/forms/submissions/{submission_id}", response_model=SubmissionResponse)
async def submission_detail(submission_id: str, user: User = Depends(require_auth)):
    d = await SUBMISSIONS.find_one({"_id": ObjectId(submission_id), "user_id": user.id})
    if not d:
        raise HTTPException(status_code=404, detail="Submission not found")
    return SubmissionResponse(id=str(d["_id"]), template_key=d.get("template_key"), template_id=d.get("template_id"), data=d.get("data", {}), errors=d.get("errors"))

# Drafts
@router.post("/forms/drafts", response_model=DraftItem)
async def save_draft(payload: DraftRequest, user: User = Depends(require_auth)):
    # Upsert by (user_id, template_key or template_id)
    key = payload.template_key or payload.template_id
    if not key:
        raise HTTPException(status_code=400, detail="template_key or template_id required")
    selector = {"user_id": user.id}
    if payload.template_key:
        selector.update({"template_key": payload.template_key})
    else:
        selector.update({"template_id": payload.template_id})
    now = datetime.utcnow().isoformat()
    update = {"$set": {"data": payload.data, "updated_at": now, **selector}}
    res = await DRAFTS.update_one(selector, update, upsert=True)
    doc = await DRAFTS.find_one(selector)
    return DraftItem(id=str(doc["_id"]), template_key=doc.get("template_key"), template_id=doc.get("template_id"), title=None, updated_at=doc.get("updated_at"))

@router.get("/forms/drafts/my", response_model=DraftsResponse)
async def my_drafts(user: User = Depends(require_auth)):
    cursor = DRAFTS.find({"user_id": user.id})
    items: List[DraftItem] = []
    async for d in cursor:
        items.append(DraftItem(id=str(d["_id"]), template_key=d.get("template_key"), template_id=d.get("template_id"), title=None, updated_at=d.get("updated_at")))
    return DraftsResponse(items=items)

app.include_router(router)

# New helper functions to support sample forms' finance and date logic

def emi(principal: float, rate_percent: float, tenure_years: float) -> float:
    r = (rate_percent or 0.0) / 12.0 / 100.0
    n = int(round((tenure_years or 0.0) * 12))
    if n <= 0:
        return 0.0
    if r == 0:
        return principal / n
    pow_ = (1 + r) ** n
    return principal * r * pow_ / (pow_ - 1)


def loan_from_emi(emi_amount: float, rate_percent: float, tenure_years: float) -> float:
    r = (rate_percent or 0.0) / 12.0 / 100.0
    n = int(round((tenure_years or 0.0) * 12))
    if n <= 0:
        return 0.0
    if r == 0:
        return emi_amount * n
    pow_ = (1 + r) ** n
    return emi_amount * (pow_ - 1) / (r * pow_)


def sip(future_value: float, annual_return_percent: float, years: float) -> float:
    r = (annual_return_percent or 0.0) / 12.0 / 100.0
    n = int(round((years or 0.0) * 12))
    if n <= 0:
        return 0.0
    if r == 0:
        return future_value / n
    pow_ = (1 + r) ** n
    return future_value * r / (pow_ - 1)


def inflation_fv(amount: float, annual_inflation_percent: float, years: float) -> float:
    rate = (annual_inflation_percent or 0.0) / 100.0
    return (amount or 0.0) * ((1 + rate) ** (years or 0.0))


from datetime import datetime
import re


def _normalize_date(v):
    if isinstance(v, datetime):
        return v
    if isinstance(v, str):
        if re.fullmatch(r"\d{4}-\d{2}$", v):
            year, month = map(int, v.split("-"))
            return datetime(year, month, 1)
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}$", v):
            y, m, d = map(int, v.split("-"))
            return datetime(y, m, d)
    return None


def months_between(start_date, end_date) -> int:
    d1 = _normalize_date(start_date)
    d2 = _normalize_date(end_date)
    if not d1 or not d2:
        return 0
    return (d2.year - d1.year) * 12 + (d2.month - d1.month)


def age(dob_str: str) -> int:
    d = _normalize_date(dob_str)
    if not d:
        return 0
    today = datetime.today()
    age_years = today.year - d.year - ((today.month, today.day) < (d.month, d.day))
    return max(age_years, 0)

# Expand allowed functions for safe evaluator
ALLOWED_FUNCS.update({
    "emi": emi,
    "loan_from_emi": loan_from_emi,
    "sip": sip,
    "inflation_fv": inflation_fv,
    "months_between": months_between,
    "age": age,
    "floor": math.floor,
    "ceil": math.ceil,
})