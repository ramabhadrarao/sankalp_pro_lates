┌─────────────────────────────────────────────────────────────┐
│                     USER ECOSYSTEM                          │
│                                                             │
│  ┌─────────────┐      ┌─────────────┐      ┌────────────┐ │
│  │   MASTER    │      │  AFFILIATE  │      │  ADVISOR   │ │
│  │   ADMIN     │◄────►│    USER     │◄────►│   USER     │ │
│  │ (Platform)  │      │ (Promoter)  │      │ (End User) │ │
│  └─────────────┘      └─────────────┘      └────────────┘ │
│        │                     │                    │        │
│        │                     │                    │        │
│   Manages all          Earns commission      Generates     │
│   Approves/Rejects     Customizes page       Reports       │
│   Sets commissions     Tracks referrals      Pays for      │
│   Processes payments   Views dashboard       Subscription  │
└─────────────────────────────────────────────────────────────┘
```

---

## **3. AFFILIATE USER COMPLETE WORKFLOW**

### **Phase 1: Affiliate Onboarding**

#### **Entry Points (2 Methods)**

**Method A: Admin Adds Affiliate**
```
Master Admin Panel
    ↓
"Add New Affiliate" Section
    ↓
Admin enters:
  - Name
  - Email
  - Mobile
  - Photo/Logo
  - Bio/Description
  - Initial Commission Rate (optional, defaults to tier structure)
    ↓
System automatically:
  - Creates affiliate account
  - Generates unique ID (e.g., AFF_12345)
  - Sends welcome email with credentials
  - Status: "Approved" (immediate access)
    ↓
Affiliate receives email with:
  - Login credentials
  - Dashboard access link
  - Getting started guide
```

**Method B: Affiliate Self-Signup**
```
Main Website
    ↓
"Become an Affiliate" Page
    ↓
Affiliate fills form:
  - Name
  - Email
  - Mobile
  - Company/Organization (optional)
  - Why you want to join (text area)
  - Agreement to terms checkbox
    ↓
System creates account:
  - Status: "Pending Approval"
  - Sends notification to admin
  - Sends confirmation email to affiliate
    ↓
Affiliate waits for approval
    ↓
Admin reviews in "Pending Affiliates" section:
  - View application details
  - Approve or Reject
    ↓
If Approved:
  - Status: "Approved"
  - Unique ID generated
  - Email sent with credentials
  - Affiliate can access dashboard
    ↓
If Rejected:
  - Status: "Rejected"
  - Rejection email sent with reason
  - Account remains inactive
```

### **Phase 2: Affiliate Dashboard Access**

**Dashboard Components:**
```
AFFILIATE DASHBOARD
│
├── Overview Section
│   ├── Total Referrals (count)
│   ├── Active Advisors (from referrals)
│   ├── Total Commission Earned (₹)
│   ├── Pending Commission (₹)
│   ├── Paid Commission (₹)
│   └── This Month Performance
│
├── Referral Management
│   ├── Unique Referral Link (with copy button)
│   │   Example: salahkaarpro.com/ref/AFF_12345
│   ├── Landing Page Link (if customized)
│   │   Example: salahkaarpro.com/partners/AFF_12345
│   └── QR Code for link sharing
│
├── Landing Page Customization
│   ├── Preview current page
│   ├── Edit custom fields:
│   │   ├── Headline text
│   │   ├── Special offer text
│   │   ├── Your photo/logo upload
│   │   ├── Bio/description
│   │   └── Custom message
│   ├── Save & Publish
│   └── View Live Page button
│
├── Referral List Table
│   ├── Advisor Name
│   ├── Signup Date
│   ├── Subscription Tier
│   ├── Subscription Status (Trial/Active/Expired)
│   ├── Commission Amount
│   ├── Commission Status (Pending/Approved/Paid)
│   └── Actions (View Details)
│
├── Commission Dashboard
│   ├── Commission Plan Details (assigned by admin)
│   │   ├── Tier 1: 20% (₹0 - ₹1,00,000)
│   │   ├── Tier 2: 25% (₹1,00,001 - ₹2,00,000)
│   │   ├── Tier 3: 30% (₹2,00,001 - ₹4,00,000)
│   │   ├── Tier 4: 40% (Above ₹4,00,001)
│   │   └── Renewal: 10% (Lifetime)
│   ├── Custom Rate (if admin overrode)
│   ├── Commission Breakdown (charts)
│   │   ├── By Month
│   │   ├── By Advisor Tier
│   │   └── New vs Renewal
│   └── Commission Transactions Table
│       ├── Date
│       ├── Advisor Name
│       ├── Transaction Type (New/Renewal)
│       ├── Amount
│       ├── Commission Rate
│       ├── Commission Earned
│       ├── Status (Pending/Approved/Rejected/Paid)
│       └── Payment Date
│
├── Payout History
│   ├── Payout Date
│   ├── Amount
│   ├── Payment Method
│   ├── Transaction ID
│   └── Invoice Download
│
├── Marketing Assets
│   ├── Promotional Videos
│   ├── Banner Images
│   ├── Email Templates
│   ├── Social Media Graphics
│   └── Demo Account Access
│
└── Profile Settings
    ├── Update personal info
    ├── Bank account details (for payouts)
    ├── Tax information (PAN, GST if applicable)
    └── Change password
