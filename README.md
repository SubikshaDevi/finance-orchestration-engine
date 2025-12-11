# Automated Financial Orchestration Engine

![Status](https://img.shields.io/badge/Status-Production-success)
![Role](https://img.shields.io/badge/Role-Data_Scientist-blue)
![Stack](https://img.shields.io/badge/Tech-Python_|_Prefect_|_FastAPI_|_PostgreSQL-yellow)

**A dual-sided marketplace billing engine designed to reconcile payments between Healthcare Providers (Radiologists) and Clients (Hospitals).**

This system serves as the financial backbone for the company, handling complex variable-rate pricing logic, multi-currency support, and immutable financial reporting.

---

## 🚀 Business Impact
* **Scale:** Automates billing for **800+ invoices/month** across two distinct user bases.
* **Efficiency:** Reduced manual finance operations by **90%** (process time dropped from 5 days/month to minutes).
* **Accuracy:** Eliminated manual Excel errors by enforcing strict schema validation and automated unit testing.

---

## 🏗️ System Architecture

### The "Mediator" Pattern
Unlike standard SaaS billing (subscription-based), this system operates as a mediator. Every transaction (Medical Report) triggers two distinct financial events:
1.  **Cost of Goods Sold (COGS):** The fee paid to the Radiologist (based on Grade, Seniority, Modality).
2.  **Revenue:** The fee charged to the Hospital (based on Volume Tier, Contract Type, Foreign Exchange Rate).

### Data Pipeline (The "Windowed Sync")
* **Orchestrator:** Prefect (Python) triggers hourly sync jobs.
* **Strategy:** Implemented a **"Rolling Window" ETL pattern**.
    * The pipeline processes data from `Day 1` to `Current Timestamp` for the active month.
    * **Locking Mechanism:** Once a month is "Closed" (invoices generated), the data is virtually locked to ensure historical consistency. Updates to closed months require a privileged "Rerun" action.

---

## 🛠️ Key Engineering Decisions

### 1. Immutable Ledger for Credit Notes
* **Problem:** Financial data must be auditable. Deleting an incorrect invoice violates accounting principles.
* **Solution:** Implemented an **Append-Only Architecture**.
    * If an invoice is incorrect, we generate a `Credit Note` (a new row in a separate table) rather than modifying the original record.
    * **Final Statement Logic:** `Total Due = Sum(Invoices) - Sum(Credit Notes)`.
    * This ensures a complete audit trail for every cent adjusted.

### 2. Handling Dynamic Pricing & Historical Reruns
* **Problem:** Pricing agreements change retrospectively. A client might negotiate a new rate for January in February.
* **Solution:** Built a **"Cost Rerun" API**.
    * Allows Finance Ops to target a specific historical window (e.g., "Jan 2023").
    * The engine pulls the *current* pricing configuration and re-calculates margins for that specific period without corrupting active data.

### 3. Multi-Currency Handling
* **Integration:** Embedded an external API call within the Python processing layer to fetch real-time Foreign Exchange (Forex) rates for international clients.
* **Logic:** Normalized all margins to the base currency (INR) for accurate C-Suite reporting in the `Margin_Summary` materialized views.

---

## 💾 Database Schema (Simplified)

| Table Name | Description |
| :--- | :--- |
| `finance_invoices` | The immutable record of generated bills. |
| `finance_credit_notes` | Adjustments and refunds (Append-only). |
| `provider_pricing_rules` | JSON-based rules for Radiologist payouts (Grade/Modality logic). |
| `client_pricing_rules` | Tiered pricing logic for Hospitals. |
| `margin_summary` | Pre-aggregated table updating hourly for instant C-Level dashboard visibility. |

---

## 💻 Tech Stack
* **Language:** Python 3.9+
* **API Framework:** FastAPI
* **Orchestration:** Prefect
* **Database:** PostgreSQL (Microservices Architecture)
* **Containerization:** Docker
