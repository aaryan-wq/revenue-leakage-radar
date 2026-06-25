
# Revenue Leakage Radar — Build Plan v1.0

----------

# 1. Sprint Roadmap

Sprint

Goal

Deliverables

Exit Criteria

**Sprint 1**

Foundation

Next.js, FastAPI, PostgreSQL, Clerk, Upload UI, DB schema

App runs locally, authentication works, CSV upload accepted

**Sprint 2**

Ingestion & Processing

CSV parser, AI mapping, validation, canonical transformer

Uploads validated and converted into canonical data model

**Sprint 3**

Verification Engine

Deterministic rules, findings generation, ARR calculations

Verification engine produces evidence-backed findings

**Sprint 4**

Reports

Free Summary, Paid Report, Dashboard, PDF export

Reports generated from findings, downloadable PDF

**Sprint 5**

Payments & Launch

Stripe Checkout, audit history, security page, landing page, QA

Complete anonymous-to-paid workflow functional

----------

# 2. Milestone Timeline

Milestone

Outcome

M1

User uploads billing CSVs

M2

Data validates automatically

M3

Verification engine completes scan

M4

Free Revenue Summary displayed

M5

User purchases report

M6

Full report available in dashboard

M7

Production deployment

----------

# 3. Repository Structure

```text
revenue-leakage-radar/
│
├── apps/
│   ├── web/                    # Next.js frontend
│   └── api/                    # FastAPI backend
│
├── packages/
│   ├── shared/                 # Shared TS types
│   ├── ui/                     # Shared UI components
│   └── config/                 # Shared configs
│
├── docs/
│   ├── product-spec.md
│   ├── design-system.md
│   ├── technical-spec.md
│   └── build-plan.md
│
├── infrastructure/
│   ├── docker/
│   ├── nginx/
│   └── scripts/
│
├── .github/
│
├── docker-compose.yml
├── README.md
└── .env.example

```

----------

# 4. Frontend Structure

```text
web/
│
├── app/
│   ├── (marketing)
│   ├── dashboard
│   ├── report
│   ├── upload
│   ├── checkout
│   └── account
│
├── components/
│   ├── layout
│   ├── upload
│   ├── report
│   ├── dashboard
│   ├── charts
│   ├── findings
│   ├── ui
│   └── common
│
├── hooks/
├── lib/
├── services/
├── styles/
├── types/
└── utils/

```

----------

# 5. Backend Structure

```text
api/
│
├── app/
│
├── audit/
│
├── upload/
│
├── validation/
│
├── canonical/
│
├── verification/
│
├── findings/
│
├── reports/
│
├── payments/
│
├── ai/
│
├── auth/
│
├── database/
│
├── models/
│
├── schemas/
│
├── workers/
│
├── middleware/
│
├── core/
│
└── main.py

```

----------

# 6. Verification Module

```text
verification/
│
├── engine.py
├── registry.py
│
├── rules/
│   ├── expired_discount.py
│   ├── legacy_pricing.py
│   ├── renewal_drift.py
│   ├── duplicate_discount.py
│   ├── price_catalog.py
│   ├── grandfathered.py
│   └── ...
│
└── outputs.py

```

----------

# 7. AI Module

```text
ai/
│
├── provider.py
├── mapping.py
├── normalization.py
├── summaries.py
├── recommendations.py
└── prompts/

```

----------

# 8. Report Module

```text
reports/
│
├── generator.py
├── pdf.py
├── summary.py
├── findings.py
└── exports.py

```

----------

# 9. Infrastructure

```text
Docker

↓

FastAPI

↓

Redis

↓

Celery Workers

↓

PostgreSQL

↓

Next.js

↓

Vercel / Railway

```

----------

# 10. Build Order

Order

Module

1

Database

2

Authentication

3

Upload

4

CSV Validation

5

Canonical Transformer

6

Verification Engine

7

Findings

8

Report Generator

9

Dashboard

10

Stripe Checkout

11

PDF Export

12

Polish & QA

----------

# 11. Epic: Upload → Free Summary

## Acceptance Criteria

### Upload

-   Anonymous audit session created.
    
-   Multiple CSV uploads supported.
    