```

### **Phase 3: Commission Flow (Detailed)**

#### **Step 1: Advisor Signup via Affiliate**
```
User clicks affiliate link/lands on custom page
    ↓
URL contains: ?ref=AFF_12345
    ↓
User completes signup
    ↓
System records in database:
  - referrals table: (affiliate_id: AFF_12345, advisor_id: ADV_67890, signup_date, status: "trial")
    ↓
Affiliate sees in dashboard:
  - New entry in "Referral List"
  - Status: "Trial" (3 days, 5 reports)
  - Commission: "Pending Conversion"
```

#### **Step 2: Advisor Purchases Subscription**
```
Advisor completes trial
    ↓
Chooses subscription tier (e.g., Starter+ at ₹4,499)
    ↓
Payment successful
    ↓
System calculates:
  - Payment amount: ₹4,499
  - Less GST (18%): ₹679.82
  - Less payment gateway fee (2%): ₹89.98
  - Net amount: ₹3,729.20
  - Affiliate's commission tier: 20% (assuming first ₹1L revenue)
  - Commission amount: ₹3,729.20 × 20% = ₹745.84
    ↓
System creates commission record:
  - commissions table:
    {
      affiliate_id: AFF_12345,
      advisor_id: ADV_67890,
      transaction_type: "new_subscription",
      subscription_tier: "Starter+",
      gross_amount: 4499,
      net_amount: 3729.20,
      commission_rate: 20%,
      commission_amount: 745.84,
      status: "pending_approval",
      created_at: timestamp
    }
    ↓
Affiliate dashboard updates:
  - Total Commission Earned: +₹745.84 (in "Pending" status)
  - Referral status: "Active Subscriber"
```

#### **Step 3: Admin Reviews Commission**
```
Master Admin Panel
    ↓
"Commission Management" Section
    ↓
Sees pending commission:
  - Affiliate: John Doe (AFF_12345)
  - Advisor: Rajesh Kumar (ADV_67890)
  - Amount: ₹745.84
  - Status: Pending Approval
    ↓
Admin actions:
  ┌─────────────────┬─────────────────┬──────────────────┐
  │   APPROVE       │    REJECT       │   MODIFY         │
  └─────────────────┴─────────────────┴──────────────────┘
```

**Action: APPROVE**
```
Admin clicks "Approve"
    ↓
System updates:
  - status: "approved"
  - approved_by: admin_id
  - approved_at: timestamp
    ↓
Affiliate dashboard shows:
  - Status: "Approved"
  - Eligible for next payout cycle
    ↓
Email sent to affiliate:
  "Your commission of ₹745.84 has been approved and will be paid on [payout_date]"
```

**Action: REJECT**
```
Admin clicks "Reject"
    ↓
Modal opens: "Reason for rejection" (required field)
    ↓
Admin enters reason: "Suspected fraudulent referral"
    ↓
System updates:
  - status: "rejected"
  - rejected_by: admin_id
  - rejected_at: timestamp
  - rejection_reason: "Suspected fraudulent referral"
    ↓
Affiliate dashboard shows:
  - Status: "Rejected"
  - Commission amount deducted from pending
    ↓
Email sent to affiliate:
  "Your commission has been rejected. Reason: [reason]"
```

**Action: MODIFY**
```
Admin clicks "Modify"
    ↓
Modal opens with fields:
  - Current commission amount: ₹745.84
  - New commission amount: [editable]
  - Reason for modification: [text area]
    ↓
Admin changes to: ₹600.00
Reason: "Negotiated custom rate for this referral"
    ↓
System updates:
  - commission_amount: 600.00
  - original_amount: 745.84
  - modified_by: admin_id
  - modification_reason: "Negotiated custom rate..."
  - status: "modified_approved"
    ↓
Affiliate dashboard shows:
  - Commission: ₹600.00 (Modified)
  - Original: ₹745.84
  - Can view modification reason
