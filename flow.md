# SalahkaarPro: User Flow → API Endpoints Mapping
Complete Workflow-to-Endpoint Reference

## 1. ADVISOR USER FLOWS

### 1.1 Organic Advisor Registration → Trial Activation

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Check email availability | GET | `/api/v1/auth/check-email?email=user@example.com` | Validate email not taken | `email` (query) |
| 2 | Register account | POST | `/api/v1/auth/register` | Create user account | `{user_type: "advisor", email, password, full_name, mobile, organization, role, city, terms_accepted}` |
| 3 | Verify email | POST | `/api/v1/auth/verify-email` | Activate account | `{token}` (from email) |
| 4 | Login | POST | `/api/v1/auth/login` | Get access tokens | `{email, password}` |
| 5 | Activate trial | POST | `/api/v1/subscriptions/trial/activate` | Start 3-day trial | - |
| 6 | Get dashboard data | GET | `/api/v1/users/dashboard-stats` | Load dashboard | - |
| 7 | Get trial status | GET | `/api/v1/subscriptions/trial/status` | Show trial info | - |

### 1.2 Affiliate Referral → Advisor Registration → Paid Subscription

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Load affiliate landing page | GET | `/api/v1/affiliates/landing-page?affiliate_id=AFF_12345` | Get custom content | `affiliate_id` (from URL) |
| 2 | Check email availability | GET | `/api/v1/auth/check-email?email=user@example.com` | Validate email | `email` (query) |
| 3 | Register with referral | POST | `/api/v1/auth/register` | Create account with ref | `{user_type: "advisor", email, password, ..., referral_code: "AFF_12345"}` |
| 4 | Verify email | POST | `/api/v1/auth/verify-email` | Activate account | `{token}` |
| 5 | Login | POST | `/api/v1/auth/login` | Get access tokens | `{email, password}` |
| 6 | Get subscription tiers | GET | `/api/v1/subscriptions/tiers` | Show pricing | - |
| 7 | Subscribe to tier | POST | `/api/v1/subscriptions/subscribe` | Initiate subscription | `{tier_id, payment_method}` |
| 8 | Create payment order | POST | `/api/v1/payments/create-order` | Generate payment link | `{subscription_id, tier_id, amount}` |
| 9 | Verify payment | POST | `/api/v1/payments/verify` | Confirm payment | `{order_id, payment_id, signature}` |
| 10 | Select forms (if Starter+/Specialist+) | POST | `/api/v1/subscriptions/forms/select` | Choose forms | `{form_ids: ["term_insurance", "retirement"]}` |
| 11 | Get my subscription | GET | `/api/v1/subscriptions/my-subscription` | Confirm activation | - |

### 1.3 Trial User → Paid Conversion

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Check trial status | GET | `/api/v1/subscriptions/trial/status` | Get remaining reports/days | - |
| 2 | Get subscription tiers | GET | `/api/v1/subscriptions/tiers` | Show pricing options | - |
| 3 | Subscribe to tier | POST | `/api/v1/subscriptions/subscribe` | Choose paid plan | `{tier_id, payment_method}` |
| 4 | Create payment order | POST | `/api/v1/payments/create-order` | Generate payment | `{subscription_id, tier_id, amount}` |
| 5 | Verify payment | POST | `/api/v1/payments/verify` | Confirm payment | `{order_id, payment_id, signature}` |
| 6 | Select forms (if applicable) | POST | `/api/v1/subscriptions/forms/select` | Choose forms | `{form_ids[]}` |
| 7 | Get updated subscription | GET | `/api/v1/subscriptions/my-subscription` | Confirm conversion | - |

