# 🧠 SalahkaarPro: Complete API Endpoints Reference

This document provides the full reference of SalahkaarPro’s backend microservices and their API endpoints.

---

# SalahkaarPro: Complete API Endpoints Reference

## 1. AUTH SERVICE (Port: 8001)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|--------|-----------|----------|---------------|--------------|-----------|
| 1 | POST | `/api/v1/auth/register` | Register new user (advisor/affiliate) | No | `{user_type, email, password, full_name, mobile, organization, role, city, terms_accepted}` | `{user_id, email, verification_sent}` |
| 2 | POST | `/api/v1/auth/verify-email` | Verify email address | No | `{token}` | `{email, is_verified}` |
| 3 | POST | `/api/v1/auth/resend-verification` | Resend verification email | No | `{email}` | `{message}` |
| 4 | POST | `/api/v1/auth/login` | User login | No | `{email, password, remember_me}` | `{access_token, refresh_token, user}` |
| 5 | POST | `/api/v1/auth/logout` | User logout | Yes | None | `{message}` |
| 6 | POST | `/api/v1/auth/refresh` | Refresh access token | No | `{refresh_token}` | `{access_token, expires_in}` |
| 7 | POST | `/api/v1/auth/password-reset/request` | Request password reset | No | `{email}` | `{message}` |
| 8 | POST | `/api/v1/auth/password-reset/confirm` | Reset password with token | No | `{token, new_password}` | `{message}` |
| 9 | POST | `/api/v1/auth/change-password` | Change password (logged in) | Yes | `{old_password, new_password}` | `{message}` |
| 10 | POST | `/api/v1/auth/mfa/setup` | Setup MFA (admin only) | Admin | None | `{qr_code_url, secret, backup_codes}` |
| 11 | POST | `/api/v1/auth/mfa/verify` | Verify MFA code | Yes | `{code}` | `{mfa_verified}` |
| 12 | POST | `/api/v1/auth/mfa/disable` | Disable MFA | Admin | `{code}` | `{message}` |
| 13 | GET | `/api/v1/auth/me` | Get current user info | Yes | None | `{user_id, email, user_type, profile}` |
| 14 | GET | `/api/v1/auth/check-email` | Check if email exists | No | Query: `?email=` | `{exists: boolean}` |

## 2. USER SERVICE (Port: 8002)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|--------|-----------|----------|---------------|--------------|-----------|
| 15 | GET | `/api/v1/users/profile` | Get user profile | Yes | None | `{profile_data}` |
| 16 | PUT | `/api/v1/users/profile` | Update profile (allowed fields) | Yes | `{mobile, email}` | `{updated_profile}` |
| 17 | POST | `/api/v1/users/profile/photo` | Upload profile photo | Yes | `multipart/form-data` | `{photo_url}` |
| 18 | POST | `/api/v1/users/profile/logo` | Upload logo | Yes | `multipart/form-data` | `{logo_url}` |
| 19 | DELETE | `/api/v1/users/profile/photo` | Delete profile photo | Yes | None | `{message}` |
| 20 | DELETE | `/api/v1/users/profile/logo` | Delete logo | Yes | None | `{message}` |
| 21 | GET | `/api/v1/users/grace-period-status` | Check grace period status | Yes | None | `{in_grace_period, expires_at}` |
| 22 | POST | `/api/v1/users/profile/lock` | Manually lock profile | Yes | None | `{message}` |
| 23 | POST | `/api/v1/users/profile/update-request` | Request critical field update | Yes | `{field_name, new_value, reason}` | `{request_id, status}` |
| 24 | GET | `/api/v1/users/profile/update-requests` | Get pending update requests | Yes | None | `[{request_id, field, status}]` |
| 25 | GET | `/api/v1/users/activity-log` | Get user activity log | Yes | Query: `?page=1&limit=20` | `{activities[], pagination}` |
| 26 | GET | `/api/v1/users/dashboard-stats` | Get dashboard statistics | Yes | None | `{reports_used, reports_remaining, subscription_status}` |
| 27 | GET | `/api/v1/users/search` | Search users (admin only) | Admin | Query: `?q=&type=&status=` | `{users[], pagination}` |
| 28 | GET | `/api/v1/users/{user_id}` | Get user by ID (admin only) | Admin | None | `{user_data}` |
| 29 | PUT | `/api/v1/users/{user_id}/profile` | Update any user profile (admin) | Admin | `{any_field}` | `{updated_profile}` |
| 30 | POST | `/api/v1/users/{user_id}/activate` | Activate user account (admin) | Admin | None | `{message}` |
| 31 | POST | `/api/v1/users/{user_id}/deactivate` | Deactivate user account (admin) | Admin | `{reason}` | `{message}` |
| 32 | GET | `/api/v1/users/referral-info` | Get referral information | Yes | None | `{referred_by, referral_link}` |