```

#### **Step 4: Monthly Payout Processing**
```
End of month (automated job)
    ↓
System aggregates all "approved" commissions:
  - Filters: status = "approved" AND payout_status = "pending"
    ↓
Groups by affiliate_id:
  - AFF_12345: Total ₹15,450.00 (20 referrals)
    ↓
Admin reviews payout queue:
  - "Process Payouts" section
  - List of affiliates with amounts
    ↓
Admin actions:
  ┌────────────────────────┬──────────────────────┐
  │  PROCESS INDIVIDUAL    │   BULK PROCESS       │
  │  (for testing/manual)  │   (all at once)      │
  └────────────────────────┴──────────────────────┘
```

**Manual Processing:**
```
Admin clicks "Process Payment" for AFF_12345
    ↓
Modal shows:
  - Affiliate: John Doe
  - Bank Account: HDFC Bank - ****5678
  - Amount: ₹15,450.00
  - Payment method: [NEFT/RTGS/UPI]
    ↓
Admin confirms
    ↓
System updates:
  - All related commissions: payout_status = "paid"
  - payout_date: timestamp
  - payment_reference: generated_id
    ↓
System creates payout record:
  - payouts table:
    {
      affiliate_id: AFF_12345,
      amount: 15450.00,
      payment_method: "NEFT",
      transaction_id: "PAY_ABC123",
      processed_by: admin_id,
      processed_at: timestamp
    }
    ↓
Affiliate dashboard updates:
  - Payout History: New entry
  - Pending Commission: -₹15,450.00
  - Paid Commission: +₹15,450.00
    ↓
Email & SMS sent:
  "Your commission of ₹15,450 has been processed. Check your bank account."
```

**Future: Auto-Payment Integration**
```
Admin enables auto-payout in settings
    ↓
Integrates with Razorpay Payouts API
    ↓
Monthly job runs automatically:
  - Fetches all approved commissions
  - Groups by affiliate
  - Initiates payouts via API
  - Updates status automatically
  - Sends notifications
    ↓
Admin only reviews exceptions/failures
```

#### **Step 5: Renewal Commission (Lifetime)**
```
Year later: Advisor renews Starter+ subscription
    ↓
Payment: ₹4,499
Net amount: ₹3,729.20
Renewal commission rate: 10% (fixed)
Commission: ₹372.92
    ↓
System creates new commission record:
  - transaction_type: "renewal"
  - commission_rate: 10%
  - commission_amount: 372.92
  - status: "pending_approval"
    ↓
Same approval workflow as above
    ↓
This continues for lifetime of advisor
```

### **Phase 4: Landing Page Customization**

**Affiliate Dashboard → "Customize Landing Page"**
```
┌──────────────────────────────────────────────────────┐
│         LANDING PAGE CUSTOMIZATION                   │
│                                                      │
│  Preview Panel          │     Edit Panel            │
│  (Live Preview)         │                           │
│  ┌──────────────────┐  │  Headline Text:           │
│  │  [Your Photo]    │  │  ┌─────────────────────┐  │
│  │                  │  │  │ "Transform Your     │  │
│  │  John Doe        │  │  │  Advisory Practice" │  │
│  │  Financial Coach │  │  └─────────────────────┘  │
│  │                  │  │                           │
│  │  [Custom Text]   │  │  Special Offer:           │
│  │  "Join 500+..."  │  │  ┌─────────────────────┐  │
│  │                  │  │  │ "Get 20% OFF..."    │  │
│  │  [See Plans CTA] │  │  └─────────────────────┘  │
│  └──────────────────┘  │                           │
│                        │  Your Bio:                │
│  Your Landing Page:    │  ┌─────────────────────┐  │
│  salahkaarpro.com/    │  │ "I help advisors..." │  │
│  partners/AFF_12345    │  └─────────────────────┘  │
│                        │                           │
│  [Copy Link] [QR Code] │  Upload Photo:            │
│                        │  [Choose File] (Max 2MB)  │
│                        │                           │
│                        │  Upload Logo:             │
│                        │  [Choose File] (Max 1MB)  │
│                        │                           │
│                        │  [Save Changes] [Preview] │
└──────────────────────────────────────────────────────┘
```

**Dynamic Landing Page Rendering:**
```
User visits: salahkaarpro.com/partners/AFF_12345
    ↓
Frontend detects affiliate ID from URL
    ↓
API call: GET /api/affiliates/AFF_12345/landing-page
    ↓
