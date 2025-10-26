from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from common.db.mysql import Base


class AffiliateProfile(Base):
    __tablename__ = "affiliate_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True, nullable=False)
    code = Column(String(32), unique=True, index=True, nullable=False)
    approved = Column(Boolean, default=False)
    photo_url = Column(String(255), nullable=True)
    logo_url = Column(String(255), nullable=True)
    custom_headline = Column(String(255), nullable=True)
    special_offer = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    custom_message = Column(Text, nullable=True)
    cta_text = Column(String(64), nullable=True)
    landing_page_slug = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class AffiliateApplication(Base):
    __tablename__ = "affiliate_applications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    company_name = Column(String(128), nullable=True)
    bio = Column(Text, nullable=True)
    why_join = Column(Text, nullable=True)
    status = Column(String(32), default="pending")  # pending, approved, rejected
    review_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Referral(Base):
    __tablename__ = "affiliate_referrals"
    id = Column(Integer, primary_key=True, index=True)
    affiliate_user_id = Column(Integer, index=True, nullable=False)
    advisor_user_id = Column(Integer, index=True, nullable=True)
    referral_code = Column(String(32), index=True, nullable=False)
    signup_date = Column(DateTime, nullable=True)
    status = Column(String(32), default="trial")  # trial, active, expired, converted
    created_at = Column(DateTime, default=datetime.utcnow)


class Commission(Base):
    __tablename__ = "affiliate_commissions"
    id = Column(Integer, primary_key=True, index=True)
    affiliate_user_id = Column(Integer, index=True, nullable=False)
    advisor_user_id = Column(Integer, index=True, nullable=False)
    payment_id = Column(Integer, index=True, nullable=True)
    transaction_type = Column(String(32), nullable=False)  # new_subscription, renewal
    subscription_tier = Column(String(64), nullable=True)
    gross_amount = Column(Float, default=0.0)
    net_amount = Column(Float, default=0.0)
    commission_rate = Column(Float, default=0.0)  # percent
    commission_amount = Column(Float, default=0.0)
    status = Column(String(32), default="pending_approval")  # pending_approval, approved, rejected, modified_approved
    payout_status = Column(String(32), default="pending")  # pending, paid
    approved_by = Column(Integer, nullable=True)
    rejected_by = Column(Integer, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    modification_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)


class Payout(Base):
    __tablename__ = "affiliate_payouts"
    id = Column(Integer, primary_key=True, index=True)
    affiliate_user_id = Column(Integer, index=True, nullable=False)
    amount = Column(Float, default=0.0)
    payment_method = Column(String(32), nullable=True)  # NEFT/RTGS/UPI
    transaction_id = Column(String(64), nullable=True)
    processed_by = Column(Integer, nullable=True)
    processed_at = Column(DateTime, default=datetime.utcnow)


class AffiliateBankAccount(Base):
    __tablename__ = "affiliate_bank_accounts"
    id = Column(Integer, primary_key=True, index=True)
    affiliate_user_id = Column(Integer, index=True, nullable=False)
    account_holder = Column(String(128), nullable=False)
    bank_name = Column(String(128), nullable=False)
    account_number = Column(String(64), nullable=False)
    ifsc = Column(String(16), nullable=False)
    account_type = Column(String(32), nullable=True)  # savings/current
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)