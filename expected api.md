# 🧠 SalahkaarPro: Complete API Endpoints Reference

This document provides the full reference of SalahkaarPro’s backend microservices and their API endpoints.

---

## ⚙️ 1. AUTH SERVICE (Port: 8001)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|---------|-----------|----------|----------------|---------------|------------|
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

---

## 👤 2. USER SERVICE (Port: 8002)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|---------|-----------|----------|----------------|---------------|------------|
| 15 | GET | `/api/v1/users/profile` | Get user profile | Yes | None | `{profile_data}` |
| 16 | PUT | `/api/v1/users/profile` | Update profile (allowed fields) | Yes | `{mobile, email}` | `{updated_profile}` |
| 17 | POST | `/api/v1/users/profile/photo` | Upload profile photo | Yes | multipart/form-data | `{photo_url}` |
| 18 | POST | `/api/v1/users/profile/logo` | Upload logo | Yes | multipart/form-data | `{logo_url}` |
| 19 | DELETE | `/api/v1/users/profile/photo` | Delete profile photo | Yes | None | `{message}` |
| 20 | DELETE | `/api/v1/users/profile/logo` | Delete logo | Yes | None | `{message}` |
| 21 | GET | `/api/v1/users/grace-period-status` | Check grace period status | Yes | None | `{in_grace_period, expires_at}` |
| 22 | POST | `/api/v1/users/profile/lock` | Manually lock profile | Yes | None | `{message}` |
| 23 | POST | `/api/v1/users/profile/update-request` | Request critical field update | Yes | `{field_name, new_value, reason}` | `{request_id, status}` |
| 24 | GET | `/api/v1/users/profile/update-requests` | Get pending update requests | Yes | None | `[{request_id, field, status}]` |
| 25 | GET | `/api/v1/users/activity-log` | Get user activity log | Yes | `?page=1&limit=20` | `{activities[], pagination}` |
| 26 | GET | `/api/v1/users/dashboard-stats` | Get dashboard statistics | Yes | None | `{reports_used, reports_remaining, subscription_status}` |
| 27 | GET | `/api/v1/users/search` | Search users (admin only) | Admin | `?q=&type=&status=` | `{users[], pagination}` |
| 28 | GET | `/api/v1/users/{user_id}` | Get user by ID (admin only) | Admin | None | `{user_data}` |

---

## 💳 3. SUBSCRIPTION SERVICE (Port: 8003)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|---------|-----------|----------|----------------|---------------|------------|
| 33 | GET | `/api/v1/subscriptions/tiers` | Get all subscription tiers | No | None | `[{tier_name, price, features}]` |
| 35 | GET | `/api/v1/subscriptions/my-subscription` | Get current subscription | Yes | None | `{subscription_details}` |
| 36 | POST | `/api/v1/subscriptions/trial/activate` | Activate free trial | Yes | None | `{trial_details, expires_at}` |
| 38 | POST | `/api/v1/subscriptions/subscribe` | Subscribe to paid tier | Yes | `{tier_id, payment_method}` | `{subscription_id, payment_url}` |
| 41 | POST | `/api/v1/subscriptions/renew` | Renew subscription | Yes | `{tier_id}` | `{payment_url}` |
| 42 | POST | `/api/v1/subscriptions/cancel` | Cancel subscription | Yes | `{reason}` | `{cancellation_date}` |

---

## 💰 4. PAYMENT SERVICE (Port: 8004)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|---------|-----------|----------|----------------|---------------|------------|
| 53 | POST | `/api/v1/payments/create-order` | Create payment order | Yes | `{subscription_id, tier_id, amount}` | `{order_id, payment_url}` |
| 54 | POST | `/api/v1/payments/verify` | Verify payment | Yes | `{order_id, payment_id, signature}` | `{verified, transaction_id}` |
| 57 | GET | `/api/v1/payments/my-payments` | Get payment history | Yes | `?page=1` | `{payments[], pagination}` |
| 60 | POST | `/api/v1/payments/refund/request` | Request refund | Yes | `{payment_id, reason}` | `{refund_request_id}` |

---

## 📊 5. CALCULATION SERVICE (Port: 8005)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|---------|-----------|----------|----------------|---------------|------------|
| 69 | POST | `/api/v1/calculate/term-insurance` | Calculate term insurance | Yes | `{age, income, expenses, dependents, existing_cover, liabilities}` | `{recommended_cover, shortfall, monthly_premium_estimate}` |
| 70 | POST | `/api/v1/calculate/health-insurance` | Calculate health insurance | Yes | `{family_members[], city_tier, existing_policies[]}` | `{recommended_cover, family_floater, individual_covers[]}` |
| 71 | POST | `/api/v1/calculate/retirement` | Calculate retirement corpus | Yes | `{current_age, retirement_age, monthly_expenses, inflation_rate, existing_corpus}` | `{required_corpus, monthly_sip_10, monthly_sip_12, monthly_sip_15}` |

---