Backend returns:
{
  "affiliate_id": "AFF_12345",
  "name": "John Doe",
  "photo_url": "https://cdn.../john.jpg",
  "logo_url": "https://cdn.../logo.png",
  "custom_headline": "Transform Your Advisory Practice",
  "special_offer": "Get 20% OFF on Pro Plan",
  "bio": "I help advisors scale their business...",
  "cta_text": "Start Your Free Trial"
}
    ↓
Frontend renders landing page with:
  - Hero section with custom headline
  - Affiliate's photo and bio
  - Special offer banner
  - CTA button linking to: /signup?ref=AFF_12345
    ↓
Conversion tracking begins
```

---

## **4. ADVISOR USER COMPLETE WORKFLOW**

### **Entry Points (3 Methods)**

**Method A: Direct from Main Website**
```
salahkaarpro.com homepage
    ↓
Clicks "Book Free 3-Day Trial"
    ↓
Registration form (no ref parameter)
    ↓
System tracks: source = "organic"
```

**Method B: Via Affiliate Landing Page**
```
salahkaarpro.com/partners/AFF_12345
    ↓
Clicks "Start Your Free Trial" CTA
    ↓
Redirected to: /signup?ref=AFF_12345
    ↓
System tracks: source = "affiliate", affiliate_id = AFF_12345
```

**Method C: Via Affiliate Direct Link**
```
Affiliate shares: salahkaarpro.com/ref/AFF_12345
    ↓
User clicks link
    ↓
Redirected to: /signup?ref=AFF_12345
    ↓
System tracks: source = "affiliate", affiliate_id = AFF_12345
```

### **Registration & Trial Phase**
```
SIGNUP FORM
│
├── Personal Information
│   ├── Full Name*
│   ├── Email* (verification required)
│   ├── Mobile Number* (10-digit)
│   ├── Gender
│   └── Date of Birth (min age: 23)
│
├── Professional Information
│   ├── Organization Name*
│   ├── Role/Designation*
│   ├── City of Residence*
│   └── City Tier (removed as per update)
│
├── Optional Branding
│   ├── Upload Photo (max 2MB)
│   └── Upload Logo (max 1MB)
│   └── Note: "Photos/logos visible only on Pro tier reports"
│
├── Legal Agreements*
│   ├── ☐ I agree to Terms & Conditions (clickable)
│   ├── ☐ I have read the Privacy Policy (clickable)
│   └── Note: "By registering, you accept our Refund Policy"
│
└── [Start Free Trial] Button
    ↓
Email verification sent
    ↓
User clicks verification link
    ↓
Account created with:
  - Status: "trial"
  - Tier: "Starter" (temporary)
  - Report limit: 5
  - Expiry: 3 days from activation
  - Grace period: 72 hours (for name/org/role edits)
    ↓
Welcome email sent with:
  - Dashboard access instructions
  - Quick start guide
  - Video tutorials
```

### **Trial Period Experience**
```
USER DASHBOARD (Trial)
│
├── Trial Banner (prominent)
│   "Trial Active: 2 days remaining | 3/5 reports used"
│   [Upgrade to Paid Plan]
│
├── Full Access to All Features:
│   ├── All 8 report forms accessible
│   ├── Financial Horoscope (Pro feature preview)
│   ├── 1-on-1 Interface (Pro feature preview)
│   └── All calculators and tools
│
├── Report Generation
│   ├── Select any form
│   ├── Fill client data
│   ├── View calculation summary (modal)
│   ├── Generate PDF (deducts from 5-report limit)
│   └── Download report
│
└── Trial End Scenarios:
    ├── 5 reports used before 3 days:
    │   → Immediate upgrade prompt
    │   → Report generation locked
    │
    └── 3 days expire:
        → Account status: "trial_expired"
        → All features locked
        → Upgrade prompt modal
```

### **Subscription Purchase Phase**
```
User clicks "Upgrade to Paid Plan"
    ↓
PRICING PAGE (7 Tiers)
│
├── Basic (₹1,999) - 50 reports
├── Starter (₹3,499) - 100 reports
├── Starter+ (₹4,499) - 150 reports + Form selection*
├── Specialist (₹5,999) - 200 reports
├── Specialist+ (₹7,999) - 250 reports + Form selection*
├── Pro (₹12,499) - 1,000 reports + Full features
└── Enterprise (Custom) - Unlimited
    ↓
User selects tier
    ↓