## 3. SUBSCRIPTION SERVICE (Port: 8003)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|--------|-----------|----------|---------------|--------------|-----------|
| 33 | GET | `/api/v1/subscriptions/tiers` | Get all subscription tiers | No | None | `[{tier_name, price, features}]` |
| 34 | GET | `/api/v1/subscriptions/tiers/{tier_id}` | Get tier details | No | None | `{tier_data}` |
| 35 | GET | `/api/v1/subscriptions/my-subscription` | Get current subscription | Yes | None | `{subscription_details}` |
| 36 | POST | `/api/v1/subscriptions/trial/activate` | Activate free trial | Yes | None | `{trial_details, expires_at}` |
| 37 | GET | `/api/v1/subscriptions/trial/status` | Get trial status | Yes | None | `{status, reports_used, expires_at}` |
| 38 | POST | `/api/v1/subscriptions/subscribe` | Subscribe to paid tier | Yes | `{tier_id, payment_method}` | `{subscription_id, payment_url}` |
| 39 | POST | `/api/v1/subscriptions/upgrade` | Upgrade subscription | Yes | `{new_tier_id}` | `{prorated_amount, payment_url}` |
| 40 | POST | `/api/v1/subscriptions/downgrade` | Downgrade subscription | Yes | `{new_tier_id}` | `{effective_date}` |
| 41 | POST | `/api/v1/subscriptions/renew` | Renew subscription | Yes | `{tier_id}` | `{payment_url}` |
| 42 | POST | `/api/v1/subscriptions/cancel` | Cancel subscription | Yes | `{reason}` | `{cancellation_date}` |
| 43 | PUT | `/api/v1/subscriptions/auto-renew` | Toggle auto-renew | Yes | `{enabled: boolean}` | `{auto_renew_status}` |
| 44 | GET | `/api/v1/subscriptions/history` | Get subscription history | Yes | None | `[{subscription_data}]` |
| 45 | POST | `/api/v1/subscriptions/forms/select` | Select forms (Starter+/Specialist+) | Yes | `{form_ids[]}` | `{selected_forms}` |
| 46 | GET | `/api/v1/subscriptions/forms/available` | Get available forms for tier | Yes | None | `{available_forms[]}` |
| 47 | POST | `/api/v1/subscriptions/reports/check-limit` | Check if can generate report | Yes | None | `{can_generate, remaining}` |
| 48 | POST | `/api/v1/subscriptions/reports/deduct` | Deduct report count | Yes (Internal) | `{user_id}` | `{remaining_reports}` |
| 49 | POST | `/api/v1/subscriptions/{user_id}/extend` | Extend subscription (admin) | Admin | `{days}` | `{new_end_date}` |
| 50 | POST | `/api/v1/subscriptions/{user_id}/add-reports` | Add bonus reports (admin) | Admin | `{count, reason}` | `{new_limit}` |
| 51 | PUT | `/api/v1/subscriptions/{user_id}/change-tier` | Change user tier (admin) | Admin | `{tier_id, reason}` | `{updated_subscription}` |
| 52 | GET | `/api/v1/subscriptions/analytics` | Subscription analytics (admin) | Admin | Query: `?from=&to=` | `{stats}` |