## 📄 6. REPORT SERVICE (Port: 8006)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|---------|-----------|----------|----------------|---------------|------------|
| 80 | POST | `/api/v1/reports/generate` | Generate PDF report | Yes | `{form_type, submission_id, language}` | `{report_id, pdf_url}` |
| 81 | GET | `/api/v1/reports/my-reports` | Get report history | Yes | `?page=1&form_type=` | `{reports[], pagination}` |
| 83 | GET | `/api/v1/reports/{report_id}/download` | Download report PDF | Yes | None | `PDF file` |

---

## 📦 7. FORM DATA SERVICE (Port: 8007)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|---------|-----------|----------|----------------|---------------|------------|
| 90 | POST | `/api/v1/forms/submit` | Submit form data | Yes | `{form_type, client_name, form_data{}}` | `{submission_id, calculation_results}` |
| 91 | GET | `/api/v1/forms/submissions` | Get form submissions | Yes | `?form_type=&page=1` | `{submissions[], pagination}` |
| 92 | GET | `/api/v1/forms/submission/{submission_id}` | Get submission details | Yes | None | `{submission_data}` |

---

## 🤝 8. AFFILIATE SERVICE (Port: 8008)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|---------|-----------|----------|----------------|---------------|------------|
| 100 | POST | `/api/v1/affiliates/apply` | Apply to become affiliate | Yes | `{company_name, bio, why_join}` | `{application_id, status}` |
| 102 | GET | `/api/v1/affiliates/dashboard` | Get affiliate dashboard data | Affiliate | None | `{stats, referrals_summary}` |
| 108 | GET | `/api/v1/affiliates/my-links` | Get referral links | Affiliate | None | `{referral_link, landing_page_url, qr_code}` |

---

## 🛠️ 9. ADMIN SERVICE (Port: 8009)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|---------|-----------|----------|----------------|---------------|------------|
| 118 | GET | `/api/v1/admin/dashboard` | Get admin dashboard data | Admin | None | `{key_metrics, charts}` |
| 119 | GET | `/api/v1/admin/users` | Get all users | Admin | `?type=&status=&page=1` | `{users[], pagination}` |
| 127 | POST | `/api/v1/admin/affiliates/{affiliate_id}/approve` | Approve affiliate | Admin | `{commission_plan_id}` | `{approved, unique_code}` |
| 141 | GET | `/api/v1/admin/subscription-tiers` | Get all tiers (for editing) | Admin | None | `{tiers[]}` |

---

## 🔔 10. NOTIFICATION SERVICE (Port: 8010)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|---------|-----------|----------|----------------|---------------|------------|
| 158 | POST | `/api/v1/notifications/send-email` | Send email (internal) | Internal | `{to, template_key, variables{}, language}` | `{sent, notification_id}` |
| 166 | GET | `/api/v1/notifications/my-notifications` | Get user notifications | Yes | `?page=1` | `{notifications[], pagination}` |
| 169 | PUT | `/api/v1/notifications/preferences` | Update preferences | Yes | `{email_enabled, sms_enabled}` | `{updated}` |

---

## 🗂️ 11. STORAGE SERVICE (Port: 8011)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|---------|-----------|----------|----------------|---------------|------------|
| 170 | POST | `/api/v1/storage/upload` | Upload file | Yes | multipart/form-data | `{file_id, url}` |
| 172 | GET | `/api/v1/storage/download/{file_id}` | Download file | Yes | None | File stream |
| 173 | DELETE | `/api/v1/storage/file/{file_id}` | Delete file | Yes | None | `{deleted}` |

---

## 🌐 12. I18N SERVICE (Port: 8012)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|---------|-----------|----------|----------------|---------------|------------|
| 177 | GET | `/api/v1/i18n/languages` | Get supported languages | No | None | `{languages[]}` |
| 179 | GET | `/api/v1/i18n/translate` | Translate key | No | `?key=&lang=` | `{translation}` |
| 185 | POST | `/api/v1/i18n/export` | Export translations | Admin | `{language, format}` | JSON/CSV file |

---

## 💼 13. PRO TIER FEATURES SERVICE (Port: 8013)

| # | Method | Endpoint | Purpose | Auth Required | Request Body | Response |
|---|---------|-----------|----------|----------------|---------------|------------|
| 187 | POST | `/api/v1/pro/financial-horoscope/generate` | Generate financial horoscope | Pro | `{comprehensive_financial_data}` | `{horoscope_id, scores{}, top_5_actions[]}` |
| 190 | POST | `/api/v1/pro/planning-session/create` | Create 1-on-1 planning session | Pro | `{client_id, horoscope_id}` | `{session_id}` |
| 197 | POST | `/api/v1/pro/planning-session/{session_id}/generate-summary` | Generate 1-pager summary | Pro | None | `{summary_pdf_url}` |

---

📘 **Total Endpoints:** 200  
📡 **Microservices:** 13  
🧩 **Architecture:** Modular REST API with JWT, Role-based Access, and Multi-Tenant Support  

---

© 2025 **SalahkaarPro API Documentation**