IF Starter+ or Specialist+:
  ┌─────────────────────────────────────┐
  │     FORM SELECTION MODAL            │
  │                                     │
  │  Select 2 forms (Starter+)          │
  │  or 3 forms (Specialist+):          │
  │                                     │
  │  ☐ Term Insurance                   │
  │  ☐ Health Insurance                 │
  │  ☐ Retirement Planning              │
  │  ☐ Child Education                  │
  │  ☐ Child Wedding                    │
  │  ☐ Home Purchase                    │
  │  ☐ Car Purchase                     │
  │  ☐ Vacation Planning                │
  │                                     │
  │  ⚠️ Warning: Form selection cannot  │
  │     be changed once confirmed!      │
  │                                     │
  │  [Confirm Selection]                │
  └─────────────────────────────────────┘
    ↓
  User confirms forms
    ↓
PAYMENT GATEWAY (Razorpay/Stripe)
│
├── Order Summary:
│   ├── Subscription: Starter+ (Annual)
│   ├── Amount: ₹4,499
│   ├── GST (18%): ₹809.82
│   ├── Total: ₹5,308.82
│   └── Selected Forms: Term Insurance, Retirement Planning
│
├── Payment Methods:
│   ├── Credit/Debit Card
│   ├── UPI
│   ├── Net Banking
│   └── Wallets
│
└── [Pay Now]
    ↓
Payment successful
    ↓
System updates:
  - Account status: "active"
  - Subscription tier: "Starter+"
  - Report limit: 150 (annual)
  - Reports used: 0 (reset counter)
  - Start date: today
  - End date: today + 365 days
  - Selected forms: ["term_insurance", "retirement_planning"]
  - Forms locked: true
    ↓
IF from affiliate:
  - Create commission record
  - Notify affiliate
    ↓
Email sent to advisor:
  - Payment confirmation
  - Invoice (PDF)
  - Getting started guide for paid tier
    ↓
Dashboard access with full features
```

### **Post-Purchase: Advisor Usage**
```
ADVISOR DASHBOARD (Paid Account)
│
├── Header Section
│   ├── Subscription: Starter+ (Active)
│   ├── Reports: 145/150 remaining
│   ├── Expires: 320 days
│   └── [Upgrade Plan] [Renew Early]
│
├── Quick Actions
│   ├── Generate New Report
│   ├── View Report History (3 months)
│   └── Manage Profile
│
├── Report Forms Section
│   ├── Available Forms (unlocked based on tier):
│   │   ├── ✓ Term Insurance (enabled)
│   │   ├── ✓ Retirement Planning (enabled)
│   │   ├── ✓ Smart Tax Planning (bonus - unlimited)
│   │   ├── 🔒 Health Insurance (locked)
│   │   ├── 🔒 Child Education (locked)
│   │   ├── 🔒 Child Wedding (locked)
│   │   ├── 🔒 Home Purchase (locked)
│   │   └── 🔒 Vacation Planning (locked)
│   └── Upgrade to access more forms
│
├── Report Generation Workflow
│   ├── Select form (Term Insurance)
│   ├── Fill client details (multilingual form)
│   ├── Frontend collects data
│   ├── Backend calculates
│   ├── Modal shows summary:
│   │   ├── Existing coverage: ₹50 lakhs
│   │   ├── Recommended coverage: ₹2 crores
│   │   ├── Shortfall: ₹1.5 crores
│   │   └── Top 3 actions highlighted
│   ├── Advisor reviews
│   ├── Clicks "Generate PDF Report"
│   ├── Report generated with branding:
│   │   └── Name, Role, Contact (no photo/logo for non-Pro)
│   ├── Report counter: 144/150 remaining
│   └── PDF stored for 3 months
│
├── Profile Management
│   ├── Editable (always):
│   │   ├── Mobile number
│   │   └── Email
│   ├── Grace period (72 hours only):
│   │   ├── Full name
│   │   ├── Organization
│   │   └── Role
│   ├── Locked after 72 hours:
│   │   └── Requires email to support@salahkaarpro.com
│   └── Upload anytime:
│       ├── Photo (stored but only visible on Pro reports)
│       └── Logo (stored but only visible on Pro reports)
│
├── Subscription Management
│   ├── Current Plan Details
│   ├── Usage Statistics
│   ├── Renewal Options:
│   │   ├── Auto-renew (enable/disable)
│   │   └── Renew early (discounts available)
│   └── Upgrade Options:
│       ├── Compare tiers
│       ├── Pro-rated upgrade pricing
│       └── Instant upgrade (additional reports added)
│
└── Notifications
    ├── Report limit warnings:
    │   ├── At 90% (135/150): "10 reports remaining"
    │   └── At 100% (150/150): "Upgrade or renew to continue"
    ├── Expiry warnings:
    │   ├── 30 days before: "Subscription expiring soon"
    │   ├── 7 days before: "Renew now to avoid disruption"
    │   └── Expired: All features locked, upgrade prompt
    └── Feature updates and announcements