## 4. PAYMENT SERVICE (Port: 8004)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|--------|-----------|----------|---------------|--------------|-----------|
| 53 | POST | `/api/v1/payments/create-order` | Create payment order | Yes | `{subscription_id, tier_id, amount}` | `{order_id, payment_url}` |
| 54 | POST | `/api/v1/payments/verify` | Verify payment | Yes | `{order_id, payment_id, signature}` | `{verified, transaction_id}` |
| 55 | POST | `/api/v1/payments/webhook/razorpay` | Razorpay webhook | No (Verified) | Razorpay payload | `{received}` |
| 56 | POST | `/api/v1/payments/webhook/stripe` | Stripe webhook | No (Verified) | Stripe payload | `{received}` |
| 57 | GET | `/api/v1/payments/my-payments` | Get payment history | Yes | Query: `?page=1` | `{payments[], pagination}` |
| 58 | GET | `/api/v1/payments/{payment_id}` | Get payment details | Yes | None | `{payment_data}` |
| 59 | GET | `/api/v1/payments/{payment_id}/invoice` | Download invoice | Yes | None | PDF file |
| 60 | POST | `/api/v1/payments/refund/request` | Request refund | Yes | `{payment_id, reason}` | `{refund_request_id}` |
| 61 | GET | `/api/v1/payments/refund/eligibility` | Check refund eligibility | Yes | Query: `?payment_id=` | `{eligible, reason}` |
| 62 | GET | `/api/v1/payments/refunds` | Get refund requests (admin) | Admin | Query: `?status=` | `{refunds[]}` |
| 63 | POST | `/api/v1/payments/refund/{refund_id}/approve` | Approve refund (admin) | Admin | None | `{refund_id, status}` |
| 64 | POST | `/api/v1/payments/refund/{refund_id}/reject` | Reject refund (admin) | Admin | `{reason}` | `{message}` |
| 65 | POST | `/api/v1/payments/refund/{refund_id}/process` | Process refund (admin) | Admin | `{gateway_refund_id}` | `{processed}` |
| 66 | GET | `/api/v1/payments/analytics` | Payment analytics (admin) | Admin | Query: `?from=&to=` | `{revenue, transactions}` |
| 67 | GET | `/api/v1/payments/failed` | Get failed payments (admin) | Admin | None | `{failed_payments[]}` |
| 68 | POST | `/api/v1/payments/{payment_id}/retry` | Retry failed payment | Yes | None | `{payment_url}` |

## 5. CALCULATION SERVICE (Port: 8005)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|--------|-----------|----------|---------------|--------------|-----------|
| 69 | POST | `/api/v1/calculate/term-insurance` | Calculate term insurance needs | Yes | `{age, income, expenses, dependents, existing_cover, liabilities}` | `{recommended_cover, shortfall, monthly_premium_estimate}` |
| 70 | POST | `/api/v1/calculate/health-insurance` | Calculate health insurance needs | Yes | `{family_members[], city_tier, existing_policies[]}` | `{recommended_cover, family_floater, individual_covers[]}` |
| 71 | POST | `/api/v1/calculate/retirement` | Calculate retirement corpus | Yes | `{current_age, retirement_age, monthly_expenses, inflation_rate, existing_corpus}` | `{required_corpus, monthly_sip_10, monthly_sip_12, monthly_sip_15}` |
| 72 | POST | `/api/v1/calculate/child-education` | Calculate education corpus | Yes | `{children[], education_type, years_to_goal, cost_today, inflation}` | `{per_child_corpus[], total_required, monthly_sip_scenarios[]}` |
| 73 | POST | `/api/v1/calculate/child-wedding` | Calculate wedding corpus | Yes | `{children[], years_to_goal, cost_today, inflation}` | `{per_child_corpus[], total_required, monthly_sip_scenarios[]}` |
| 74 | POST | `/api/v1/calculate/home-purchase` | Calculate home purchase plan | Yes | `{property_cost, down_payment, years_to_purchase, income_sources[], loan_tenure, interest_rate}` | `{loan_eligibility, emi, down_payment_sip, shortfall_analysis}` |
| 75 | POST | `/api/v1/calculate/car-purchase` | Calculate car purchase plan | Yes | `{car_cost, down_payment, years_to_purchase, income_sources[], loan_tenure, interest_rate}` | `{loan_eligibility, emi, down_payment_sip}` |
| 76 | POST | `/api/v1/calculate/vacation` | Calculate vacation savings plan | Yes | `{vacations[{destination, travelers, date, cost}], inflation, return_rate}` | `{per_vacation_sip[], total_monthly_investment}` |
| 77 | POST | `/api/v1/calculate/tax-planning` | Calculate tax optimization | Yes | `{income_heads{}, deductions_80c{}, deductions_80d{}, regime}` | `{taxable_income, tax_liability, savings_suggestions}` |
| 78 | GET | `/api/v1/calculate/cache/{calculation_id}` | Get cached calculation | Yes | None | `{calculation_results}` |
| 79 | POST | `/api/v1/calculate/validate-inputs` | Validate calculation inputs | Yes | `{form_type, inputs{}}` | `{valid: boolean, errors[]}` |