-   Drag-and-drop and file picker supported.
    
-   Upload progress visible.
    

----------

### Validation

-   Platform detected automatically.
    
-   Required columns identified.
    
-   Missing columns reported.
    
-   AI maps equivalent headers.
    
-   Validation report displayed.
    

----------

### Canonical Transformation

-   All valid CSVs normalized into canonical schema.
    
-   Foreign-key relationships verified.
    
-   Duplicate records handled.
    
-   Invalid rows isolated without crashing the audit.
    

----------

### Verification Engine

-   All enabled deterministic rules executed.
    
-   Findings generated with evidence.
    
-   ARR calculations completed.
    
-   Confidence scores assigned.
    
-   Rule execution logged.
    

----------

### Free Summary

-   Total recoverable ARR displayed.
    
-   Opportunity breakdown shown.
    
-   Verification status displayed.
    
-   Locked detailed findings preview shown.
    
-   Upgrade CTA displayed.
    

----------

# 12. Acceptance Criteria (Reports)

-   Executive Summary generated.
    
-   Findings grouped by category.
    
-   Invoice-level evidence available.
    
-   PDF generated successfully.
    
-   CSV export available.
    
-   Dashboard stores completed audit.
    

----------

# 13. Acceptance Criteria (Payments)

-   Anonymous audit linked to account after signup.
    
-   Stripe Checkout completes successfully.
    
-   Purchased report unlocked instantly.
    
-   Audit history updated.
    
-   Receipt available.
    

----------

# 14. Definition of Done (Per Feature)

-   Functional implementation complete.
    
-   Unit tests pass.
    
-   No console errors.
    
-   Responsive (desktop + tablet).
    
-   Loading state implemented.
    
-   Error state implemented.
    
-   Empty state implemented.
    
-   Accessibility basics (keyboard + focus).
    
-   API documented.
    
-   Logging added.
    
-   Types fully defined.
    
-   No TODO/FIXME comments.
    
-   Reviewed by Cursor agent before merge.
    

----------

# 15. MVP Definition of Done

## Functional

-   Landing page complete.
    
-   Upload workflow complete.
    
-   CSV validation complete.
    
-   Canonical transformation complete.
    
-   Verification engine operational.
    
-   Minimum 15 deterministic verification rules.
    
-   Free Revenue Summary operational.
    
-   Stripe Checkout operational.
    
-   Paid report operational.
    
-   Dashboard operational.
    
-   PDF export operational.
    

----------

## Technical

-   Typed end-to-end.
    
-   No blocking bugs.
    
-   API documented.
    
-   Database migrations complete.
    
-   Environment variables documented.
    
-   Background jobs functioning.
    
-   Raw CSV cleanup automated.
    

----------

## UX

-   Consistent Design System.
    
-   Responsive layout.
    
-   Skeleton loading states.
    
-   Clear validation messages.
    
-   Smooth page transitions.
    
-   Premium visual polish.
    

----------

## Security

-   HTTPS enforced.
    
-   Authentication required for paid content.
    
-   Secrets stored in environment variables.
    
-   Uploaded CSVs automatically deleted after processing.
    
-   Audit logs enabled.
    

----------

## Performance Targets

Metric

Target

Landing → Upload

<30 sec

Upload Validation

<10 sec

Verification Scan

<5 min (target), <15 min (max)

Free Summary Render

<2 sec

Report Generation

<60 sec

PDF Export

<15 sec

Page Load

<2 sec

----------

# 16. Launch Checklist

-   Production database deployed.
    
-   Environment variables configured.
    
-   Stripe production keys enabled.
    
-   Authentication configured.
    
-   Email domain configured.
    
-   Error monitoring enabled.
    
-   Analytics enabled.
    
-   Security page published.
    
-   Pricing page published.
    
-   Sample report available.
    
-   Support email configured.
    
-   First customer audit successfully completed end-to-end.
    

</> **Build Complete** = A user can land on the website, upload billing CSVs without creating an account, receive a free Revenue Verification Summary, create an account only when purchasing, pay via Stripe, instantly unlock a detailed evidence-backed report, export PDF/CSV findings, and revisit purchased reports through their dashboard—all without manual intervention.