### 1.4 Report Generation Flow (Complete)

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Check report limit | POST | `/api/v1/subscriptions/reports/check-limit` | Verify can generate | - |
| 2 | Get form schema | GET | `/api/v1/forms/schema/term-insurance` | Load form fields | - |
| 3 | Load saved draft (if exists) | GET | `/api/v1/forms/draft/term-insurance` | Restore previous data | - |
| 4 | Save draft (auto-save) | POST | `/api/v1/forms/draft/save` | Backup form data | `{form_type, draft_data{}}` |
| 5 | Validate inputs | POST | `/api/v1/calculate/validate-inputs` | Check data validity | `{form_type, inputs{}}` |
| 6 | Calculate results | POST | `/api/v1/calculate/term-insurance` | Backend calculation | `{age, income, expenses, ...}` |
| 7 | Preview report (modal) | POST | `/api/v1/reports/preview` | Show summary | `{form_type, calculation_results}` |
| 8 | Submit form data | POST | `/api/v1/forms/submit` | Save submission | `{form_type, client_name, form_data{}}` |
| 9 | Generate PDF | POST | `/api/v1/reports/generate` | Create PDF report | `{form_type, submission_id, language: "en"}` |
| 10 | Deduct report count | POST | `/api/v1/subscriptions/reports/deduct` | Decrement limit | `{user_id}` (internal) |
| 11 | Get report details | GET | `/api/v1/reports/{report_id}` | Fetch report data | - |
| 12 | Download PDF | GET | `/api/v1/reports/{report_id}/download` | Download file | - |

### 1.5 Profile Management (Within 72-Hour Grace Period)

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Get profile | GET | `/api/v1/users/profile` | Load current profile | - |
| 2 | Check grace period | GET | `/api/v1/users/grace-period-status` | Verify can edit | - |
| 3 | Update profile | PUT | `/api/v1/users/profile` | Save changes | `{full_name, organization, role, mobile, email}` |
| 4 | Upload photo | POST | `/api/v1/users/profile/photo` | Add profile picture | `multipart/form-data` |
| 5 | Upload logo | POST | `/api/v1/users/profile/logo` | Add company logo | `multipart/form-data` |
| 6 | Lock profile manually | POST | `/api/v1/users/profile/lock` | End grace period | - |

### 1.6 Profile Update Request (After Grace Period)

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Get profile | GET | `/api/v1/users/profile` | View locked profile | - |
| 2 | Check grace period | GET | `/api/v1/users/grace-period-status` | Confirm expired | - |
| 3 | Request update | POST | `/api/v1/users/profile/update-request` | Submit request | `{field_name: "full_name", new_value: "New Name", reason: "Typo correction"}` |
| 4 | Check request status | GET | `/api/v1/users/profile/update-requests` | Monitor approval | - |
| 5 | (Wait for admin approval) | - | - | - | - |
| 6 | Get updated profile | GET | `/api/v1/users/profile` | View changes | - |

### 1.7 Subscription Upgrade Flow

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Get current subscription | GET | `/api/v1/subscriptions/my-subscription` | View current tier | - |
| 2 | Get all tiers | GET | `/api/v1/subscriptions/tiers` | Compare options | - |
| 3 | Initiate upgrade | POST | `/api/v1/subscriptions/upgrade` | Calculate prorated cost | `{new_tier_id}` |
| 4 | Create payment order | POST | `/api/v1/payments/create-order` | Generate payment | `{subscription_id, tier_id, amount}` |
| 5 | Verify payment | POST | `/api/v1/payments/verify` | Confirm payment | `{order_id, payment_id, signature}` |
| 6 | Select additional forms (if applicable) | POST | `/api/v1/subscriptions/forms/select` | Add more forms | `{form_ids[]}` |
| 7 | Get updated subscription | GET | `/api/v1/subscriptions/my-subscription` | Confirm upgrade | - |
| 8 | Get dashboard stats | GET | `/api/v1/users/dashboard-stats` | View new limits | - |

### 1.8 Subscription Renewal Flow

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Get current subscription | GET | `/api/v1/subscriptions/my-subscription` | Check expiry | - |
| 2 | Get subscription tiers | GET | `/api/v1/subscriptions/tiers` | View pricing | - |
| 3 | Initiate renewal | POST | `/api/v1/subscriptions/renew` | Start renewal | `{tier_id}` (same or different) |
| 4 | Create payment order | POST | `/api/v1/payments/create-order` | Generate payment | `{subscription_id, tier_id, amount}` |
| 5 | Verify payment | POST | `/api/v1/payments/verify` | Confirm payment | `{order_id, payment_id, signature}` |
| 6 | Get updated subscription | GET | `/api/v1/subscriptions/my-subscription` | Confirm renewal | - |
| 7 | Get payment history | GET | `/api/v1/payments/my-payments` | View invoice | - |