## 6. REPORT SERVICE (Port: 8006)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|--------|-----------|----------|---------------|--------------|-----------|
| 80 | POST | `/api/v1/reports/generate` | Generate PDF report | Yes | `{form_type, submission_id, language}` | `{report_id, pdf_url}` |
| 81 | GET | `/api/v1/reports/my-reports` | Get report history | Yes | Query: `?page=1&form_type=` | `{reports[], pagination}` |
| 82 | GET | `/api/v1/reports/{report_id}` | Get report details | Yes | None | `{report_data}` |
| 83 | GET | `/api/v1/reports/{report_id}/download` | Download report PDF | Yes | None | PDF file |
| 84 | DELETE | `/api/v1/reports/{report_id}` | Delete report | Yes | None | `{message}` |
| 85 | POST | `/api/v1/reports/{report_id}/share` | Share report via email | Yes | `{recipient_email}` | `{message}` |
| 86 | GET | `/api/v1/reports/templates` | Get report templates | Admin | None | `{templates[]}` |
| 87 | POST | `/api/v1/reports/preview` | Preview report (no PDF) | Yes | `{form_type, submission_id}` | `{summary, charts_data}` |
| 88 | GET | `/api/v1/reports/statistics` | Get report statistics | Yes | None | `{total_generated, by_form_type{}}` |
| 89 | POST | `/api/v1/reports/bulk-delete` | Bulk delete expired reports | Admin | `{before_date}` | `{deleted_count}` |

## 7. FORM DATA SERVICE (Port: 8007)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|--------|-----------|----------|---------------|--------------|-----------|
| 90 | POST | `/api/v1/forms/submit` | Submit form data | Yes | `{form_type, client_name, form_data{}}` | `{submission_id, calculation_results}` |
| 91 | GET | `/api/v1/forms/submissions` | Get form submissions | Yes | Query: `?form_type=&page=1` | `{submissions[], pagination}` |
| 92 | GET | `/api/v1/forms/submission/{submission_id}` | Get submission details | Yes | None | `{submission_data}` |
| 93 | PUT | `/api/v1/forms/submission/{submission_id}` | Update submission | Yes | `{form_data{}}` | `{updated_submission}` |
| 94 | DELETE | `/api/v1/forms/submission/{submission_id}` | Delete submission | Yes | None | `{message}` |
| 95 | POST | `/api/v1/forms/draft/save` | Save form draft | Yes | `{form_type, draft_data{}}` | `{draft_id}` |
| 96 | GET | `/api/v1/forms/draft/{form_type}` | Get form draft | Yes | None | `{draft_data}` |
| 97 | DELETE | `/api/v1/forms/draft/{form_type}` | Delete form draft | Yes | None | `{message}` |
| 98 | GET | `/api/v1/forms/types` | Get available form types | Yes | None | `{form_types[]}` |
| 99 | GET | `/api/v1/forms/schema/{form_type}` | Get form schema (fields) | Yes | None | `{schema}` |

