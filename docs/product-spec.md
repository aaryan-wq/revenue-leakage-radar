
# Revenue Leakage Radar MVP, Product Specification v1.0

> **Product Statement:** Revenue Leakage Radar enables finance teams to upload billing (required) and CRM (recommended) CSV exports, receive a free Revenue Verification Summary in minutes, and purchase a detailed Revenue Verification Report containing evidence, customer-level findings, and remediation guidance.

----------

# 1. Product Principles

Principle

Decision

Core Value

Find recoverable recurring revenue from existing customers.

Primary User

CFO, VP Finance, Finance Manager, RevOps

Secondary User

CEO, Founder

Time to Value

<15 minutes from landing page to free summary

Signup

Not required until purchasing report

Data Source

CSV uploads only (API integrations later)

AI Usage

CSV mapping, validation, summaries, recommendations, not primary financial decisions

Detection

Deterministic verification engine

----------

# 2. Navigation Structure

## Public

-   Landing
    
-   Pricing
    
-   Security
    
-   FAQ
    
-   Contact
    

----------

## Anonymous Audit

-   Upload
    
-   Validation
    
-   Analysis
    
-   Free Summary
    
-   Checkout
    

----------

## Authenticated

-   Dashboard
    
-   Report
    
-   Findings
    
-   Account
    
-   Billing
    

----------

# 3. User Flow

```text
Landing
↓
Run Free Revenue Scan
↓
Upload CSVs
↓
Validation
↓
Verification Engine
↓
Free Revenue Summary
↓
Unlock Report
↓
Create Account
↓
Stripe Checkout
↓
Detailed Report
↓
Dashboard

```

----------

# 4. Landing Page

## Goal

Get upload started immediately.

----------

## Sections

### Hero

Headline

Subheadline

Primary CTA

Secondary CTA

Supported Platforms

----------

### How It Works

1 Upload CSV

2 Revenue Verification

3 Recover Revenue

----------

### Example Report

Static preview

Blurred customer names

Visible ARR numbers

----------

### Verification Checks

Grid

Each card

-   icon
    
-   title
    
-   description
    

----------

### Pricing

Free

Detailed Report

Annual Membership

----------

### Security

Encryption

CSV deletion

Privacy

----------

### FAQ

10–15 questions

----------

### Footer

Legal

Privacy

Terms

Contact

----------

# 5. Upload Flow

## Objective

Collect billing data with progressive coverage tiers, start with the minimum viable dataset and enrich as files become available.

----------

## Tier 0, Required (Minimum Viable Data)

Core pricing drift detection runs on exactly two files:

-   invoice_line_items.csv
    
-   prices.csv (alias: price_catalog.csv)
    

----------

## Tier 1, Strongly Recommended

Improves confidence and unlocks subscription, invoice, and customer-level rules:

-   subscriptions.csv
    
-   invoices.csv
    
-   customers.csv
    

----------

## Tier 2 & 3, Optional Power-Ups

-   coupons.csv, discount and coupon rules
    
-   CRM exports (accounts, contracts, opportunities), contract and seat-count validation
    

Supported CRM platforms:

HubSpot

Salesforce

Pipedrive

Zoho

----------

## Upload UX

Drag & Drop

Browse

Auto filename detection

Progress bars

Delete file

Replace file

----------

Validation immediately begins.

----------

# 6. Validation Screen

## AI Mapping

Automatically detect

Stripe

Chargebee

Maxio

Zuora

Generic

----------

Map

Customer ID

Subscription

Invoice

Coupon

Price

Dates

Currency

----------

## Validation

Required columns

Missing values

Duplicate IDs

Broken dates

Currency mismatch

Relationship integrity

----------

## Validation Result

Green

Ready

Yellow

Warnings

Red

Blocking errors

----------

Blocking errors prevent scan.

Warnings allow continuation.

----------

# 7. Analysis Screen

Full screen.

Progress animation.

----------

Pipeline

✓ Upload

✓ Parse

✓ Normalize

✓ Validation

✓ Verification Checks

✓ Revenue Estimation

✓ Report Generation

----------

Estimated remaining time.

Cancel scan.

----------

# 8. Free Revenue Verification Summary

## Purpose

Sell detailed report.

----------

### Hero

Estimated Recoverable ARR

Confidence

Verification Checks Run

Potential Findings

Accounts Reviewed

Invoices Reviewed

----------

### Opportunity Breakdown

Expired Discounts

Legacy Pricing

Renewal Pricing

Duplicate Discounts

Invoice Errors

etc.

Each shows

Estimated ARR

Confidence

Issue count

----------

### Verification Checklist

Pass

Warning

Issue Found

----------

### Coverage

Billing Coverage

CRM Coverage

Confidence Impact

----------

### Locked Cards

Blurred

Customer list

Evidence

Recommendations

Invoices

Remediation

----------

CTA

Unlock Full Report

----------

# 9. Checkout

Anonymous user.

----------

Click

Unlock Report

↓

Modal

Create Account

↓

Stripe Checkout

↓

Success

↓

Dashboard

↓

Report

----------

Plans

Detailed Report

Annual Membership

----------

# 10. Dashboard