### 1.9 Refund Request Flow (Within 72 Hours)

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Get payment history | GET | `/api/v1/payments/my-payments` | Find payment | - |
| 2 | Check refund eligibility | GET | `/api/v1/payments/refund/eligibility?payment_id={id}` | Verify MBG window | `payment_id` (query) |
| 3 | Request refund | POST | `/api/v1/payments/refund/request` | Submit request | `{payment_id, reason: "Not satisfied"}` |
| 4 | (Wait for admin processing) | - | - | - | - |
| 5 | Check payment status | GET | `/api/v1/payments/{payment_id}` | Monitor refund | - |

### 1.10 Password Reset Flow

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Request reset | POST | `/api/v1/auth/password-reset/request` | Send reset email | `{email}` |
| 2 | (User clicks email link with token) | - | - | - | - |
| 3 | Confirm reset | POST | `/api/v1/auth/password-reset/confirm` | Set new password | `{token, new_password}` |
| 4 | Login with new password | POST | `/api/v1/auth/login` | Access account | `{email, new_password}` |

## 2. AFFILIATE USER FLOWS

### 2.1 Affiliate Self-Application Flow

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Check email availability | GET | `/api/v1/auth/check-email?email=affiliate@example.com` | Validate email | `email` (query) |
| 2 | Register as affiliate | POST | `/api/v1/auth/register` | Create account | `{user_type: "affiliate", email, password, full_name, mobile, company_name}` |
| 3 | Verify email | POST | `/api/v1/auth/verify-email` | Activate account | `{token}` |
| 4 | Login | POST | `/api/v1/auth/login` | Get access tokens | `{email, password}` |
| 5 | Submit application | POST | `/api/v1/affiliates/apply` | Apply for program | `{company_name, bio, why_join}` |
| 6 | Check application status | GET | `/api/v1/affiliates/application-status` | Monitor approval | - |
| 7 | (Wait for admin approval) | - | - | - | - |
| 8 | Get dashboard data (after approval) | GET | `/api/v1/affiliates/dashboard` | Load dashboard | - |

### 2.2 Affiliate Landing Page Customization

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Get current landing page | GET | `/api/v1/affiliates/landing-page` | Load existing content | - |
| 2 | Upload photo | POST | `/api/v1/affiliates/landing-page/photo` | Add profile photo | `multipart/form-data` |
| 3 | Update content | PUT | `/api/v1/affiliates/landing-page` | Customize page | `{headline, special_offer, custom_message, cta_text}` |
| 4 | Preview landing page | GET | `/api/v1/affiliates/landing-page` | Verify changes | - |
| 5 | Get referral links | GET | `/api/v1/affiliates/my-links` | Get URLs & QR code | - |

### 2.3 Affiliate Commission Tracking Flow

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Get dashboard overview | GET | `/api/v1/affiliates/dashboard` | View summary stats | - |
| 2 | Get referral list | GET | `/api/v1/affiliates/referrals?page=1&status=converted` | View referrals | Query params |
| 3 | Get referral details | GET | `/api/v1/affiliates/referral/{referral_id}` | View specific referral | - |
| 4 | Get commission list | GET | `/api/v1/affiliates/commissions?status=pending_approval&page=1` | View earnings | Query params |
| 5 | Get commission details | GET | `/api/v1/affiliates/commission/{commission_id}` | View specific commission | - |
| 6 | Get payout history | GET | `/api/v1/affiliates/payouts` | View paid commissions | - |
| 7 | Get performance analytics | GET | `/api/v1/affiliates/performance?from=2025-01-01&to=2025-01-31` | View metrics | Date range |

### 2.4 Affiliate Bank Account Setup

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Get existing accounts | GET | `/api/v1/affiliates/bank-accounts` | View saved accounts | - |
| 2 | Add bank account | POST | `/api/v1/affiliates/bank-account` | Add payout details | `{account_holder_name, bank_name, account_number, ifsc_code, account_type}` |
| 3 | Update account | PUT | `/api/v1/affiliates/bank-account/{account_id}` | Edit details | `{fields to update}` |
| 4 | Delete account | DELETE | `/api/v1/affiliates/bank-account/{account_id}` | Remove account | - |

