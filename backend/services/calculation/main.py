from fastapi import FastAPI, APIRouter, Header, HTTPException
from typing import List
from math import pow

from common.security.jwt import decode_token

from .schemas import (
    TermInsuranceRequest, TermInsuranceResponse,
    HealthInsuranceRequest, HealthInsuranceResponse, IndividualCover,
    RetirementRequest, RetirementResponse,
    ChildEducationRequest, ChildEducationResponse,
    ChildWeddingRequest, ChildWeddingResponse,
    HomePurchaseRequest, HomePurchaseResponse,
    CarPurchaseRequest, CarPurchaseResponse,
    VacationPlanningRequest, VacationPlanningResponse,
    TaxPlanningRequest, TaxPlanningResponse,
    ValidateInputsResponse, ValidationErrorItem,
    CalculationCacheResponse,
)

app = FastAPI(title="Calculation Service", version="1.0.0")
router = APIRouter(prefix="/api/v1")


def require_auth(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

@router.get("/health")
def health():
    return {"status": "ok", "service": "calculation"}

# Utilities

def future_value(present: float, rate_percent: float, years: int) -> float:
    return present * pow(1 + rate_percent / 100.0, years)

def sip_required(target: float, rate_percent: float, months: int) -> float:
    r = rate_percent / 100.0 / 12.0
    if r == 0:
        return target / months
    return target * r / (pow(1 + r, months) - 1)

# 69: Term insurance
@router.post("/calculate/term-insurance", response_model=TermInsuranceResponse)
def calc_term(req: TermInsuranceRequest, user= require_auth):
    recommended = max(req.annual_income * 15, req.liabilities + 20_00_000)
    shortfall = max(0.0, recommended - req.existing_cover)
    monthly_premium = recommended / 10_00_000 * 500  # rough heuristic
    return TermInsuranceResponse(recommended_cover=recommended, shortfall=shortfall, monthly_premium_estimate=monthly_premium)

# 70: Health insurance
@router.post("/calculate/health-insurance", response_model=HealthInsuranceResponse)
def calc_health(req: HealthInsuranceRequest, user= require_auth):
    members = req.adults + req.children
    recommended = 3_00_000 + members * 2_00_000 + (req.city_tier - 1) * 1_00_000
    floater = max(5_00_000, recommended)
    individuals: List[IndividualCover] = []
    for i in range(members):
        individuals.append(IndividualCover(person=f"Member-{i+1}", cover=max(2_00_000, recommended / members)))
    return HealthInsuranceResponse(recommended_cover=recommended, family_floater=floater, individual_covers=individuals)

# 71: Retirement
@router.post("/calculate/retirement", response_model=RetirementResponse)
def calc_retirement(req: RetirementRequest, user= require_auth):
    years = max(0, req.retirement_age - req.current_age)
    needed_monthly_today = req.desired_monthly_expense
    needed_monthly_at_retire = future_value(needed_monthly_today, req.inflation_percent, years)
    corpus = needed_monthly_at_retire * 12 * 25  # 4% rule approx
    months = years * 12
    sip10 = sip_required(max(0.0, corpus - req.current_savings), 10.0, months)
    sip12 = sip_required(max(0.0, corpus - req.current_savings), 12.0, months)
    sip15 = sip_required(max(0.0, corpus - req.current_savings), 15.0, months)
    return RetirementResponse(required_corpus=corpus, monthly_sip_10=sip10, monthly_sip_12=sip12, monthly_sip_15=sip15)

# 72: Child education
@router.post("/calculate/child-education", response_model=ChildEducationResponse)
def calc_child_education(req: ChildEducationRequest, user= require_auth):
    target_per_child = future_value(req.current_cost_per_child, req.inflation_percent, req.years_to_goal)
    per_child = [target_per_child for _ in range(req.children)]
    total = target_per_child * req.children
    months = req.years_to_goal * 12
    scenarios = [sip_required(total, r, months) for r in (10.0, 12.0, 15.0)]
    return ChildEducationResponse(per_child_corpus=per_child, total_required=total, monthly_sip_scenarios=scenarios)

# 73: Child wedding
@router.post("/calculate/child-wedding", response_model=ChildWeddingResponse)
def calc_child_wedding(req: ChildWeddingRequest, user= require_auth):
    target_per_child = future_value(req.current_cost_per_child, req.inflation_percent, req.years_to_goal)
    per_child = [target_per_child for _ in range(req.children)]
    total = target_per_child * req.children
    months = req.years_to_goal * 12
    scenarios = [sip_required(total, r, months) for r in (10.0, 12.0, 15.0)]
    return ChildWeddingResponse(per_child_corpus=per_child, total_required=total, monthly_sip_scenarios=scenarios)

# 74: Home purchase
@router.post("/calculate/home-purchase", response_model=HomePurchaseResponse)
def calc_home_purchase(req: HomePurchaseRequest, user= require_auth):
    eligibility = req.annual_income * 4
    principal = max(0.0, req.property_price - req.down_payment)
    r = req.interest_percent / 100.0 / 12.0
    n = req.tenure_years * 12
    emi = principal * r * pow(1 + r, n) / (pow(1 + r, n) - 1)
    dp_sip = sip_required(req.down_payment, 10.0, 36) if req.down_payment > 0 else 0.0
    shortfall = max(0.0, principal - eligibility)
    return HomePurchaseResponse(loan_eligibility=eligibility, emi=emi, down_payment_sip=dp_sip, shortfall_analysis=shortfall)

# 75: Car purchase
@router.post("/calculate/car-purchase", response_model=CarPurchaseResponse)
def calc_car_purchase(req: CarPurchaseRequest, user= require_auth):
    eligibility = req.annual_income * 0.6
    principal = max(0.0, req.car_price - req.down_payment)
    r = req.interest_percent / 100.0 / 12.0
    n = req.tenure_years * 12
    emi = principal * r * pow(1 + r, n) / (pow(1 + r, n) - 1)
    dp_sip = sip_required(req.down_payment, 10.0, 18) if req.down_payment > 0 else 0.0
    return CarPurchaseResponse(loan_eligibility=eligibility, emi=emi, down_payment_sip=dp_sip)

# 76: Vacation planning
@router.post("/calculate/vacation", response_model=VacationPlanningResponse)
def calc_vacation(req: VacationPlanningRequest, user= require_auth):
    per_sip: List[float] = []
    total = 0.0
    for plan in req.plans:
        target = future_value(plan.budget, req.inflation_percent, plan.years_to_vacation)
        months = plan.years_to_vacation * 12
        sip = sip_required(target, 12.0, months)
        per_sip.append(sip)
        total += sip
    return VacationPlanningResponse(per_vacation_sip=per_sip, total_monthly_investment=total)

# 77: Tax planning
@router.post("/calculate/tax-planning", response_model=TaxPlanningResponse)
def calc_tax(req: TaxPlanningRequest, user= require_auth):
    taxable = max(0.0, req.annual_income - (req.deductions_80c + req.deductions_80d + req.housing_loan_interest))
    # Simple slab (old regime placeholder): 5%, 20%, 30%
    tax = 0.0
    if taxable <= 250000:
        tax = 0.0
    elif taxable <= 500000:
        tax = (taxable - 250000) * 0.05
    elif taxable <= 1000000:
        tax = 250000 * 0.05 + (taxable - 500000) * 0.20
    else:
        tax = 250000 * 0.05 + 500000 * 0.20 + (taxable - 1000000) * 0.30
    suggestions = []
    if req.deductions_80c < 150000:
        suggestions.append("Increase 80C investments up to 1.5L limit")
    if req.deductions_80d < 25000:
        suggestions.append("Consider health insurance to claim 80D")
    return TaxPlanningResponse(taxable_income=taxable, tax_liability=tax, savings_suggestions=suggestions)

# 78: Cache read (stub)
@router.get("/calculate/cache/{calculation_id}", response_model=CalculationCacheResponse)
def calc_cache(calculation_id: str, user= require_auth):
    return CalculationCacheResponse(calculation_id=calculation_id, results=None)

# 79: Validate inputs
@router.post("/calculate/validate-inputs", response_model=ValidateInputsResponse)
def validate_inputs(payload: dict, user= require_auth):
    errors: List[ValidationErrorItem] = []
    for field in ("annual_income", "age"):
        if field not in payload:
            errors.append(ValidationErrorItem(field=field, message="Required"))
    return ValidateInputsResponse(valid=len(errors) == 0, errors=errors)

app.include_router(router)