Purpose

Audit history.

----------

Header

Company

Reports Remaining

New Audit

----------

Table

Audit

Date

ARR Found

Status

Findings

Actions

----------

Actions

Open

Download

Delete

----------

Empty State

Run first audit.

----------

# 11. Detailed Report

Sections

Executive Summary

Opportunity Breakdown

Verification Checks

Findings

Recommendations

Exports

----------

# 12. Executive Summary

Report ID

Date

Company

Generated By

----------

Metrics

Recoverable ARR

High Confidence ARR

Medium Confidence ARR

Accounts

Invoices

Checks

Confidence

----------

Executive Narrative

Generated by AI.

----------

# 13. Opportunity Breakdown

Cards

Category

ARR

Confidence

Accounts

Priority

----------

Categories

Expired Discounts

Legacy Pricing

Underpriced Renewals

Invoice Errors

Duplicate Discounts

Manual Overrides

Custom Pricing

Future checks

----------

# 14. Verification Checks

Table

Check

Status

Affected Accounts

Estimated ARR

Confidence

----------

Statuses

Passed

Issues Found

Needs CRM

Not Run

----------

# 15. Findings

Each Finding Card

Title

Priority

Estimated ARR

Confidence

Affected Accounts

Expand

----------

Sorting

Highest ARR

Highest Confidence

Newest

Category

----------

Filtering

Confidence

ARR

Category

Status

----------

# 16. Finding Detail

Header

Finding ID

Category

Rule Triggered

Priority

----------

Summary

Explanation

Financial Impact

Recommendation

----------

Evidence Table

Customer

Subscription

Invoice

Product

Expected Price

Actual Price

Difference

Monthly Impact

Annual Impact

Confidence

----------

Recommendation

Example

Increase renewal price.

Remove expired discount.

Update billing catalog.

Review contract.

----------

Actions

Export CSV

Download PDF

Copy Link

----------

# 17. Exports

PDF

CSV

Executive Summary

Findings CSV

Evidence CSV

----------

# 18. Account

Company

Billing

Reports

Password

Delete Account

----------

# 19. Billing

Plan

Reports Remaining

Invoices

Upgrade

Cancel

----------

# 20. Security Page

Encryption

Retention Policy

CSV Deletion

Infrastructure

Contact

FAQ

----------

# 21. Admin (Internal)

Search Companies

Search Reports

View Logs

Delete Reports

Delete Uploads

Refund Payment

Support Notes

----------

# Core Verification Checks (MVP)

Check

Billing

CRM

MVP

Expired Discounts

✓

✓

Legacy Pricing

✓

✓

Renewal Pricing Drift

✓

✓

✓

Duplicate Discounts

✓

✓

Price Catalog Mismatch

✓

✓

Missing Scheduled Increase

✓

✓

✓

Contract vs Billing Price

✓

Later

Seat Count Variance

✓

Later

Manual Billing Overrides

✓

Later

Duplicate Active Subscriptions

✓

Later

Currency Errors

✓

Later

Credit Leakage

✓

Later

Incorrect Billing Frequency

✓

Later

Free Plans Never Converted

✓

✓

Later

Grandfathered Pricing

✓

✓

----------

# AI Responsibilities

## CSV Mapping

Identify platform.

Map columns.

Detect synonyms.

----------

## Validation

Suggest corrections.

Repair headers.

Normalize dates.

Normalize currencies.

----------

## Narrative

Executive summary.

Category summaries.

Recommendations.

----------

## NOT AI

Financial calculations.

Leakage detection.

Evidence generation.

Pricing comparisons.

These remain deterministic.

----------

# Error States

## Missing File

Explain.

Show sample.

Retry.

----------

## Invalid CSV

Highlight problem.

Suggest correction.

----------

## AI Failure

Retry.

Fallback.

Continue if deterministic path available.

----------

## Payment Failure

Retry.

Change method.

Contact support.

----------

## Timeout

Resume processing.

Notify user.

----------

# Empty States

Dashboard

No audits.

↓

Run first scan.

----------

Report

No findings.

↓

Congratulations.

Show passed checks.

----------

Validation

No files.

↓

Upload.

----------

# Notifications

Upload Complete

Validation Passed

Analysis Started

Analysis Complete

Payment Success

Report Ready

Download Complete

----------

# Permissions

Anonymous

Upload

Summary

Checkout

----------

Authenticated

Dashboard

Reports

Downloads

Billing

----------

Admin

Everything

----------

# MVP Success Criteria

-   User reaches free summary in <15 minutes.
    
-   Free summary clearly quantifies potential revenue opportunity.
    
-   Detailed report provides invoice-level evidence and remediation guidance.
    
-   Payment unlocks immediate access to the full report.
    
-   Reports can be exported as PDF and CSV.
    
-   Raw uploaded CSVs are automatically deleted after processing according to the retention policy.
    
-   Every financial finding is backed by deterministic evidence, with AI limited to data normalization, summarization, and recommendations.
    

This specification defines the complete functional scope of the CSV-first MVP. Future iterations (API integrations, scheduled scans, collaboration, and continuous monitoring) extend this foundation without changing the core user experience.