## 3. ADMIN FLOWS

### 3.1 Admin Dashboard Overview

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Login with MFA | POST | `/api/v1/auth/login` | Initial authentication | `{email, password}` |
| 2 | Verify MFA code | POST | `/api/v1/auth/mfa/verify` | Complete MFA | `{code}` |
| 3 | Get dashboard metrics | GET | `/api/v1/admin/dashboard` | Load overview | - |
| 4 | Get overall analytics | GET | `/api/v1/admin/analytics/overview?from=2025-01-01&to=2025-01-31` | View trends | Date range |
| 5 | Get revenue analytics | GET | `/api/v1/admin/analytics/revenue?from=2025-01-01&to=2025-01-31` | Revenue breakdown | Date range |

### 3.2 Admin: Approve Affiliate Application

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Get pending applications | GET | `/api/v1/admin/affiliates/pending` | View applications | - |
| 2 | View affiliate details | GET | `/api/v1/admin/users/{user_id}/details` | Review profile | - |
| 3 | Approve affiliate | POST | `/api/v1/admin/affiliates/{affiliate_id}/approve` | Grant access | `{commission_plan_id}` |
| 4 | (System sends approval email) | - | - | - | - |
| 5 | View updated affiliate list | GET | `/api/v1/admin/users?type=affiliate&status=approved` | Confirm approval | - |

**OR Reject:**
| 3 | Reject affiliate | POST | `/api/v1/admin/affiliates/{affiliate_id}/reject` | Deny access | `{reason: "Insufficient information"}` |

### 3.3 Admin: Approve Commission Flow

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Get pending commissions | GET | `/api/v1/admin/commissions/pending?page=1` | View queue | - |
| 2 | View commission details | GET | `/api/v1/affiliates/commission/{commission_id}` | Review transaction | - |
| 3 | View payment details | GET | `/api/v1/payments/{payment_id}` | Verify payment | - |
| 4 | Approve commission | POST | `/api/v1/admin/commissions/{commission_id}/approve` | Approve earning | - |
| 5 | View updated commission list | GET | `/api/v1/admin/commissions/pending` | Confirm approval | - |

**OR Modify/Reject:**
| 4 | Modify commission | POST | `/api/v1/admin/commissions/{commission_id}/modify` | Change amount | `{new_amount: 500, reason: "Negotiated rate"}` |
| 4 | Reject commission | POST | `/api/v1/admin/commissions/{commission_id}/reject` | Deny earning | `{reason: "Fraudulent referral"}` |

**Bulk Approval:**
| 4 | Bulk approve | POST | `/api/v1/admin/commissions/bulk-approve` | Approve multiple | `{commission_ids: ["id1", "id2", ...]}` |

### 3.4 Admin: Process Affiliate Payout

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Get pending payouts | GET | `/api/v1/admin/payouts/pending` | View payout queue | - |
| 2 | View affiliate bank account | GET | `/api/v1/affiliates/bank-accounts` | Get payout details | - |
| 3 | Process payout | POST | `/api/v1/admin/payouts/{affiliate_id}/process` | Mark as paid | `{amount, payment_method: "NEFT", transaction_id: "TXN123"}` |
| 4 | (System updates commission status to "paid") | - | - | - | - |
| 5 | (System sends confirmation email to affiliate) | - | - | - | - |
| 6 | View payout history | GET | `/api/v1/affiliates/payouts` | Verify completion | - |

**Bulk Processing:**
| 3 | Bulk process payouts | POST | `/api/v1/admin/payouts/bulk-process` | Pay multiple affiliates | `{affiliate_ids: ["AFF_1", "AFF_2", ...]}` |