## 8. AFFILIATE SERVICE (Port: 8008)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|--------|-----------|----------|---------------|--------------|-----------|
| 100 | POST | `/api/v1/affiliates/apply` | Apply to become affiliate | Yes | `{company_name, bio, why_join}` | `{application_id, status}` |
| 101 | GET | `/api/v1/affiliates/application-status` | Check application status | Affiliate | None | `{status, review_notes}` |
| 102 | GET | `/api/v1/affiliates/dashboard` | Get affiliate dashboard data | Affiliate | None | `{stats, referrals_summary}` |
| 103 | GET | `/api/v1/affiliates/referrals` | Get referral list | Affiliate | Query: `?page=1&status=` | `{referrals[], pagination}` |
| 104 | GET | `/api/v1/affiliates/referral/{referral_id}` | Get referral details | Affiliate | None | `{referral_data}` |
| 105 | GET | `/api/v1/affiliates/commissions` | Get commission list | Affiliate | Query: `?status=&page=1` | `{commissions[], pagination}` |
| 106 | GET | `/api/v1/affiliates/commission/{commission_id}` | Get commission details | Affiliate | None | `{commission_data}` |
| 107 | GET | `/api/v1/affiliates/payouts` | Get payout history | Affiliate | None | `{payouts[]}` |
| 108 | GET | `/api/v1/affiliates/my-links` | Get referral links | Affiliate | None | `{referral_link, landing_page_url, qr_code}` |
| 109 | GET | `/api/v1/affiliates/landing-page` | Get landing page data | Affiliate | None | `{custom_content}` |
| 110 | PUT | `/api/v1/affiliates/landing-page` | Update landing page | Affiliate | `{headline, offer, message, cta_text}` | `{updated_content}` |
| 111 | POST | `/api/v1/affiliates/landing-page/photo` | Upload landing page photo | Affiliate | `multipart/form-data` | `{photo_url}` |
| 112 | POST | `/api/v1/affiliates/bank-account` | Add bank account | Affiliate | `{account_holder, bank_name, account_number, ifsc}` | `{account_id}` |
| 113 | GET | `/api/v1/affiliates/bank-accounts` | Get bank accounts | Affiliate | None | `{accounts[]}` |
| 114 | PUT | `/api/v1/affiliates/bank-account/{account_id}` | Update bank account | Affiliate | `{fields}` | `{updated_account}` |
| 115 | DELETE | `/api/v1/affiliates/bank-account/{account_id}` | Delete bank account | Affiliate | None | `{message}` |
| 116 | GET | `/api/v1/affiliates/marketing-assets` | Get marketing assets | Affiliate | None | `{videos[], images[], templates[]}` |
| 117 | GET | `/api/v1/affiliates/performance` | Get performance analytics | Affiliate | Query: `?from=&to=` | `{conversion_rate, revenue_generated}` |

