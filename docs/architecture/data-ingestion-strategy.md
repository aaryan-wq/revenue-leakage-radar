\# data-ingestion-strategy.md



\# Revenue Leakage Radar



\## Canonical Data Ingestion Strategy



\---



\# Philosophy



The Verification Engine never understands Stripe, Chargebee, Salesforce, HubSpot, or any vendor-specific schema.



It only understands the Canonical Entity Model (CEM).



Every billing platform is translated into the CEM through adapters.



```

Billing Export

&#x20;       │

&#x20;       ▼

&#x20;Platform Adapter

&#x20;       │

&#x20;       ▼

Canonical Entity Model

&#x20;       │

&#x20;       ▼

Verification Engine

&#x20;       │

&#x20;       ▼

Findings

```



\---



\# Supported Billing Platforms



| Platform   | CSVs                                                                                                             | Priority |

| ---------- | ---------------------------------------------------------------------------------------------------------------- | -------- |

| Stripe     | Customers, Subscriptions, Invoices, Invoice Line Items, Products, Prices, Coupons, Promotion Codes, Credit Notes | P1       |

| Chargebee  | Customers, Subscriptions, Invoices, Invoice Line Items, Item Prices, Coupons, Credit Notes                       | P1       |

| Maxio      | Customers, Subscriptions, Invoices, Invoice Items, Products                                                      | P2       |

| Zuora      | Accounts, Subscriptions, Invoice Items, Product Catalog, Amendments                                              | P2       |

| Paddle     | Transactions, Subscriptions, Products, Discounts                                                                 | P3       |

| Recurly    | Accounts, Subscriptions, Invoices, Coupons                                                                       | P3       |

| ChargeOver | Customers, Recurring Billing, Invoices                                                                           | P3       |



\---



\# Supported CRM Platforms



| Platform   | CSVs                                                 | Priority |

| ---------- | ---------------------------------------------------- | -------- |

| Salesforce | Accounts, Opportunities, Contracts, Products, Quotes | P1       |

| HubSpot    | Companies, Deals, Products                           | P1       |

| Pipedrive  | Organizations, Deals                                 | P2       |

| Attio      | Companies, Deals                                     | P2       |

| Close      | Leads, Opportunities                                 | P3       |



\---



\# Canonical Entities



```

Customer

Subscription

Invoice

InvoiceLineItem

Product

Price

Coupon

PromotionCode

CreditNote

Refund

Contract

Opportunity

Quote

```



No verification rule may reference vendor-specific fields.



\---



\# Upload Categories



\## Billing (Core)



Customer



Subscription



Invoice



Invoice Line Item



Price Catalog



Product Catalog



Coupon



Promotion Code



Credit Note



Refund



\---



\## CRM (Optional)



Account



Company



Opportunity



Deal



Contract



Quote



\---



\# MVP Upload Requirements



\## Hard Required



Invoice Line Items



\---



\## Strongly Recommended



Subscriptions



Invoices



Customers



Price Catalog



\---



\## Optional



Products



Coupons



Promotion Codes



Credit Notes



Refunds



\---



\## CRM Enhancement



Accounts / Companies



Contracts



Opportunities / Deals



Quotes



\---



\# Verification Rule Coverage



| Rule                       | Billing                       | CRM         |

| -------------------------- | ----------------------------- | ----------- |

| Expired Discount           | InvoiceLineItem,Coupon        | -           |

| Legacy Pricing             | InvoiceLineItem,Price         | Contract    |

| Renewal Drift              | Subscription                  | Opportunity |

| Duplicate Discount         | InvoiceLineItem,Coupon        | -           |

| Price Catalog Mismatch     | InvoiceLineItem,Price         | -           |

| Grandfathered Pricing      | Subscription,Price            | Contract    |

| Missing Scheduled Increase | Subscription                  | Contract    |

| Invoice Pricing Mismatch   | Invoice,InvoiceLineItem,Price | -           |

| Duplicate Subscription     | Subscription                  | Account     |

| Billing Frequency Mismatch | Subscription,Invoice          | Contract    |

| Credit Leakage             | CreditNote,Invoice            | -           |

| Currency Mismatch          | Customer,Invoice,Price        | Contract    |

| Manual Override            | InvoiceLineItem               | Opportunity |

| Discount Stacking          | Coupon,InvoiceLineItem        | -           |

| Custom Field Drift         | Subscription                  | CRM         |

| Cancelled Still Billing    | Subscription,Invoice          | CRM         |

| Active Not Billing         | Subscription,Invoice          | CRM         |

| Missing Invoice            | Subscription,Invoice          | CRM         |

| Orphan Subscription        | Customer,Subscription         | CRM         |

| Duplicate Customer         | Customer                      | Account     |



\---



\# Rule Availability



The engine must determine executable rules dynamically.



Pseudo:



```

available\_rules = \[]



for rule in registry:

&#x20;   if rule.required\_entities ⊆ uploaded\_entities:

&#x20;       available\_rules.append(rule)

```



Missing entities never fail the scan.



Unavailable rules are skipped.



\---



\# Adapter Contract



Every adapter outputs:



Customer\[]



Subscription\[]



Invoice\[]



InvoiceLineItem\[]



Product\[]



Price\[]



Coupon\[]



CreditNote\[]



Contract\[]



Opportunity\[]



Quote\[]



No downstream service may consume vendor-specific CSV schemas.



\---



\# Future API Strategy



CSV adapters and API adapters must emit identical Canonical Entities.



Verification Engine → unchanged.



Only ingestion changes.



Architecture:



Stripe CSV → Adapter → CEM



Stripe API → Adapter → CEM



Chargebee CSV → Adapter → CEM



Chargebee API → Adapter → CEM



Salesforce CSV → Adapter → CEM



Salesforce API → Adapter → CEM