### 3.5 Admin: User Management (Advisor)

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Search users | GET | `/api/v1/admin/users?q=john&type=advisor&status=active` | Find user | Query params |
| 2 | Get user details | GET | `/api/v1/admin/users/{user_id}/details` | View full profile | - |
| 3 | View subscription | GET | `/api/v1/subscriptions/my-subscription` | Check tier | - |
| 4 | View payment history | GET | `/api/v1/payments/my-payments` | View transactions | - |
| 5 | View report history | GET | `/api/v1/reports/my-reports` | View usage | - |
| 6 | Update user profile | PUT | `/api/v1/admin/users/{user_id}/profile` | Edit any field | `{any_field: value}` |
| 7 | Extend subscription | POST | `/api/v1/subscriptions/{user_id}/extend` | Add free days | `{days: 30}` |
| 8 | Add bonus reports | POST | `/api/v1/subscriptions/{user_id}/add-reports` | Add reports | `{count: 50, reason: "Goodwill"}` |
| 9 | Change tier | PUT | `/api/v1/subscriptions/{user_id}/change-tier` | Change subscription | `{tier_id, reason: "Special request"}` |
| 10 | Deactivate user | POST | `/api/v1/admin/users/{user_id}/deactivate` | Suspend account | `{reason: "Policy violation"}` |

### 3.6 Admin: Approve Profile Update Request

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Get pending requests | GET | `/api/v1/admin/profile-update-requests?status=pending` | View requests | - |
| 2 | View user profile | GET | `/api/v1/admin/users/{user_id}/details` | Review current data | - |
| 3 | Approve request | POST | `/api/v1/admin/profile-update-requests/{request_id}/approve` | Apply changes | - |
| 4 | (System updates user profile) | - | - | - | - |
| 5 | (System sends confirmation email) | - | - | - | - |

**OR Reject:**
| 3 | Reject request | POST | `/api/v1/admin/profile-update-requests/{request_id}/reject` | Deny changes | `{reason: "Insufficient documentation"}` |

### 3.7 Admin: Process Refund Request

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Get refund requests | GET | `/api/v1/payments/refunds?status=pending` | View requests | - |
| 2 | View payment details | GET | `/api/v1/payments/{payment_id}` | Verify payment | - |
| 3 | View user subscription | GET | `/api/v1/subscriptions/my-subscription` | Check eligibility | - |
| 4 | Approve refund | POST | `/api/v1/payments/refund/{refund_id}/approve` | Authorize refund | - |
| 5 | Process refund | POST | `/api/v1/payments/refund/{refund_id}/process` | Execute refund | `{gateway_refund_id: "REFUND_123"}` |
| 6 | (System cancels subscription) | - | - | - | - |
| 7 | (System reverses affiliate commission if applicable) | - | - | - | - |

**OR Reject:**
| 4 | Reject refund | POST | `/api/v1/payments/refund/{refund_id}/reject` | Deny refund | `{reason: "Outside 72-hour window"}` |

### 3.8 Admin: Subscription Tier Management

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Get all tiers | GET | `/api/v1/admin/subscription-tiers` | View tiers | - |
| 2 | Update tier pricing | PUT | `/api/v1/admin/subscription-tiers/{tier_id}` | Modify tier | `{price_original, price_launch, report_limit, features[]}` |
| 3 | Create new tier | POST | `/api/v1/admin/subscription-tiers` | Add tier | `{tier_name, display_name, price_original, price_launch, report_limit, features[]}` |
| 4 | Deactivate tier | DELETE | `/api/v1/admin/subscription-tiers/{tier_id}` | Remove tier | - |

### 3.9 Admin: Commission Plan Management

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Get all plans | GET | `/api/v1/admin/commission-plans` | View plans | - |
| 2 | Update default plan | PUT | `/api/v1/admin/commission-plans/{plan_id}` | Modify structure | `{tier_1_rate: 22, tier_2_rate: 27, ...}` |
| 3 | Create custom plan | POST | `/api/v1/admin/commission-plans` | New plan | `{plan_name, tier_rates{}, renewal_rate}` |
| 4 | Assign custom plan to affiliate | PUT | `/api/v1/admin/affiliates/{affiliate_id}/commission-plan` | Override plan | `{plan_id, custom_rate: 35}` |