## 9. ADMIN SERVICE (Port: 8009)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|--------|-----------|----------|---------------|--------------|-----------|
| 118 | GET | `/api/v1/admin/dashboard` | Get admin dashboard data | Admin | None | `{key_metrics, charts}` |
| 119 | GET | `/api/v1/admin/users` | Get all users | Admin | Query: `?type=&status=&page=1` | `{users[], pagination}` |
| 120 | GET | `/api/v1/admin/users/{user_id}/details` | Get user full details | Admin | None | `{user_data, subscription, payments, activity}` |
| 121 | PUT | `/api/v1/admin/users/{user_id}/profile` | Update user profile | Admin | `{any_field}` | `{updated_profile}` |
| 122 | POST | `/api/v1/admin/users/{user_id}/send-notification` | Send notification to user | Admin | `{type, message}` | `{sent}` |
| 123 | GET | `/api/v1/admin/profile-update-requests` | Get profile update requests | Admin | Query: `?status=` | `{requests[]}` |
| 124 | POST | `/api/v1/admin/profile-update-requests/{request_id}/approve` | Approve update request | Admin | None | `{approved}` |
| 125 | POST | `/api/v1/admin/profile-update-requests/{request_id}/reject` | Reject update request | Admin | `{reason}` | `{rejected}` |
| 126 | GET | `/api/v1/admin/affiliates/pending` | Get pending affiliate applications | Admin | None | `{applications[]}` |
| 127 | POST | `/api/v1/admin/affiliates/{affiliate_id}/approve` | Approve affiliate | Admin | `{commission_plan_id}` | `{approved, unique_code}` |
| 128 | POST | `/api/v1/admin/affiliates/{affiliate_id}/reject` | Reject affiliate | Admin | `{reason}` | `{rejected}` |
| 129 | POST | `/api/v1/admin/affiliates/create` | Create affiliate manually | Admin | `{email, name, mobile, commission_plan_id}` | `{affiliate_id, credentials}` |
| 130 | PUT | `/api/v1/admin/affiliates/{affiliate_id}/commission-plan` | Update affiliate commission plan | Admin | `{plan_id, custom_rate}` | `{updated}` |
| 131 | POST | `/api/v1/admin/affiliates/{affiliate_id}/suspend` | Suspend affiliate | Admin | `{reason}` | `{suspended}` |
| 132 | POST | `/api/v1/admin/affiliates/{affiliate_id}/reactivate` | Reactivate affiliate | Admin | None | `{reactivated}` |
| 133 | GET | `/api/v1/admin/commissions/pending` | Get pending commissions | Admin | Query: `?page=1` | `{commissions[], pagination}` |
| 134 | POST | `/api/v1/admin/commissions/{commission_id}/approve` | Approve commission | Admin | None | `{approved}` |
| 135 | POST | `/api/v1/admin/commissions/{commission_id}/reject` | Reject commission | Admin | `{reason}` | `{rejected}` |
| 136 | POST | `/api/v1/admin/commissions/{commission_id}/modify` | Modify commission amount | Admin | `{new_amount, reason}` | `{modified}` |
| 137 | POST | `/api/v1/admin/commissions/bulk-approve` | Bulk approve commissions | Admin | `{commission_ids[]}` | `{approved_count}` |
| 138 | GET | `/api/v1/admin/payouts/pending` | Get pending payouts | Admin | None | `{payouts_by_affiliate[]}` |
| 139 | POST | `/api/v1/admin/payouts/{affiliate_id}/process` | Process affiliate payout | Admin | `{amount, payment_method, transaction_id}` | `{payout_id}` |
| 140 | POST | `/api/v1/admin/payouts/bulk-process` | Bulk process payouts | Admin | `{affiliate_ids[]}` | `{processed_count}` |
| 141 | GET | `/api/v1/admin/subscription-tiers` | Get all tiers (for editing) | Admin | None | `{tiers[]}` |
| 142 | PUT | `/api/v1/admin/subscription-tiers/{tier_id}` | Update tier configuration | Admin | `{price, features[], report_limit}` | `{updated_tier}` |
| 143 | POST | `/api/v1/admin/subscription-tiers` | Create new tier | Admin | `{tier_data}` | `{tier_id}` |
| 144 | DELETE | `/api/v1/admin/subscription-tiers/{tier_id}` | Deactivate tier | Admin | None | `{deactivated}` |
| 145 | GET | `/api/v1/admin/commission-plans` | Get all commission plans | Admin | None | `{plans[]}` |
| 146 | POST | `/api/v1/admin/commission-plans` | Create commission plan | Admin | `{plan_data}` | `{plan_id}` |
| 147 | PUT | `/api/v1/admin/commission-plans/{plan_id}` | Update commission plan | Admin | `{plan_data}` | `{updated_plan}` |
| 148 | GET | `/api/v1/admin/analytics/overview` | Get overall analytics | Admin | Query: `?from=&to=` | `{revenue, users, reports, conversions}` |
| 149 | GET | `/api/v1/admin/analytics/revenue` | Get revenue analytics | Admin | Query: `?from=&to=&breakdown=` | `{revenue_data, charts}` |
| 150 | GET | `/api/v1/admin/analytics/affiliates` | Get affiliate performance | Admin | Query: `?from=&to=` | `{top_affiliates[], metrics}` |
| 151 | GET | `/api/v1/admin/analytics/reports` | Get report generation analytics | Admin | Query: `?from=&to=` | `{by_form_type, by_tier}` |
| 152 | GET | `/api/v1/admin/analytics/conversions` | Get conversion analytics | Admin | Query: `?from=&to=` | `{trial_to_paid, funnel_data}` |
| 153 | GET | `/api/v1/admin/audit-logs` | Get audit logs | Admin | Query: `?user_id=&action=&page=1` | `{logs[], pagination}` |
| 154 | GET | `/api/v1/admin/system-config` | Get system configuration | Admin | None | `{configs{}}` |
| 155 | PUT | `/api/v1/admin/system-config` | Update system config | Admin | `{key, value}` | `{updated}` |
| 156 | GET | `/api/v1/admin/feature-flags` | Get feature flags | Admin | None | `{flags[]}` |
| 157 | PUT | `/api/v1/admin/feature-flags/{flag_key}` | Toggle feature flag | Admin | `{enabled: boolean}` | `{updated}` |