```

### **Whichever Comes First: Report Limit or Expiry**
```
Scenario A: Reports Exhausted Before Year
─────────────────────────────────────────
Advisor uses 150 reports in 6 months
    ↓
System detects: reports_used = report_limit
    ↓
Account status: "active_no_reports"
    ↓
Dashboard shows:
  "You've used all 150 reports. Your subscription is valid
   for 6 more months, but report generation is locked."
    ↓
Options presented:
  ├── Upgrade to higher tier (immediate reports added)
  │   Example: Upgrade to Specialist (200 reports)
  │   Cost: Pro-rated difference
  │
  └── Purchase additional report pack (future feature)
      Example: Buy 50 more reports for ₹999
    ↓
User remains in "active_no_reports" status until:
  - They upgrade/purchase more reports, OR
  - Subscription expires (then full renewal needed)


Scenario B: Subscription Expires Before Reports Used
─────────────────────────────────────────────────────
Advisor uses only 80/150 reports in 12 months
    ↓
System detects: current_date > end_date
    ↓
Account status: "expired"
    ↓
All features locked (unused reports forfeit)
    ↓
Dashboard shows:
  "Your subscription has expired. Renew to continue."
    ↓
Options presented:
  ├── Renew same tier (₹4,499 for Starter+)
  │   New 150 reports + 365 days
  │
  └── Upgrade to different tier
      Compare plans and select
    ↓
After renewal:
  - Status: "active"
  - Reports reset to new limit
  - New 365-day period starts
```

---

## **5. MASTER ADMIN COMPLETE WORKFLOW**

### **Admin Panel Access & Security**
```
ADMIN LOGIN
    ↓
Email + Password
    ↓
MFA Required (Google Authenticator/SMS)
    ↓
Access Granted
    ↓
