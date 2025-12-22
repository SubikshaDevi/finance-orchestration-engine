# Intelligent Financial Orchestration Engine

![Status](https://img.shields.io/badge/Status-Production-success)
![Role](https://img.shields.io/badge/Role-Data_Engineer-blue)
![Stack](https://img.shields.io/badge/Tech-Python_|_Prefect_|_FastAPI_|_PostgreSQL_|_Scikit--Learn-yellow)

**A dual-sided marketplace billing platform that automates payment reconciliation between Healthcare Providers (Radiologists) and Clients (Hospitals), fortified by an AI-driven anomaly detection layer.**

This system serves as the financial backbone for the company, managing the end-to-end lifecycle from raw usage data to immutable invoice generation. It combines deterministic financial logic with probabilistic ML auditing to ensure revenue integrity.

---

## 🚀 Business Impact
* **Scale:** Automates billing for **800+ invoices/month** across two distinct user bases.
* **Efficiency:** Reduced manual finance operations by **90%** (process time dropped from 5 days/month to minutes).
* **Revenue Assurance:** The AI audit layer catches "legal but suspicious" billing spikes (e.g., ratio anomalies), reducing potential revenue leakage and false positives by **~40%**.
* **Accuracy:** Eliminated manual Excel errors by enforcing strict schema validation and automated unit testing.

---

## 🏗️ System Architecture

![System Architecture Diagram](./engine%20architecture.png)
*(The AI Auditor operates within the Processing Layer, validating calculations before the final write to the Finance DB.)*

### 1. The Core Engine (The "Mediator" Pattern)
Unlike standard SaaS billing (subscription-based), this system operates as a mediator. Every transaction (Medical Report) triggers two distinct financial events:
1.  **Cost of Goods Sold (COGS):** The fee paid to the Radiologist (based on Grade, Seniority, Modality).
2.  **Revenue:** The fee charged to the Hospital (based on Volume Tier, Contract Type, Foreign Exchange Rate).

### 2. The AI Guardian ("Billing-Guard")
Integrated directly into the pipeline is a **Context-Aware Anomaly Detection Microservice**.
* **Problem:** Traditional rules fail to catch "Soft Anomalies" (e.g., a startup scaling 1000% is valid growth, but a mature vendor spiking 1000% is likely fraud).
* **Solution:** A hybrid filter that runs post-calculation:
    * **Hard Gate:** Enforces contract limits (e.g., "Max 300 Images").
    * **Soft Gate (ML):** Uses **Isolation Forest** to detect behavioral drift in ratios (e.g., *Images-per-Case*) rather than raw totals.

### 3. Data Pipeline (The "Windowed Sync")
* **Orchestrator:** Prefect (Python) triggers hourly sync jobs.
* **Strategy:** Implemented a **"Rolling Window" ETL pattern**.
    * The pipeline processes data from `Day 1` to `Current Timestamp` for the active month.
    * **Locking Mechanism:** Once a month is "Closed", data is virtually locked. Updates require a privileged "Rerun" action.

---

## 🛠️ Key Engineering Decisions

### 1. Hybrid Validation Strategy (Rules + AI)
* **Problem:** Pure rule-based systems miss complex fraud; Pure AI systems generate too many false positives on high-growth clients.
* **Solution:** I implemented a **Two-Stage Filter**:
    * **Stage 1 (Contract Enforcer):** Deterministic checks against the PostgreSQL `client_pricing_rules` table.
    * **Stage 2 (Pattern Watchdog):** An unsupervised learning model (Isolation Forest) that analyzes the *relationship* between volume and cost. This prevents the system from flagging legitimate hyper-growth startups as anomalies.

### 2. Immutable Ledger for Credit Notes
* **Problem:** Financial data must be auditable. Deleting an incorrect invoice violates accounting principles.
* **Solution:** Implemented an **Append-Only Architecture**.
    * If an invoice is incorrect, we generate a `Credit Note` (a new row) rather than modifying the original record.
    * **Final Statement Logic:** `Total Due = Sum(Invoices) - Sum(Credit Notes)`.

### 3. Handling Dynamic Pricing & Historical Reruns
* **Problem:** Pricing agreements change retrospectively.
* **Solution:** Built a **"Cost Rerun" API** that allows Finance Ops to target a specific historical window (e.g., "Jan 2023") and re-calculate margins using the configuration *from that point in time*.

---

## 💾 Database Schema (Simplified)

| Table Name | Description |
| :--- | :--- |
| `finance_invoices` | The immutable record of generated bills. |
| `finance_audit_logs` | **(New)** Stores AI flag reasons (e.g., "High Image Ratio: 10.0") for human review. |
| `finance_credit_notes` | Adjustments and refunds (Append-only). |
| `provider_pricing_rules` | JSON-based rules for Radiologist payouts. |
| `margin_summary` | Pre-aggregated table updating hourly for instant C-Level dashboards. |

---

## 💻 Tech Stack
* **Language:** Python 3.9+
* **Machine Learning:** Scikit-Learn (Isolation Forest), Pandas
* **API Framework:** FastAPI
* **Orchestration:** Prefect
* **Database:** PostgreSQL
* **Containerization:** Docker

