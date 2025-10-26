from pydantic import BaseModel, Field
from typing import List, Optional

# Generic response models
class ValidationErrorItem(BaseModel):
    field: str
    message: str

class ValidateInputsResponse(BaseModel):
    valid: bool
    errors: List[ValidationErrorItem] = []

# Term insurance
class TermInsuranceRequest(BaseModel):
    age: int
    annual_income: float
    existing_cover: float = 0.0
    liabilities: float = 0.0
    dependents: int = 1

class TermInsuranceResponse(BaseModel):
    recommended_cover: float
    shortfall: float
    monthly_premium_estimate: float

# Health insurance
class HealthInsuranceRequest(BaseModel):
    adults: int = 2
    children: int = 0
    city_tier: int = Field(2, ge=1, le=3)
    existing_cover: float = 0.0

class IndividualCover(BaseModel):
    person: str
    cover: float

class HealthInsuranceResponse(BaseModel):
    recommended_cover: float
    family_floater: float
    individual_covers: List[IndividualCover]

# Retirement
class RetirementRequest(BaseModel):
    current_age: int
    retirement_age: int
    current_savings: float = 0.0
    monthly_investment: float = 0.0
    expected_return_percent: float = 10.0
    inflation_percent: float = 6.0
    desired_monthly_expense: float = 50000.0

class RetirementResponse(BaseModel):
    required_corpus: float
    monthly_sip_10: float
    monthly_sip_12: float
    monthly_sip_15: float

# Child education
class ChildEducationRequest(BaseModel):
    children: int
    years_to_goal: int
    current_cost_per_child: float
    inflation_percent: float = 8.0

class ChildEducationResponse(BaseModel):
    per_child_corpus: List[float]
    total_required: float
    monthly_sip_scenarios: List[float]

# Child wedding
class ChildWeddingRequest(BaseModel):
    children: int
    years_to_goal: int
    current_cost_per_child: float
    inflation_percent: float = 7.0

class ChildWeddingResponse(BaseModel):
    per_child_corpus: List[float]
    total_required: float
    monthly_sip_scenarios: List[float]

# Home purchase
class HomePurchaseRequest(BaseModel):
    property_price: float
    down_payment: float = 0.0
    annual_income: float
    tenure_years: int = 20
    interest_percent: float = 9.0

class HomePurchaseResponse(BaseModel):
    loan_eligibility: float
    emi: float
    down_payment_sip: float
    shortfall_analysis: float

# Car purchase
class CarPurchaseRequest(BaseModel):
    car_price: float
    down_payment: float = 0.0
    annual_income: float
    tenure_years: int = 7
    interest_percent: float = 10.0

class CarPurchaseResponse(BaseModel):
    loan_eligibility: float
    emi: float
    down_payment_sip: float

# Vacation planning
class VacationPlanItem(BaseModel):
    years_to_vacation: int
    budget: float

class VacationPlanningRequest(BaseModel):
    plans: List[VacationPlanItem]
    inflation_percent: float = 7.0

class VacationPlanningResponse(BaseModel):
    per_vacation_sip: List[float]
    total_monthly_investment: float

# Tax planning
class TaxPlanningRequest(BaseModel):
    annual_income: float
    deductions_80c: float = 0.0
    deductions_80d: float = 0.0
    housing_loan_interest: float = 0.0

class TaxPlanningResponse(BaseModel):
    taxable_income: float
    tax_liability: float
    savings_suggestions: List[str]

# Cache read
class CalculationCacheResponse(BaseModel):
    calculation_id: str
    results: Optional[dict]