### 3.10 Admin: Analytics & Reports

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Get overview analytics | GET | `/api/v1/admin/analytics/overview?from=2025-01-01&to=2025-01-31` | High-level metrics | Date range |
| 2 | Get revenue analytics | GET | `/api/v1/admin/analytics/revenue?from=2025-01-01&to=2025-01-31&breakdown=monthly` | Revenue breakdown | Date range, breakdown |
| 3 | Get affiliate performance | GET | `/api/v1/admin/analytics/affiliates?from=2025-01-01&to=2025-01-31` | Affiliate metrics | Date range |
| 4 | Get report analytics | GET | `/api/v1/admin/analytics/reports?from=2025-01-01&to=2025-01-31` | Report usage | Date range |
| 5 | Get conversion analytics | GET | `/api/v1/admin/analytics/conversions?from=2025-01-01&to=2025-01-31` | Funnel data | Date range |
| 6 | Get subscription analytics | GET | `/api/v1/subscriptions/analytics?from=2025-01-01&to=2025-01-31` | Subscription stats | Date range |
| 7 | Get payment analytics | GET | `/api/v1/payments/analytics?from=2025-01-01&to=2025-01-31` | Payment stats | Date range |

## 4. PRO USER FLOWS

### 4.1 Financial Horoscope Generation (Pro Only)

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Verify Pro subscription | GET | `/api/v1/subscriptions/my-subscription` | Check tier access | - |
| 2 | Get form schema | GET | `/api/v1/forms/schema/financial-horoscope` | Load comprehensive form | - |
| 3 | Submit comprehensive data | POST | `/api/v1/forms/submit` | Save client data | `{form_type: "financial_horoscope", client_name, comprehensive_data{}}` |
| 4 | Generate horoscope | POST | `/api/v1/pro/financial-horoscope/generate` | Calculate scores | `{submission_id}` |
| 5 | Get horoscope details | GET | `/api/v1/pro/financial-horoscope/{horoscope_id}` | View full results | - |
| 6 | Generate PDF report | POST | `/api/v1/reports/generate` | Create PDF | `{form_type: "financial_horoscope", submission_id, language}` |
| 7 | View clients list | GET | `/api/v1/pro/clients` | View all clients | - |

### 4.2 1-on-1 Financial Planning Session (Pro Only)

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Get client dashboard | GET | `/api/v1/pro/client/{client_id}/dashboard` | Load client data | - |
| 2 | Get horoscope details | GET | `/api/v1/pro/financial-horoscope/{horoscope_id}` | View client horoscope | - |
| 3 | Create planning session | POST | `/api/v1/pro/planning-session/create` | Start session | `{client_id, horoscope_id}` |
| 4 | Get session data | GET | `/api/v1/pro/planning-session/{session_id}` | Load session | - |
| 5 | Update goals | PUT | `/api/v1/pro/planning-session/{session_id}/goals` | Modify goals | `{goals: [{goal_type, data}, ...]}` |
| 6 | Add specific goal | POST | `/api/v1/pro/planning-session/{session_id}/goals/{goal_id}` | Add/edit goal | `{goal_data{}}` |
| 7 | Remove goal | DELETE | `/api/v1/pro/planning-session/{session_id}/goals/{goal_id}` | Delete goal | - |
| 8 | Update risk management | PUT | `/api/v1/pro/planning-session/{session_id}/risk-management` | Edit risk section | `{risk_data{}}` |
| 9 | Customize pages | PUT | `/api/v1/pro/planning-session/{session_id}/customize` | Personalize pages | `{page_id, custom_data{}}` |
| 10 | Generate 1-pager summary | POST | `/api/v1/pro/planning-session/{session_id}/generate-summary` | Create summary PDF | - |
| 11 | Get all sessions | GET | `/api/v1/pro/planning-session/my-sessions` | View session history | - |

## 5. SYSTEM FLOWS

### 5.1 Automated Report Cleanup (Background Job)

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | (Celery scheduled task runs daily) | - | - | - | - |
| 2 | Bulk delete expired reports | POST | `/api/v1/reports/bulk-delete` | Delete 3+ month old | `{before_date: "2025-01-01"}` |
| 3 | Cleanup expired files | POST | `/api/v1/storage/cleanup-expired` | Delete orphaned files | - |

### 5.2 Automated Commission Calculation (Monthly Job)

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | (Celery task runs on 1st of month) | - | - | - | - |
| 2 | Fetch all approved subscriptions | Internal | Database query | Get last month's conversions | - |
| 3 | Calculate commissions | Internal | Business logic | Apply commission rates | - |
| 4 | Create commission records | Internal | Database insert | Save pending commissions | - |
| 5 | Send notification to affiliates | POST | `/api/v1/notifications/send-email` | Notify earnings | `{template_key: "commission_earned"}` |