MASTER ADMIN DASHBOARD
│
├── Overview Metrics (Real-time)
│   ├── Total Advisors: 1,247
│   ├── Active Subscriptions: 1,089
│   ├── Trial Users: 158
│   ├── Total Affiliates: 45 (32 active)
│   ├── Reports Generated (Today): 342
│   ├── Revenue (This Month): ₹18,45,600
│   └── Pending Actions:
│       ├── Affiliate Approvals: 3
│       ├── Commission Approvals: 27
│       ├── Profile Update Requests: 5
│       └── Refund Requests: 2
│
├── User Management Section
│   │
│   ├── Advisors Tab
│   │   ├── Search & Filters:
│   │   │   ├── By name/email/mobile
│   │   │   ├── By tier
│   │   │   ├── By status (active/trial/expired)
│   │   │   └── By signup source (organic/affiliate)
│   │   │
│   │   ├── Advisor List Table:
│   │   │   ├── Name, Email, Mobile
│   │   │   ├── Subscription Tier
│   │   │   ├── Reports Used/Limit
│   │   │   ├── Expiry Date
│   │   │   ├── Status
│   │   │   └── Actions:
│   │   │       ├── View Details
│   │   │       ├── Edit Subscription
│   │   │       ├── Extend Subscription
│   │   │       ├── Add Reports
│   │   │       ├── Cancel Subscription
│   │   │       └── View Audit Log
│   │   │
│   │   └── Individual Advisor Detail View:
│   │       ├── Personal Info
│   │       ├── Subscription History
│   │       ├── Payment History
│   │       ├── Report Generation History
│   │       ├── Activity Timeline
│   │       └── Manual Actions:
│   │           ├── Change Tier (with reason)
│   │           ├── Extend Validity (free extension)
│   │           ├── Add Bonus Reports
│   │           ├── Approve Profile Changes
│   │           └── Send Notification
│   │
│   └── Profile Update Requests Tab
│       ├── Pending requests for critical fields
│       ├── Request details:
│       │   ├── Advisor name
│       │   ├── Field to update
│       │   ├── Old value
│       │   ├── New value
│       │   ├── Reason provided
│       │   └── Requested date
│       └── Actions:
│           ├── Approve (update immediately)
│           └── Reject (with reason)
│
├── Affiliate Management Section
│   │
│   ├── Active Affiliates Tab
│   │   ├── List with stats:
│   │   │   ├── Name, Email
│   │   │   ├── Total Referrals
│   │   │   ├── Active Advisors (from refs)
│   │   │   ├── Total Commission Earned
│   │   │   ├── Commission Plan
│   │   │   └── Status
│   │   └── Actions per affiliate:
│   │       ├── View Dashboard (admin view)
│   │       ├── View Landing Page
│   │       ├── Edit Commission Plan
│   │       ├── View Referral Details
│   │       ├── Suspend/Deactivate
│   │       └── Send Message
│   │
│   ├── Pending Approvals Tab
│   │   ├── New affiliate applications
│   │   ├── Application details:
│   │   │   ├── Name, Email, Mobile
│   │   │   ├── Company/Organization
│   │   │   ├── Why joining (text)
│   │   │   ├── Applied date
│   │   │   └── Attached documents (if any)
│   │   └── Actions:
│   │       ├── Approve:
│   │       │   ├── Assign commission plan
│   │       │   ├── Generate unique ID
│   │       │   ├── Send welcome email
│   │       │   └── Grant dashboard access
│   │       └── Reject:
│   │           ├── Provide reason
│   │           └── Send rejection email
│   │
│   ├── Add New Affiliate (Manual)
│   │   ├── Form fields:
│   │   │   ├── Name*
│   │   │   ├── Email*
│   │   │   ├── Mobile*
│   │   │   ├── Photo/Logo upload
│   │   │   ├── Bio
│   │   │   └── Commission plan assignment
│   │   ├── Auto-generates:
│   │   │   ├── Unique ID
│   │   │   ├── Referral link
│   │   │   └── Landing page URL
│   │   └── Sends welcome email with credentials
│   │
│   └── Landing Page Management
│       ├── Preview all affiliate pages
│       ├── Edit custom content (if needed)
│       └── Monitor page performance
│
├── Commission Management Section
│   │
│   ├── Pending Approvals Tab
│   │   ├── Commission records awaiting approval:
│   │   │   ├── Affiliate Name
│   │   │   ├── Advisor Name
│   │   │   ├── Transaction Type (New/Renewal)
│   │   │   ├── Subscription Tier
│   │   │   ├── Gross Amount
│   │   │   ├── Net Amount
│   │   │   ├── Commission Rate
│   │   │   ├── Commission Amount
│   │   │   ├── Created Date
│   │   │   └── Actions:
│   │   │       ├── Approve (bulk or individual)
│   │   │       ├── Reject (with reason)
│   │   │       └── Modify Amount:
│   │   │           ├── Enter new amount
│   │   │           ├── Provide reason
│   │   │           └── Save
│   │   │
│   │   └── Bulk Actions:
│   │       ├── Select multiple commissions
│   │       ├── Approve all selected
│   │       └── Export to CSV
│   │
│   ├── Approved Commissions Tab
│   │   ├── All approved, awaiting payout
│   │   ├── Filtered by:
│   │   │   ├── Affiliate
│   │   │   ├── Date range
│   │   │   └── Payout status
│   │   └── Ready for payout processing
│   │
│   ├── Payout Processing Tab
│   │   ├── Monthly payout queue
│   │   ├── Grouped by affiliate:
│   │   │   ├── Affiliate Name
│   │   │   ├── Bank Details
│   │   │   ├── Total Amount
│   │   │   ├── Number of Commissions
│   │   │   └── Tax Deduction (TDS if applicable)
│   │   │
│   │   ├── Manual Processing:
│   │   │   ├── Select affiliate
│   │   │   ├── Verify bank details
│   │   │   ├── Choose payment method (NEFT/RTGS/UPI)
│   │   │   ├── Enter transaction ID
│   │   │   ├── Mark as paid
│   │   │   └── System sends confirmation
│   │   │
│   │   └── Future: Auto-Payout Setup
│   │       ├── Integrate Razorpay Payouts
│   │       ├── Enable auto-processing
│   │       ├── Set payout schedule (monthly/bi-weekly)
│   │       └── Admin reviews only exceptions
│   │
│   ├── Rejected Commissions Tab
│   │   ├── Historical rejections
│   │   ├── Rejection reasons
│   │   └── Dispute resolution (if any)
│   │
│   └── Commission Plan Management
│       ├── View all commission structures
│       ├── Default tiered structure:
│       │   ├── Edit tier thresholds
│       │   ├── Edit commission percentages
│       │   └── Set renewal commission rate
│       └── Custom affiliate plans:
│           ├── Override default for specific affiliate
│           ├── Set flat rate or custom tiers
│           ├── Effective date range
│           └── Reason for custom plan
│
├── Subscription & Pricing Management
│   │
│   ├── Tier Configuration
│   │   ├── For each tier (Basic to Enterprise):
│   │   │   ├── Original Price (₹)
│   │   │   ├── Launch Offer Price (₹)
│   │   │   ├── Report Limit
│   │   │   ├── Features JSON:
│   │   │       ├── Forms included
│   │   │       ├── Branding options
│   │   │       ├── Special features
│   │   │       └── Support level
│   │   │   └── Is Active (toggle)
│   │   │
│   │   └── Apply changes:
│   │       ├── Immediate effect for new signups
│   │       ├── Existing subscriptions unaffected
│   │       └── Announcement email option
│   │
│   ├── Form Selection Rules
│   │   ├── Starter+: 2 forms
│   │   ├── Specialist+: 3 forms
│   │   └── Lock/unlock forms per tier
│   │
│   └── Special Promotions
│       ├── Create promo codes
│       ├── Set discount percentage
│       ├── Set validity period
│       └── Usage limit per code
│
├── Payment & Refund Management
│   │
│   ├── Payment Transactions
│   │   ├── All payment records
│   │   ├── Filter by status/date/amount
│   │   ├── View payment details:
│   │   │   ├── Advisor details
│   │   │   ├── Amount breakdown
│   │   │   ├── Gateway fees
│   │   │   ├── GST
│   │   │   ├── Transaction ID
│   │   │   └── Invoice link
│   │   └── Actions:
│   │       ├── Download invoice
│   │       ├── Resend invoice
│   │       └── Initiate refund
│   │
│   ├── Refund Requests
│   │   ├── Pending refunds (within 72-hour MBG)
│   │   ├── Request details:
│   │   │   ├── Advisor info
│   │   │   ├── Purchase date
│   │   │   ├── Amount
│   │   │   ├── Eligibility status:
│   │   │       ├── Organic user (no trial): Eligible
│   │   │       ├── Affiliate user: Eligible
│   │   │       ├── Trial conversion: Not eligible
│   │   │   ├── Time remaining (72-hour window)
│   │   │   └── Reason provided
│   │   │
│   │   └── Actions:
│   │       ├── Approve Refund:
│   │       │   ├── Full refund to payment method
│   │       │   ├── Update subscription status
│   │       │   ├── If affiliate referral: reverse commission
│   │       │   └── Send confirmation
│   │       └── Reject Refund:
│   │           ├── Provide reason
│   │           └── Send email
│   │
│   └── Failed Payments (Dunning)
│       ├── Auto-retry schedule
│       ├── Email notification logs
│       └── Manual retry option
│
├── Report & Analytics Dashboard
│   │
│   ├── Real-Time Metrics
│   │   ├── Reports generated today/week/month
│   │   ├── By form type (bar chart)
│   │   ├── By subscription tier (pie chart)
│   │   └── Peak usage times (line graph)
│   │
│   ├── Revenue Analytics
│   │   ├── Revenue by tier (monthly trend)
│   │   ├── MRR (Monthly Recurring Revenue)
│   │   ├── ARR (Annual Recurring Revenue)
│   │   ├── Revenue by source:
│   │   │   ├── Organic
│   │   │   └── Affiliate
│   │   └── Affiliate commission payout vs revenue ratio
│   │
│   ├── User Analytics
│   │   ├── Total users by status
│   │   ├── Trial to paid conversion rate
│   │   ├── Churn rate by tier
│   │   ├── Average reports per user
│   │   └── User geographic distribution
│   │
│   ├── Affiliate Analytics
│   │   ├── Top performing affiliates
│   │   ├── Referral conversion rate
│   │   ├── Average commission per referral
│   │   └── Affiliate vs organic comparison
│   │
│   └── Export Options
│       ├── CSV/Excel export
│       ├── Custom date range
│       └── Scheduled reports (email)
│
├── System Configuration
│   │
│   ├── Email Templates
│   │   ├── All notification types
│   │   ├── Multilingual versions
│   │   ├── Edit subject/body
│   │   ├── Preview before saving
│   │   └── Test send
│   │
│   ├── Policy Documents
│   │   ├── Terms & Conditions
│   │   ├── Privacy Policy
│   │   ├── Refund Policy
│   │   ├── Version control
│   │   └── Publish updates
│   │
│   ├── Feature Flags
│   │   ├── Enable/disable features globally
│   │   ├── A/B testing toggles
│   │   └── Rollout controls
│   │
│   └── API & Integration Settings
│       ├── Payment gateway credentials
│       ├── SMS provider settings
│       ├── Email service config
│       ├── Storage service config
│       └── Third-party API keys
│
└── Audit Logs
    ├── All admin actions logged
    ├── Filter by:
    │   ├── Admin user
    │   ├── Action type
    │   ├── Date range
    │   └── Entity type
    ├── View details:
    │   ├── Who performed action
    │   ├── What was changed
    │   ├── Old vs new values
    │   └── Timestamp
    └── Export for compliance