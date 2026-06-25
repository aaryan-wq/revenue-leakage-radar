
# Revenue Leakage Radar — Technical Specification v1.0 (High-Level Architecture)

----------

# 1. System Topology

```text
                 Frontend (Next.js)

                      │
                      ▼

             FastAPI Application Layer

 ┌──────────────────────────────────────────────────────┐
 │ Authentication                                        │
 │ Audit Management                                      │
 │ Upload Service                                        │
 │ Report Service                                        │
 │ Payment Service                                       │
 └──────────────────────────────────────────────────────┘

                      │

      ┌───────────────┼────────────────┐
      ▼               ▼                ▼

 CSV Import      AI Processing     Verification Engine

      │               │                │

      └───────────────▼────────────────┘

          Canonical Revenue Data Model

                      │

                 PostgreSQL

                      │

             Findings + Reports

                      │

             PDF / Dashboard / CSV

```

----------

# 2. Backend Stack

Layer

Technology

Frontend

Next.js 15 + React + TypeScript

API

FastAPI

Validation

Pydantic

Database

PostgreSQL

ORM

SQLAlchemy

Background Jobs

Celery + Redis

File Storage (Temporary)

Local → S3 later

Payments

Stripe Checkout

Authentication

Clerk

AI

OpenAI API

PDF

WeasyPrint

CSV

Pandas + Polars

----------

# 3. Core Services

Service

Responsibility

Upload Service

Receive & stage CSVs

Mapping Service

Detect platform & map columns

Validation Service

Validate schemas & relationships

Canonical Transformer

Normalize data model

Verification Engine

Execute deterministic leakage rules

AI Service

Mapping, cleaning, summaries, recommendations

Report Service

Build summary, report, PDF

Payment Service

Stripe checkout & entitlements

Audit Service

Track scans & lifecycle

----------

# 4. FastAPI Routes

## Public

Method

Endpoint

Function

POST

/audit

Create anonymous audit session

POST

/upload

Upload CSV files

POST

/validate

Validate uploaded files

POST

/scan

Start verification job

GET

/summary/{audit_id}

Free summary

POST

/checkout

Create Stripe checkout

----------

## Authenticated

Method

Endpoint

Function

GET

/reports

List reports

GET

/reports/{id}

Detailed report

GET

/findings/{id}

Finding detail

GET

/exports/pdf/{id}

PDF export

GET

/exports/csv/{id}

CSV export

GET

/dashboard

Audit history

GET

/billing

Subscription status

----------

## Internal

Method

Endpoint

Function

GET

/health

Health check

GET

/admin/audits

Admin audit list

DELETE

/admin/uploads

Delete raw uploads

POST

/admin/reprocess

Re-run audit

----------

# 5. Canonical Entity Model

```text
Company
    │
    ├──────── Customers
    │              │
    │              ├──── Subscriptions
    │              │           │
    │              │           ├──── Invoice Line Items
    │              │           │
    │              │           └──── Coupons
    │              │
    │              └──── Invoices
    │
    ├──────── Price Catalog
    │
    ├──────── Findings
    │
    └──────── Reports

```

----------

# 6. Core Tables

## Company

Field

id

name

created_at

----------

## Customer

Field

id

external_customer_id

company_id

crm_id

name

----------

## Subscription

Field

id

customer_id

external_subscription_id

product_id

plan

quantity

billing_interval

price

currency

start_date

renewal_date

status

coupon_id

----------

## Invoice

Field

id

subscription_id

invoice_number

invoice_date

period_start

period_end

subtotal

discount

total

currency

----------

## Invoice Line Item

Field

id

invoice_id

product_id

sku

quantity

unit_price

extended_price

----------

## Coupon

Field

id

code

discount_type

discount_value

expires_at

active

----------

## Price Catalog

Field

id

product_id

sku

version

effective_date

list_price

currency

----------

## Finding

Field

id

audit_id

rule_id

severity

confidence

customer_id

invoice_id

subscription_id

estimated_monthly_loss

estimated_arr_loss

recommendation

----------

## Report

Field

id

audit_id

recoverable_arr

finding_count

confidence

purchased

generated_at

----------

# 7. CSV Requirements

## Billing (Required)

File

Primary Key

subscriptions.csv

subscription_id

invoices.csv

invoice_id

invoice_line_items.csv

line_item_id

coupons.csv

coupon_id

price_catalog.csv

product_id + effective_date

----------

## CRM (Recommended)

File

Purpose