## 10. NOTIFICATION SERVICE (Port: 8010)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|--------|-----------|----------|---------------|--------------|-----------|
| 158 | POST | `/api/v1/notifications/send-email` | Send email (internal) | Internal | `{to, template_key, variables{}, language}` | `{sent, notification_id}` |
| 159 | POST | `/api/v1/notifications/send-sms` | Send SMS (internal) | Internal | `{to, message, language}` | `{sent, notification_id}` |
| 160 | GET | `/api/v1/notifications/templates` | Get all templates | Admin | Query: `?type=&language=` | `{templates[]}` |
| 161 | GET | `/api/v1/notifications/template/{template_key}` | Get template | Admin | Query: `?language=` | `{template_data}` |
| 162 | PUT | `/api/v1/notifications/template/{template_key}` | Update template | Admin | `{subject, body_text, body_html}` | `{updated}` |
| 163 | POST | `/api/v1/notifications/test-email` | Test email template | Admin | `{template_key, test_email, variables{}}` | `{sent}` |
| 164 | GET | `/api/v1/notifications/queue` | Get notification queue | Admin | Query: `?status=` | `{queue[], pagination}` |
| 165 | POST | `/api/v1/notifications/queue/{notification_id}/retry` | Retry failed notification | Admin | None | `{retried}` |
| 166 | GET | `/api/v1/notifications/my-notifications` | Get user notifications | Yes | Query: `?page=1` | `{notifications[], pagination}` |
| 167 | PUT | `/api/v1/notifications/{notification_id}/read` | Mark as read | Yes | None | `{updated}` |
| 168 | GET | `/api/v1/notifications/preferences` | Get notification preferences | Yes | None | `{email_enabled, sms_enabled}` |
| 169 | PUT | `/api/v1/notifications/preferences` | Update preferences | Yes | `{email_enabled, sms_enabled}` | `{updated}` |

## 11. STORAGE SERVICE (Port: 8011)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|--------|-----------|----------|---------------|--------------|-----------|
| 170 | POST | `/api/v1/storage/upload` | Upload file | Yes | `multipart/form-data` | `{file_id, url}` |
| 171 | GET | `/api/v1/storage/file/{file_id}` | Get file URL | Yes | None | `{url, expires_in}` |
| 172 | GET | `/api/v1/storage/download/{file_id}` | Download file | Yes | None | File stream |
| 173 | DELETE | `/api/v1/storage/file/{file_id}` | Delete file | Yes | None | `{deleted}` |
| 174 | POST | `/api/v1/storage/generate-presigned-url` | Generate presigned upload URL | Yes | `{filename, file_type}` | `{upload_url, file_id}` |
| 175 | GET | `/api/v1/storage/my-files` | Get user files | Yes | Query: `?type=&page=1` | `{files[], pagination}` |
| 176 | POST | `/api/v1/storage/cleanup-expired` | Cleanup expired files (internal) | Internal | None | `{deleted_count}` |

