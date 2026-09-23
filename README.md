# Enterprise Supply Chain & Inventory Optimization Hub

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![dbt](https://img.shields.io/badge/dbt_Core-1.8.0-FF694B?logo=dbt&logoColor=white)](https://www.getdbt.com/)
[![BigQuery](https://img.shields.io/badge/Google_BigQuery-Cloud_DW-4285F4?logo=google-cloud&logoColor=white)](https://cloud.google.com/bigquery)
[![Airflow](https://img.shields.io/badge/Apache_Airflow-2.7+-017CEE?logo=apache-airflow&logoColor=white)](https://airflow.apache.org/)
[![Power BI](https://img.shields.io/badge/Power_BI-Semantic_Model-F2C811?logo=power-bi&logoColor=black)](https://powerbi.microsoft.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**An end-to-end, production-grade cloud data platform for enterprise supply chain analytics.**  
Models a 100-facility fulfillment network across 9.55M operational records — from raw ingestion to executive dashboards.

[Architecture](#architecture) · [Data Model](#dimensional-model) · [Quick Start](#quick-start) · [Dashboards](#dashboards) · [Docs](docs/)

</div>

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Dataset Profile](#dataset-profile)
5. [Dimensional Model](#dimensional-model)
6. [Data Quality Framework](#data-quality-framework)
7. [Performance Engineering](#performance-engineering)
8. [Orchestration](#orchestration)
9. [Dashboards](#dashboards)
10. [Dynamic Row-Level Security](#dynamic-row-level-security)
11. [Quick Start](#quick-start)
12. [Project Structure](#project-structure)
13. [Key Analytics & KPIs](#key-analytics--kpis)

---

## Project Overview

The **Enterprise Supply Chain & Inventory Optimization Hub** is a full-stack analytical data platform built to demonstrate enterprise-grade data engineering for a fictional multinational retail/FMCG organization.

The platform enables supply chain planners and operations executives to answer:

| Business Question | Analytics Capability |
|:---|:---|
| Where are we overstocked or at stockout risk? | SKU-level Days-of-Inventory & Stockout event tracking |
| What is our working capital exposure? | Inventory value × carrying cost, excess stock identification |
| Which suppliers are causing lead-time problems? | Supplier OTIF, lead-time variance, PO cycle time |
| How accurate are our demand forecasts? | WAPE, MAPE, forecast bias at SKU-warehouse-month grain |
| What safety stock do we actually need? | King's Dynamic Safety Stock formula with live demand and LT volatility |
| How does performance vary by region / warehouse? | Region → Warehouse drill-through with dynamic RLS |

**Scale:** 9.55M operational records · 100 fulfillment facilities · 10,000 active SKUs · 500 global suppliers · 4-year horizon (2023–2026)

---

## Architecture

The platform implements an **8-layer, cloud-native ELT architecture** following Kimball dimensional modelling methodologies with strict separation of concerns between ingestion, transformation, semantic modelling, and presentation.

```
┌──────────────────────────────────────────────────────────────────────┐
│  1. SOURCE SYSTEMS                                                   │
│  ERP · WMS · TMS · APS · Reverse Logistics                           │
└────────────────────────────┬─────────────────────────────────────────┘
                             │  Python 3.12 Vectorized Simulation Engine
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│  2. LANDING / RAW ZONE  (GCS / data/raw/)                            │
│  Immutable Parquet files  ·  _ingested_at · _source · _batch_id      │
└────────────────────────────┬─────────────────────────────────────────┘
                             │  Quality Gate 1 · Schema & Format Validation
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│  3. STAGING LAYER  (BigQuery  stg_supply_chain)                      │
│  16 dbt Views  ·  Type-cast · Deduplicate · Null-remediation         │
└────────────────────────────┬─────────────────────────────────────────┘
                             │  Quality Gate 2 · dbt PK Uniqueness & Not Null
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│  4. TRANSFORMATION ENGINE  (dbt Core 1.8.0)                          │
│  Surrogate keys · SCD Type 2 snapshot · Conformed star schema        │
└────────────────────────────┬─────────────────────────────────────────┘
                             │  Quality Gate 3 · Referential Integrity & Balance
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│  5. ANALYTICAL WAREHOUSE  (Google BigQuery)                          │
│  9 Conformed Dims · 8 Partitioned Fact Tables · Materialized Marts   │
└────────────────────────────┬─────────────────────────────────────────┘
                             │  Quality Gate 4 · DAX / Warehouse Reconciliation
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│  6. SEMANTIC MODEL  (Power BI VertiPaq)                              │
│  Pure Star Schema · 8 DAX Measure Libraries · Dynamic RLS            │
└────────────────────────────┬─────────────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│  7. EXECUTIVE DASHBOARDS  (Power BI Desktop · 9 Canvas Pages)        │
│  Control Tower · Inventory · SKU · Supplier · Forecast · WC · Sim   │
└────────────────────────────┬─────────────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│  8. BUSINESS PERSONAS                                                │
│  VP Operations · Regional Planner · Warehouse Planner · Analyst      │
└──────────────────────────────────────────────────────────────────────┘
```

**Orchestration:** Apache Airflow 2.7+ `dag_supply_chain_daily_elt` triggers every day at **02:00 UTC** — GCS sensor → BigQuery partition sync → `dbt run` → `dbt test` (173 assertions) → Power BI REST API incremental refresh — completing end-to-end in **< 9.6 minutes** against a 6-hour business SLA.

---

## Technology Stack

| Layer | Tool / Technology | Version | Role |
|:---|:---|:---|:---|
| **Data Warehouse** | Google BigQuery | Standard SQL | Partitioned & clustered analytical storage and compute |
| **Transformation** | dbt Core (`dbt-bigquery`) | `1.8.0` | In-warehouse SQL transformation, SCD2, dimensional modeling, 173 data tests |
| **Orchestration** | Apache Airflow | `2.7+` | Daily ELT pipeline scheduling, GCS sensing, dbt CLI, Power BI API trigger |
| **Semantic Model** | Microsoft Power BI Desktop | VertiPaq | Star schema, DAX business logic, dynamic RLS, 9 executive report pages |
| **Data Engineering** | Python | `3.12` | Vectorized synthetic data engine, raw validation test suite |
| **Data Processing** | Pandas / NumPy | `2.2.2` / `2.4.3` | Dataframe vectorization and supply chain calculations |
| **File Format** | Apache Parquet (PyArrow) | `16.1.0` | Columnar file serialization with compression and audit metadata |
| **Local Warehousing** | DuckDB | `≥ 1.0.0` | Local query engine for offline development & testing (`dbt-duckdb`) |
| **Storage (Cloud)** | Google Cloud Storage | — | Raw landing zone for daily Parquet file payloads |
| **IAM / Security** | GCP IAM Service Accounts | — | Least-privilege BigQuery access (`Data Viewer` + `Job User`) |
| **Version Control** | Git / GitHub | `2.40+` | Source control, schema drift tracking, multi-environment branching |

---

## Dataset Profile

**9,551,197 records · 205.33 MB Parquet** across 18 structured entities.

### Fact Tables

| Model | Business Process | Grain | Row Count | Partition Field |
|:---|:---|:---|---:|:---|
| `FactInventorySnapshot` | Daily physical stock balance | SKU × Warehouse × Day | **5,464,956** | `snapshot_date` (Day) |
| `FactSales` | Customer order fulfillment | Sales order line | **2,472,932** | `order_date` (Day) |
| `FactPurchaseOrder` | Inbound procurement | PO line | **1,110,903** | `po_creation_date` (Day) |
| `FactDemandForecast` | S&OP consensus planning | SKU × Warehouse × Month | **179,424** | `target_period_date` (Month) |
| `FactInventoryMovement` | Inter-DC transfers & adjustments | Movement line | **175,440** | `movement_date` (Day) |
| `FactCustomerReturns` | Reverse logistics | Return line | **103,324** | `return_date` (Month) |
| `FactSupplierMonthlyPerformance` | Supplier OTIF scorecard | Supplier × Month | **11,852** | `year_month` (Month) |
| `FactStockout` | Contiguous zero-stock outage events | Outage event | **913** | `outage_start_date` (Day) |

### Dimension & Reference Tables

| Model | Description | Cardinality |
|:---|:---|---:|
| `DimProduct` | Product catalog with SCD Type 2 audit history | 11,000 |
| `BridgeProductSupplier` | M:N product–supplier sourcing relationships | 13,333 |
| `DimCustomerChannel` | Commercial accounts across wholesale / retail / e-commerce | 5,000 |
| `DimDate` | 4-year calendar master (2023–2026) with fiscal periods | 1,461 |
| `DimSupplier` | Global supplier profiles (Tier 1, 2, 3) | 500 |
| `DimWarehouse` | Fulfillment facility master (100 DCs) | 100 |
| `DimRegion` | Operating geographic regions | 6 |
| `DimEmployeePlanner` | Supply chain planners for RLS mapping | 40 |
| `DimScenario` | S&OP What-If simulation baselines | 5 |
| `SecurityUser` | Data-driven dynamic RLS user mapping | 8 |

---

## Dimensional Model

The warehouse follows a **Kimball star schema** with conformed dimensions supporting cross-process drill-through.

```
                        ┌─────────────┐
                        │   DimDate   │
                        │ (Role-play: │
                        │  OrderDate  │
                        │  ShipDate   │
                        │  DelivDate) │
                        └──────┬──────┘
                               │
          ┌─────────────┐      │      ┌────────────────┐
          │ DimCustomer │      │      │  DimWarehouse  │
          │  Channel    ├──────┤      ├────────────────┤
          └─────────────┘      │      │   DimRegion    │
                               │      └────────┬───────┘
          ┌─────────────┐      │               │
          │ DimProduct  ├──────┼───── FactSales / FactInventorySnapshot ──── DimScenario
          │  (SCD2)     │      │               │                             DimPlanner
          └──────┬──────┘      │      ┌────────┴───────┐
                 │             │      │  DimSupplier   │
    ┌────────────┴──────┐      │      └────────────────┘
    │ BridgeProduct     │      │
    │ Supplier (M:N)    │      │
    └───────────────────┘      │
                               ▼
                    FactPurchaseOrder / FactDemandForecast
                    FactInventoryMovement / FactStockout
                    FactCustomerReturns / FactSupplierMonthlyPerformance
```

**Advanced Modeling Patterns Implemented:**

- **SCD Type 2** — `snap_dim_product_scd2` tracks standard cost drifts and category reclassifications with `effective_date`, `expiry_date`, and `is_current_flag`. `FactSales` executes a point-in-time join to the historical surrogate key at order date.
- **Role-Playing Date Dimension** — `DimDate` is aliased across Order Date, Ship Date, Delivery Date, and Expected Delivery Date without ambiguous relationships.
- **Many-to-Many Bridge** — `BridgeProductSupplier` resolves genuine M:N sourcing relationships (multi-sourced SKUs across Tier 1/2/3 suppliers).
- **Surrogate Key Generation** — All dimensional surrogate keys use deterministic `FARM_FINGERPRINT()` hashing ensuring idempotent pipeline runs.

---

## Data Quality Framework

**Four validation gates prevent corrupt, duplicate, or un-reconciled data from propagating into executive reporting.**

```
Gate 1 [Raw]     → Python test suite  · 44 assertions  · PK uniqueness, FK integrity, non-negative stock
Gate 2 [Staging] → dbt source tests   · unique, not_null, accepted_values, relationships
Gate 3 [Marts]   → dbt custom SQL     · Referential integrity, inventory balance equations, business constraints
Gate 4 [BI]      → DAX reconciliation · Measure totals reconciled against BigQuery aggregates
```

**dbt Test Suite:** 173 automated assertions covering:

| Test Category | Examples |
|:---|:---|
| Primary Key Uniqueness | All 17 staging models: `unique` + `not_null` on natural/surrogate keys |
| Referential Integrity | All fact → dimension foreign key `relationships` tests |
| Business Constraint | Non-negative `on_hand_quantity`, lead time within 1–365 days, unit price > 0 |
| Accepted Values | `movement_type` ∈ `{TRANSFER, RECEIPT, ADJUSTMENT, SCRAP}`, `return_reason` codes |
| Inventory Balance | `OnHand_t = OnHand_{t-1} + Receipts + Adjustments − Sales − Transfers` |

Run the full offline validation suite against raw Parquet:

```bash
python tests/validate_dataset.py
# Expected: VALIDATION SUMMARY: 44 PASSED | 0 FAILED
```

---

## Performance Engineering

BigQuery analytical workloads are engineered for partition pruning and clustered block reads across all major fact tables.

### Partition Pruning Benchmarks

| Metric | Unpartitioned Baseline | Partitioned + Clustered | Improvement |
|:---|---:|---:|---:|
| Bytes scanned (30-day inventory query) | 326.8 MB | 13.7 MB | **95.8% reduction** |
| Query scan latency | 1,230 ms | 31 ms | **39.7× speedup** |

### Clustering Strategy

```sql
-- FactInventorySnapshot  →  CLUSTER BY product_key, warehouse_key
-- FactSales              →  CLUSTER BY product_key, warehouse_key, customer_channel_key
-- FactPurchaseOrder      →  CLUSTER BY supplier_key, product_key, receiving_warehouse_key
-- DimProduct             →  CLUSTER BY primary_supplier_key, category_name
-- BridgeProductSupplier  →  CLUSTER BY supplier_key, product_sku
```

### Power BI VertiPaq Optimization

- High-cardinality surrogate columns (`SalesLineKey`, `SnapshotKey`) excluded from the semantic model, reducing dictionary memory overhead by **~38%**.
- Bi-directional relationships strictly minimized — all dimension → fact filter propagation is single-direction.
- Incremental refresh configured on `FactInventorySnapshot` and `FactSales` for large historical table partitions.

---

## Orchestration

The production ELT pipeline is managed by Apache Airflow 2.7+ and runs daily at **02:00 UTC**.

**File:** [`orchestration/airflow/dags/dag_supply_chain_daily_elt.py`](orchestration/airflow/dags/dag_supply_chain_daily_elt.py)

```
pipeline_start
      │
      ▼
check_gcs_raw_landing          ← GCSObjectsWithPrefixExistenceSensor (poke every 60s, timeout 30m)
      │
      ▼
sync_bigquery_raw_tables       ← BigQueryInsertJobOperator  (refresh external table partition metadata)
      │
      ▼
dbt_run_transformations        ← BashOperator  (dbt run --select staging intermediate marts)
      │
      ▼
dbt_test_suite                 ← BashOperator  (dbt test  · 173 assertions)
      │
      ▼
trigger_powerbi_refresh        ← SimpleHttpOperator  (Power BI REST API incremental refresh)
      │
      ▼
pipeline_end
```

| DAG Property | Value |
|:---|:---|
| Schedule | `0 2 * * *` (daily 02:00 UTC) |
| Max Active Runs | 1 |
| Retries | 2 (5-min delay) |
| Execution Timeout | 60 min per task |
| End-to-End SLA | < 6.0 hours (actual: **9.6 min**) |
| Failure Alerting | Email on failure (`email_on_failure: true`) |

---

## Dashboards

The Power BI reporting suite delivers **9 purpose-built canvas pages** with role-filtered views via Dynamic RLS.

| Page | Title | Key Metrics |
|:---:|:---|:---|
| 1 | **Executive Control Tower** | Inventory value, annual turns, service level, WAPE, working capital exposure |
| 2 | **Inventory Health & Velocity** | DC-level storage density, aging brackets (0–30, 31–60, 61–90, 91–180, 180+ days) |
| 3 | **SKU Optimization & Replenishment** | ABC-XYZ matrix, dynamic safety stock (King's formula), reorder point triggers |
| 4 | **Supplier Performance & Sourcing** | Spend commitments, supplier OTIF, lead-time variance, Tier 1/2/3 risk exposure |
| 5 | **Forecast Performance & Sensing** | WAPE trend, Holt-Winters baseline vs consensus forecast, SKU-level bias |
| 6 | **Working Capital & Investment** | Inventory carrying cost (22% holding rate), excess stock, S&OP release roadmap |
| 7 | **What-If Simulation Sandbox** | Interactive sliders: Demand growth, Lead-time shock, Service-level target, Carrying-cost rate |
| 8 | **Planner Operational Workbench** | Daily action queue: emergency expediting, PO cancel/defer candidates (\$1.21B identified) |
| 9 | **Pipeline Health & Governance** | BigQuery row volumes, dbt test assertion counts, Airflow DAG telemetry, last refresh timestamp |

### King's Dynamic Safety Stock Formula

Replenishment measures implement King's formula with **live sample standard deviations** (no hardcoded static ratios):

$$SS = Z \times \sqrt{LT \cdot \sigma_D^2 + \bar{D}^2 \cdot \sigma_{LT}^2}$$

- $\sigma_D$ — evaluated dynamically: `STDEVX.S(VALUES(DimDate[FullDate]), CALCULATE([Total Ordered Quantity]))`
- $\sigma_{LT}$ — evaluated dynamically: `STDEV.S(FactPurchaseOrder[ActualLeadTimeDays])`
- Graceful fallback guards applied for low-sample-size contexts

---

## Dynamic Row-Level Security

Access is enforced at the semantic model layer using a **data-driven `SecurityUser` mapping table** and `USERPRINCIPALNAME()` — no email addresses are hardcoded in DAX expressions.

| Role | Data Scope |
|:---|:---|
| **VP of Operations** | All 6 operating regions · All 100 fulfillment facilities |
| **Regional Supply Planner** | Assigned geographic regions only |
| **Warehouse Planner** | Assigned distribution centers only |
| **Unauthorized Users** | Empty dataset — zero visual errors, no data leakage |

---

## Quick Start

### Prerequisites

| Requirement | Version |
|:---|:---|
| Python | 3.12+ |
| Git | 2.40+ |
| Google Cloud SDK | Latest (optional, for BigQuery deployment) |
| dbt Core | 1.8.0 (installed via `requirements.txt`) |

### 1. Clone & Install

```bash
git clone https://github.com/Khprateek/Enterprise-Supply-Chain-Inventory-Optimization-Hub.git
cd "Enterprise Supply Chain & Inventory Optimization Hub"

python -m venv venv
# Windows
.\\venv\\Scripts\\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Generate the Synthetic Dataset (Optional — pre-built Parquet files included)

```bash
# Default dev scale: 731-day horizon, seed=42
python -m python.orchestrator --scale dev --output-dir data/raw --format parquet
```

Pipeline execution sequence:
`Dimensions → Procurement → Sales (SCD2 point-in-time) → Movements → Inventory Snapshots → Forecasts → Stockouts → Returns → Supplier Scorecard`

### 3. Run the Raw Validation Suite

```bash
python tests/validate_dataset.py
# Expected: VALIDATION SUMMARY: 44 PASSED | 0 FAILED
```

### 4. Run the dbt Transformation Pipeline

```bash
cd dbt

# Validate DAG structure and node dependencies
dbt parse --profiles-dir .

# Execute SCD Type 2 product master snapshot
dbt snapshot --profiles-dir .

# Build staging views, intermediate models, and Kimball dimensional marts
dbt run --profiles-dir .

# Run the full automated data quality test suite (173 assertions)
dbt test --profiles-dir .
```

### 5. Open the Power BI Semantic Model

Open the `.pbix` file in **Power BI Desktop**, configure the BigQuery connection using your GCP service account credentials, and trigger a full dataset refresh.

---

## Project Structure

```
Enterprise Supply Chain & Inventory Optimization Hub/
│
├── data/
│   ├── raw/                        # Immutable Parquet landing files (9.55M rows, 205 MB)
│   └── staging/                    # Local staging intermediates
│
├── python/
│   ├── orchestrator.py             # Master pipeline entrypoint
│   ├── generate_dimensions.py      # Dimension master generation (regions, warehouses, SKUs, suppliers)
│   ├── generate_procurement.py     # FactPurchaseOrder with realistic lead-time distributions
│   ├── generate_sales.py           # FactSales with seasonality, channel mix, SCD2 price lookups
│   ├── generate_inventory.py       # Stateful FactInventorySnapshot (daily balance continuity)
│   ├── generate_movements.py       # FactInventoryMovement (inter-DC transfers, scrap, adjustments)
│   ├── generate_forecast.py        # FactDemandForecast (Holt-Winters + consensus overlay)
│   ├── generate_stockouts.py       # FactStockout (contiguous zero-stock event consolidation)
│   ├── generate_returns.py         # FactCustomerReturns (reverse logistics with reason codes)
│   ├── generate_supplier_perf.py   # FactSupplierMonthlyPerformance (OTIF scorecard)
│   └── config.py                   # Centralized generation parameters and seeds
│
├── dbt/
│   ├── models/
│   │   ├── staging/                # 16 stg_* views (type-cast, deduplicate, normalize)
│   │   ├── intermediate/           # 2 int_* aggregation and join models
│   │   └── marts/
│   │       ├── dimensions/         # 9 conformed dimension tables
│   │       ├── facts/              # 7 partitioned & clustered fact tables
│   │       └── scorecards/         # FactSupplierMonthlyPerformance materialized mart
│   ├── snapshots/                  # snap_dim_product_scd2 (SCD Type 2)
│   ├── tests/                      # Custom SQL business rule assertions
│   ├── macros/                     # Reusable dbt macro utilities
│   └── dbt_project.yml
│
├── orchestration/
│   └── airflow/
│       └── dags/
│           └── dag_supply_chain_daily_elt.py   # Production daily ELT DAG
│
├── tests/
│   └── validate_dataset.py         # 44-assertion raw Parquet validation suite
│
├── docs/
│   ├── architecture/               # Architecture diagrams, data flow, performance benchmarks
│   ├── data-model/                 # Dimensional model specifications and grain definitions
│   ├── business/                   # KPI definitions, business rule documentation
│   ├── powerbi/                    # DAX measure catalogue, RLS design, report walkthroughs
│   ├── testing/                    # Test strategy, quality gate specifications
│   └── decisions/                  # Architecture Decision Records (ADRs)
│
├── powerbi/                        # Power BI Desktop report files (.pbix)
├── sql/                            # Standalone BigQuery DDL and diagnostic queries
├── scripts/                        # Utility scripts (architecture diagram generation)
├── requirements.txt                # Locked Python dependencies
└── PROJECT_CONTEXT.md              # Full project specification and design rules
```

---

## Key Analytics & KPIs

### Inventory

| KPI | Definition |
|:---|:---|
| Days of Inventory (DOI) | `Avg On-Hand ÷ Avg Daily Demand` |
| Inventory Turns | `Annual COGS ÷ Avg Inventory Value` |
| Excess Inventory | Stock exceeding DOI threshold vs ABC-XYZ classification |
| Stockout Rate | `Stockout Events ÷ Total SKU-Warehouse-Days` |

### Demand Forecasting

| KPI | Definition |
|:---|:---|
| WAPE | `Σ|Forecast − Actual| ÷ Σ Actual` (weighted, avoids small-volume distortion) |
| Forecast Bias | `Σ(Forecast − Actual) ÷ Σ Actual` (positive = over-forecast) |

### Procurement & Supply

| KPI | Definition |
|:---|:---|
| Supplier OTIF | `On-Time In-Full lines ÷ Total PO lines` |
| Lead-Time Variability | `StdDev(ActualLeadTimeDays)` per supplier |
| PO Cycle Time | `ReceiptDate − POCreationDate` |

### ABC-XYZ Segmentation

| Class | Basis | Implication |
|:---|:---|:---|
| **A / B / C** | Contribution to annual consumption value | Priority tier for replenishment and working capital focus |
| **X / Y / Z** | Coefficient of Variation of demand | Inventory policy selection (MTS / MTO / VMI) |

---

## Documentation

| Document | Location |
|:---|:---|
| Architecture Overview | [`docs/architecture/architecture_overview.md`](docs/architecture/architecture_overview.md) |
| End-to-End Data Flow | [`docs/architecture/data_flow.md`](docs/architecture/data_flow.md) |
| BigQuery Setup & Security | [`docs/architecture/bigquery_setup_and_security.md`](docs/architecture/bigquery_setup_and_security.md) |
| Performance & Partitioning | [`docs/architecture/warehouse_performance_and_optimization.md`](docs/architecture/warehouse_performance_and_optimization.md) |
| Raw Layer Specification | [`docs/architecture/raw_layer_specification.md`](docs/architecture/raw_layer_specification.md) |
| Environment Configuration | [`docs/architecture/environments.md`](docs/architecture/environments.md) |
| Full Project Specification | [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) |

---

## License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">
Built as a portfolio demonstration of enterprise data engineering, Kimball dimensional modelling, dbt transformation pipelines, and cloud BI architecture.
</div>
