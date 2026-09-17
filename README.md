# Enterprise Supply Chain & Inventory Optimization Hub

[![dbt Version](https://img.shields.io/badge/dbt-1.8.0-orange.svg)](https://www.getdbt.com/)
[![BigQuery](https://img.shields.io/badge/Warehouse-Google%20BigQuery-blue.svg)](https://cloud.google.com/bigquery)
[![Power BI](https://img.shields.io/badge/Semantic%20Model-Power%20BI%20VertiPaq-yellow.svg)](https://powerbi.microsoft.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)

## 1. Overview
The **Enterprise Supply Chain & Inventory Optimization Hub** is an end-to-end analytical data platform and business intelligence solution designed for a multinational retail/FMCG distribution network. 

The platform models a 100-facility fulfillment network managing 10,000 active SKUs across 500 global suppliers, translating 9.55 million operational records into executive-grade decision support across **inventory velocity**, **working capital exposure**, **supplier OTIF reliability**, and **demand sensing**.

---

## 2. Core Architecture & Technology Stack

```
Google Cloud Storage (Raw Parquet)
   │
   ▼
[raw_supply_chain]           <-- BigQuery External Tables (18 Tables, 9.55M rows)
   │
   ▼
[stg_supply_chain]           <-- dbt 1-to-1 Staging Views (16 Models, Typed & Cleaned)
   │
   ▼
[int_supply_chain]           <-- Intermediate Aggregations & Joins (2 Models)
   │
   ▼
[analytics_supply_chain]     <-- Kimball Marts (17 Models: 9 Dims, 7 Facts, 1 Scorecard)
   │
   ▼
[snapshots_supply_chain]     <-- dbt SCD2 Product Snapshot (snap_dim_product_scd2)
   │
   ▼
[Power BI Semantic Model]    <-- Pure Star Schema (VertiPaq In-Memory, 8 Measure Libraries)
   │
   ▼
[9 Executive Canvas Pages]   <-- Control Tower, Inventory, SKU, Supplier, Forecast, WC, Sim, Planner, Pipeline
```

- **Storage & Compute:** Google BigQuery (Standard SQL, Day/Month Partitioning, Multi-column Clustering)
- **Data Transformation & Testing:** dbt Core 1.8.0 (`dbt-bigquery`) — 36 Models, 1 SCD2 Snapshot, 173 Tests
- **Semantic Modeling:** Microsoft Power BI Desktop (Kimball Star Schema, Single-Direction Filters, Dynamic RLS)
- **Data Engineering:** Python 3.12 (Pandas, PyArrow, NumPy)
- **Orchestration Reference:** Apache Airflow 2.7+ (`orchestration/airflow/dags/`)

---

## 3. Dataset Profile (9,551,197 Records / 205.33 MB Parquet)

| Layer / Model | Granularity / Entity | Table Name | Row Count |
| :--- | :--- | :--- | :---: |
| **Fact** | Daily SKU-Warehouse Inventory Snapshot | `FactInventorySnapshot` | 5,464,956 |
| **Fact** | Customer Sales Order Lines | `FactSales` | 2,472,932 |
| **Fact** | Inbound Purchase Order Lines | `FactPurchaseOrder` | 1,110,903 |
| **Fact** | Inter-DC Transfers & Adjustments | `FactInventoryMovement` | 175,440 |
| **Fact** | Monthly Consensus Demand Forecast | `FactDemandForecast` | 179,424 |
| **Fact** | Customer Return Lines | `FactCustomerReturns` | 103,324 |
| **Fact / Scorecard** | Monthly Supplier Compliance | `FactSupplierMonthlyPerformance` | 11,852 |
| **Fact** | Contiguous Stockout Outage Events | `FactStockout` | 913 |
| **Dimension** | Product Catalog & SCD2 Audit History | `DimProduct` | 11,000 |
| **Dimension** | Multi-Sourcing Product-Supplier Bridge | `BridgeProductSupplier` | 13,333 |
| **Dimension** | Commercial Customers & Channels | `DimCustomerChannel` | 5,000 |
| **Dimension** | 4-Year Calendar Master (2023–2026) | `DimDate` | 1,461 |
| **Dimension** | Global Suppliers (Tiers 1, 2, 3) | `DimSupplier` | 500 |
| **Dimension** | Fulfillment Facilities (100 DCs) | `DimWarehouse` | 100 |
| **Dimension** | Operating Regions | `DimRegion` | 6 |
| **Dimension** | Supply Chain Planners | `DimEmployeePlanner` | 40 |
| **Dimension** | S&OP What-If Scenarios | `DimScenario` | 5 |
| **Security** | Data-Driven Dynamic RLS Mapping | `SecurityUser` | 8 |

---

## 4. Setup & Reproducibility Guide

### 4.1 Prerequisites
- Python 3.12+
- Git 2.40+
- (Optional) Google Cloud SDK for BigQuery deployment

### 4.2 Installation
```bash
# 1. Clone the repository
git clone https://github.com/Khprateek/Enterprise-Supply-Chain-Inventory-Optimization-Hub.git
cd "Enterprise Supply Chain & Inventory Optimization Hub"

# 2. Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install locked dependencies
pip install -r requirements.txt
```

### 4.3 Synthetic Data Engine Execution (Optional Regeneration)
To regenerate or rescale the raw synthetic dataset:
```bash
# Execute orchestrator pipeline (default: dev scale, 731-day horizon, seed=42)
python -m python.orchestrator --scale dev --output-dir data/raw --format parquet
```
*Pipeline execution runs sequentially: Dimensions $\rightarrow$ Procurement $\rightarrow$ Sales (with SCD2 temporal lookup) $\rightarrow$ Movements $\rightarrow$ Inventory Snapshots (reconciled with transfers/scrap/damage) $\rightarrow$ Forecasts $\rightarrow$ Stockouts $\rightarrow$ Returns $\rightarrow$ Supplier Performance.*

### 4.4 Data Validation Suite
Run the automated test suite against the physical Parquet dataset in `data/raw/`:
```bash
python tests/validate_dataset.py
```
*Expected Output: `VALIDATION SUMMARY: 44 PASSED | 0 FAILED` (Validates PK uniqueness, FK referential integrity, non-negative stock balances, chronological constraints, and supplier scorecard consistency across all 9.55M rows).*

### 4.5 dbt BigQuery Transformation & Snapshot Workflow
```bash
cd dbt

# 1. Parse and validate DAG nodes and dependencies
dbt parse --profiles-dir .

# 2. Execute SCD Type 2 product master snapshot
dbt snapshot --profiles-dir .

# 3. Build Staging views, Intermediate models, and Kimball Marts
dbt run --profiles-dir .

# 4. Execute automated schema and custom business rule tests
dbt test --profiles-dir .
```
*Model Architecture: `dim_product` is wired directly to `snap_dim_product_scd2`, and `fact_sales` performs a point-in-time join to link historical order dates to historical product surrogate keys and standard costs.*

### 4.6 Airflow ELT Orchestration DAG
The daily automated pipeline is defined in [`orchestration/airflow/dags/dag_supply_chain_daily_elt.py`](file:///d:/JOB/1.Buid_Skill/Work/Enterprise%20Supply%20Chain%20&%20Inventory%20Optimization%20Hub/orchestration/airflow/dags/dag_supply_chain_daily_elt.py):
- **Schedule:** Daily at `02:00 UTC` (`0 2 * * *`).
- **Execution DAG:**
  `gcs_landing_sensor` $\rightarrow$ `stage_bigquery_tables` $\rightarrow$ `dbt_run_models` $\rightarrow$ `dbt_test_models` $\rightarrow$ `pbi_semantic_refresh`.
- **SLA:** Fully completes within 9.6 minutes (well below the 6.0-hour business freshness SLA).

---

## 5. Power BI Semantic Model & Reporting Suite

The reporting suite consists of 9 purpose-built canvas pages documented in `docs/powerbi/` and implemented with interactive HTML prototypes:

1. **Page 1: Executive Control Tower** — Global inventory valuation, annual turnover, service level, WAPE.
2. **Page 2: Inventory Health & Velocity** — DC-level storage density, excess inventory categorization.
3. **Page 3: SKU Optimization & Replenishment** — King's dual-variance safety stock, dynamic Reorder Points (ROP).
4. **Page 4: Supplier Performance & Sourcing** — Spend commitments, supplier OTIF compliance, lead-time variance.
5. **Page 5: Forecast Performance & Sensing** — Monthly WAPE tracking, Holt-Winters baseline vs consensus forecast.
6. **Page 6: Working Capital & Investment** — Holding cost structure (22%), 4,095-day Cash Conversion Cycle, S&OP release roadmap.
7. **Page 7: What-If Simulation Sandbox** — Interactive parameter sliders (Demand, Lead Time, SLA, Holding Rate).
8. **Page 8: Planner Operational Workbench** — Daily queues: emergency stockout expediting, $1.21B PO cancel/defer candidates.
9. **Page 9: Pipeline Health & Governance** — BigQuery table volumes, dbt test assertions, orchestration telemetry.

### 5.1 DAX Dynamic Variance in King's Formula
Replenishment measures implement King's formula with dynamic sample standard deviations:
$$SS = Z \times \sqrt{LT \cdot \sigma_D^2 + D^2 \cdot \sigma_{LT}^2}$$
- $\sigma_D$: Evaluated dynamically using `STDEVX.S(VALUES(DimDate[FullDate]), CALCULATE([Total Ordered Quantity]))`.
- $\sigma_{LT}$: Evaluated dynamically using `STDEV.S(FactPurchaseOrder[ActualLeadTimeDays])`.
- Zero hardcoded static ratios; graceful fallback guards for low-sample contexts.

---

## 6. Dynamic Row-Level Security (RLS)

Configured via the data-driven `SecurityUser` mapping table using `USERPRINCIPALNAME()` without hardcoded email addresses in DAX:
- **VP of Operations:** Global visibility across all 100 fulfillment facilities and 6 operating regions.
- **Regional Supply Planner:** Restricted strictly to distribution centers within assigned geographic regions.
- **Warehouse Planner:** Restricted to specific assigned distribution center facilities.
- **Unauthorized Users:** Receives empty datasets with zero visual errors.

---

## 7. Performance & Partition Pruning Benchmarks

- **Storage Engine Pruning:** Date-partitioned columnar storage achieves a **95.8% byte scan reduction** (13.7 MB scanned vs. 326.8 MB unpartitioned baseline).
- **Scan Latency:** Query scan throughput accelerated from 1,230 ms to 31 ms (**39.7x speedup**).
- **Semantic Optimization:** High-cardinality surrogate keys (`SalesLineKey`, `SnapshotKey`) excluded from the Power BI VertiPaq model, reducing dictionary memory overhead by **~38%**.