### 5.3 Subscription Expiry Notification (Daily Job)

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | (Celery task runs daily) | - | - | - | - |
| 2 | Find subscriptions expiring in 7 days | Internal | Database query | Get expiring soon | - |
| 3 | Send email notification | POST | `/api/v1/notifications/send-email` | Remind user | `{template_key: "subscription_expiring", variables: {days: 7}}` |
| 4 | Find expired subscriptions | Internal | Database query | Get expired today | - |
| 5 | Update subscription status | Internal | Database update | Set status to "expired" | - |
| 6 | Send expiry notification | POST | `/api/v1/notifications/send-email` | Inform expiry | `{template_key: "subscription_expired"}` |

### 5.4 Report Limit Warning (Realtime)

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | User generates report | POST | `/api/v1/reports/generate` | Create report | - |
| 2 | Deduct report count | POST | `/api/v1/subscriptions/reports/deduct` | Decrement limit | - |
| 3 | Check if 90% used | Internal | Business logic | Calculate percentage | - |
| 4 | Send warning email (if 90%) | POST | `/api/v1/notifications/send-email` | Warn user | `{template_key: "report_limit_90"}` |
| 5 | Check if 100% used | Internal | Business logic | Calculate percentage | - |
| 6 | Update subscription status | Internal | Database update | Set "active_no_reports" | - |
| 7 | Send limit reached email | POST | `/api/v1/notifications/send-email` | Notify user | `{template_key: "report_limit_reached"}` |

## 6. NOTIFICATION TEMPLATE MANAGEMENT (Admin)

### 6.1 Email Template Management

| Step | Action | Method | Endpoint | Purpose | Required Data |
|------|--------|--------|----------|----------|---------------|
| 1 | Get all templates | GET | `/api/v1/notifications/templates?type=email` | View templates | - |
| 2 | Get specific template | GET | `/api/v1/notifications/template/registration_successful?language=hi` | View content | - |
| 3 | Update template | PUT | `/api/v1/notifications/template/registration_successful` | Edit content | `{language: "hi", subject: "...", body_html: "...", body_text: "..."}` |
| 4 | Test email | POST | `/api/v1/notifications/test-email` | Send test | `{template_key, test_email, variables{}}` |
| 5 | View notification queue | GET | `/api/v1/notifications/queue?status=failed` | Monitor delivery | - |
| 6 | Retry failed notification | POST | `/api/v1/notifications/queue/{notification_id}/retry` | Resend | - |

## QUICK REFERENCE: Most Common Flows

### Top 10 Most Frequent Workflows

| Rank | Flow | Primary Endpoints | Frequency |
|------|------|-------------------|-----------|
| 1 | Report Generation | `/calculate/*`, `/forms/submit`, `/reports/generate` | Daily (hundreds) |
| 2 | Login | `/auth/login`, `/auth/refresh` | Daily (thousands) |
| 3 | Dashboard View | `/users/dashboard-stats`, `/subscriptions/my-subscription` | Daily (thousands) |
| 4 | Payment Processing | `/payments/create-order`, `/payments/verify` | Daily (dozens) |
| 5 | Trial Activation | `/auth/register`, `/auth/verify-email`, `/subscriptions/trial/activate` | Daily (dozens) |
| 6 | Profile Update | `/users/profile` (GET/PUT) | Weekly |
| 7 | Affiliate Tracking | `/affiliates/dashboard`, `/affiliates/commissions` | Daily (affiliates) |
| 8 | Admin User Management | `/admin/users`, `/admin/users/{id}/details` | Daily (admin) |
| 9 | Commission Approval | `/admin/commissions/pending`, `/admin/commissions/{id}/approve` | Weekly (admin) |
| 10 | Subscription Renewal | `/subscriptions/renew`, `/payments/create-order` | Monthly |

---

*This comprehensive flow-to-endpoint mapping serves as the definitive reference for frontend developers, QA testers, and API consumers to understand exactly which endpoints to call in sequence for every user journey in the SalahkaarPro platform.*