## 12. I18N SERVICE (Port: 8012)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|--------|-----------|----------|---------------|--------------|-----------|
| 177 | GET | `/api/v1/i18n/languages` | Get supported languages | No | None | `{languages[]}` |
| 178 | GET | `/api/v1/i18n/translations/{language}` | Get all translations for language | No | Query: `?module=` | `{translations{}}` |
| 179 | GET | `/api/v1/i18n/translate` | Translate key | No | Query: `?key=&lang=` | `{translation}` |
| 180 | POST | `/api/v1/i18n/translations` | Add/Update translation (admin) | Admin | `{key, language, value, module}` | `{updated}` |
| 181 | DELETE | `/api/v1/i18n/translations/{key}` | Delete translation (admin) | Admin | Query: `?language=` | `{deleted}` |
| 182 | POST | `/api/v1/i18n/languages` | Add new language (admin) | Admin | `{language_code, name, native_name}` | `{language_id}` |
| 183 | PUT | `/api/v1/i18n/languages/{language_code}` | Update language (admin) | Admin | `{is_active, display_order}` | `{updated}` |
| 184 | GET | `/api/v1/i18n/missing-translations` | Get missing translations (admin) | Admin | Query: `?language=` | `{missing_keys[]}` |
| 185 | POST | `/api/v1/i18n/export` | Export translations (admin) | Admin | `{language, format}` | JSON/CSV file |
| 186 | POST | `/api/v1/i18n/import` | Import translations (admin) | Admin | `multipart/form-data` | `{imported_count}` |

## 13. PRO TIER FEATURES SERVICE (Port: 8013)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|--------|-----------|----------|---------------|--------------|-----------|
| 187 | POST | `/api/v1/pro/financial-horoscope/generate` | Generate financial horoscope | Pro | `{comprehensive_financial_data}` | `{horoscope_id, scores{}, top_5_actions[]}` |
| 188 | GET | `/api/v1/pro/financial-horoscope/{horoscope_id}` | Get horoscope details | Pro | None | `{horoscope_data}` |
| 189 | GET | `/api/v1/pro/financial-horoscope/my-horoscopes` | Get user's horoscopes | Pro | None | `{horoscopes[]}` |
| 190 | POST | `/api/v1/pro/planning-session/create` | Create 1-on-1 planning session | Pro | `{client_id, horoscope_id}` | `{session_id}` |
| 191 | GET | `/api/v1/pro/planning-session/{session_id}` | Get session data | Pro | None | `{session_data, goals[], risk_data}` |
| 192 | PUT | `/api/v1/pro/planning-session/{session_id}/goals` | Update session goals | Pro | `{goals[]}` | `{updated_goals}` |
| 193 | POST | `/api/v1/pro/planning-session/{session_id}/goals/{goal_id}` | Add/update specific goal | Pro | `{goal_data}` | `{goal_id}` |
| 194 | DELETE | `/api/v1/pro/planning-session/{session_id}/goals/{goal_id}` | Remove goal | Pro | None | `{deleted}` |
| 195 | PUT | `/api/v1/pro/planning-session/{session_id}/risk-management` | Update risk management | Pro | `{risk_data}` | `{updated}` |
| 196 | PUT | `/api/v1/pro/planning-session/{session_id}/customize` | Customize session pages | Pro | `{page_id, custom_data}` | `{updated}` |
| 197 | POST | `/api/v1/pro/planning-session/{session_id}/generate-summary` | Generate 1-pager summary | Pro | None | `{summary_pdf_url}` |
| 198 | GET | `/api/v1/pro/planning-session/my-sessions` | Get all planning sessions | Pro | None | `{sessions[]}` |
| 199 | GET | `/api/v1/pro/clients` | Get clients (from horoscopes) | Pro | None | `{clients[]}` |
| 200 | GET | `/api/v1/pro/client/{client_id}/dashboard` | Get client dashboard | Pro | None | `{horoscope, sessions[], reports[]}` |
---

📘 **Total Endpoints:** 200  
📡 **Microservices:** 13  
🧩 **Architecture:** Modular REST API with JWT, Role-based Access, and Multi-Tenant Support  

---

© 2025 **SalahkaarPro API Documentation**