accounts.csv

Customer mapping

opportunities.csv

Renewal pricing

contracts.csv

Contract validation

----------

## CSV Constraints

-   UTF-8
    
-   Header row required
    
-   RFC4180 compliant
    
-   ISO-8601 dates
    
-   Decimal prices
    
-   Unique primary keys
    
-   Stable foreign-key references
    
-   ≤250 MB per file (MVP)
    

----------

# 8. Data Pipeline

```text
Upload

↓

Platform Detection (AI)

↓

Column Mapping (AI)

↓

Schema Validation

↓

Relationship Validation

↓

Canonical Transformation

↓

Deterministic Verification Engine

↓

Finding Generation

↓

AI Executive Summary

↓

Free Summary

↓

Paid Report

↓

PDF / Dashboard

```

----------

# 9. Verification Engine Pipeline

## Phase 1

Integrity

-   Missing IDs
    
-   Broken references
    
-   Duplicate keys
    

----------

## Phase 2

Normalization

-   Currency
    
-   Dates
    
-   Product IDs
    
-   Customer names
    

----------

## Phase 3

Deterministic Rules

-   Expired discounts
    
-   Legacy pricing
    
-   Renewal drift
    
-   Duplicate discounts
    
-   Price catalog mismatch
    
-   Grandfathered pricing
    
-   Missing scheduled increases
    
-   Invoice pricing mismatch
    
-   Duplicate subscriptions
    
-   Billing frequency mismatch
    
-   Credit leakage
    
-   Currency mismatch
    
-   Manual overrides
    
-   Discount stacking
    
-   Future extensible rules
    

----------

## Phase 4

Finding Generation

Each rule produces:

-   Evidence
    
-   ARR estimate
    
-   Confidence
    
-   Recommendation
    

----------

## Phase 5

Aggregation

Group findings by:

-   Customer
    
-   Category
    
-   Product
    
-   Revenue impact
    

----------

# 10. AI Pipeline

## AI Performs

-   Platform recognition
    
-   Column mapping
    
-   Header correction
    
-   Data normalization
    
-   Customer/entity matching
    
-   Narrative generation
    
-   Executive summary
    
-   Prioritization
    
-   Remediation recommendations
    

----------

## AI Never Performs

-   Financial calculations
    
-   Leakage detection
    
-   Price comparisons
    
-   ARR calculations
    
-   Confidence scoring
    
-   Rule execution
    

These remain deterministic.

----------

# 11. Verification Engine Inputs

Canonical Objects

-   Companies
    
-   Customers
    
-   Products
    
-   Price Catalog
    
-   Subscriptions
    
-   Coupons
    
-   Invoices
    
-   Invoice Line Items
    
-   CRM Contracts (optional)
    

----------

# 12. Verification Engine Outputs

Each rule emits:

Field

Finding ID

Rule ID

Severity

Confidence

Customer

Subscription

Invoice

Expected Value

Actual Value

Difference

Monthly Leakage

Annual Leakage

Evidence

Recommendation

----------

# 13. Processing States

```text
Created

↓

Uploading

↓

Mapping

↓

Validating

↓

Normalizing

↓

Scanning

↓

Generating Report

↓

Completed

```

Failure states:

-   Upload Failed
    
-   Validation Failed
    
-   Processing Failed
    
-   AI Retry
    
-   Payment Pending
    

----------

# 14. Background Jobs

Job

Queue

CSV Import

upload

Validation

validation

Canonical Transformation

processing

Verification Engine

verification

AI Narrative

ai

PDF Generation

reporting

CSV Cleanup

maintenance

----------

# 15. Security & Data Lifecycle

-   Anonymous audit session created on upload.
    
-   Raw CSVs stored only for active processing.
    
-   Automatic deletion of uploaded CSVs after processing or expiry.
    
-   Canonical normalized records retained only as needed for purchased reports and audit metadata.
    
-   All processing over HTTPS.
    
-   PostgreSQL encryption at rest (provider-managed).
    
-   Structured audit logs for processing events.
    
-   Secrets stored in environment variables only.
    

----------

# 16. Future Adapter Layer (No Core Changes Required)

Source

Adapter

Stripe API

Import Adapter

Chargebee API

Import Adapter

Maxio API

Import Adapter

Zuora API

Import Adapter

HubSpot API

CRM Adapter

Salesforce API

CRM Adapter

**All adapters output the same canonical data model; the Verification Engine remains unchanged regardless of input source.**
