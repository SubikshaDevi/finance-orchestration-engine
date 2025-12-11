#Automated Financial Orchestration Engine

Status: Production (Deployed at 5C Network) Role: Data Scientist : Python, Prefect, FastAPI, PostgreSQL, Docker

1. Overview
A dual-sided marketplace billing engine designed to reconcile payments between Healthcare Providers (Radiologists) and Clients (Hospitals). The system handles complex, variable-rate pricing logic, multi-currency support, and immutable financial reporting.

Business Impact:

Scale: Automates billing for 800+ invoices/month across two distinct user bases.

Efficiency: Reduced manual finance operations by 90% (from 5 days/month to minutes).

Accuracy: Eliminated manual Excel errors by enforcing strict schema validation and automated unit testing.

2. System Architecture
The "Mediator" Pattern
Unlike standard SaaS billing (subscription-based), this system operates as a mediator. Every transaction (Medical Report) has two distinct financial events:

Cost of Goods Sold (COGS): The fee paid to the Radiologist (based on Grade, Seniority, Modality).

Revenue: The fee charged to the Hospital (based on Volume Tier, Contract Type, Foreign Exchange Rate).

Data Pipeline (The "Windowed Sync")
Orchestrator: Prefect (Python) triggers hourly sync jobs.

Strategy: implemented a "Rolling Window" ETL pattern.

The pipeline processes data from Day 1 to Current Timestamp for the active month.

Locking Mechanism: Once a month is "Closed" (invoices generated), the data is virtually locked to ensure historical consistency. Updates to closed months require a privileged "Rerun" action.

3. Key Engineering Decisions
A. Immutable Ledger for Credit Notes
Problem: Financial data must be auditable. Deleting an incorrect invoice is a violation of accounting principles.

Solution: Implemented an Append-Only Architecture.

If an invoice is incorrect, we generate a Credit Note (a new row in a separate table) rather than modifying the original record.

Final Statement Logic: Total Due = Sum(Invoices) - Sum(Credit Notes).

This ensures a complete audit trail for every cent adjusted.

B. Handling Dynamic Pricing & Reruns
Problem: Pricing agreements change retrospectively. A client might negotiate a new rate for January in February.

Solution: Built a "Cost Rerun" API.

This allows Finance Ops to target a specific historical window (e.g., "Jan 2023").

The engine pulls the current pricing configuration and re-calculates margins for that specific period without corrupting active data.

C. Multi-Currency Handling
Integration: Embedded an external API call within the Python processing layer to fetch real-time Foreign Exchange (Forex) rates for international clients.

Logic: Normalized all margins to the base currency (INR) for accurate C-Suite reporting in the Margin_Summary materialized views.

4. Database Schema (Simplified)
finance_invoices: The immutable record of generated bills.

finance_credit_notes: Adjustments and refunds.

provider_pricing_rules: JSON-based rules for Radiologist payouts (based on Seniority/Modality).

client_pricing_rules: Tiered pricing logic for Hospitals.

margin_summary: Pre-aggregated table updating hourly for instant C-Level dashboard visibility.
