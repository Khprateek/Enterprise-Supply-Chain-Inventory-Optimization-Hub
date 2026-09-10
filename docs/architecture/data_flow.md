# End-to-End Data Flow Specification: Supply Chain & Inventory Optimization Hub

This document defines the complete movement, transformation, and validation lifecycle of data through the Enterprise Supply Chain & Inventory Optimization Hub.

---

## 1. High-Level Data Flow Overview

`
+-----------------------------------------------------------------------------+
| 1. DATA GENERATION & EXTRACTION                                             |
| Python 3.12 Synthetic Engine (Stateful inventory continuity, seasonal demand)|
+-----------------------------------------------------------------------------+
                                       │
                                       ▼ (Write Parquet / CSV + metadata)
+-----------------------------------------------------------------------------+
| 2. LANDING / RAW ZONE (data/raw/ / GCS)                                   |
| Immutable raw source files with _ingested_at & _batch_id                |
+-----------------------------------------------------------------------------+
                                       │
                                       ▼ (Gate 1: Schema & Format Validation)
+-----------------------------------------------------------------------------+
| 3. STAGING ZONE (data/staging/ / BigQuery stg_*)                        |
| Deduplication, type casting, key standardization, null remediation          |
+-----------------------------------------------------------------------------+
                                       │
                                       ▼ (Gate 2: dbt Source Freshness & PK Tests)
+-----------------------------------------------------------------------------+
| 4. TRANSFORMATION & CONFORMED DIMENSIONS (dbt DAG)                          |
| Surrogate keys, SCD Type 2 tracking, conformed star schema models            |
+-----------------------------------------------------------------------------+
                                       │
                                       ▼ (Gate 3: Referential Integrity & Business Logic)
+-----------------------------------------------------------------------------+
| 5. ANALYTICAL WAREHOUSE (BigQuery Partitioned / Clustered Tables)           |
| Conformed Star Schema + Materialized Marts (FactSupplierMonthlyPerformance)|
+-----------------------------------------------------------------------------+
                                       │
                                       ▼ (Gate 4: Reconciliation & Anomaly Tests)
+-----------------------------------------------------------------------------+
| 6. SEMANTIC MODELING & REPORTING (Power BI Desktop / VertiPaq)              |
| 1-to-many relationships, explicit DAX business measures, 5 dashboard pages   |
+-----------------------------------------------------------------------------+
                                       │
                                       ▼
+-----------------------------------------------------------------------------+
| 7. USER DECISION SUPPORT                                                    |
| VP of Operations, Regional Planners, Warehouse Ops, Procurement, Analysts    |
+-----------------------------------------------------------------------------+
`

---

## 2. Step-by-Step Data Flow Stages

### Stage 1: Data Generation & Source Extraction
- **Engine:** Python 3.12 vectorized data synthesis scripts (python/).
- **Cadence:** Batch execution (simulating daily and periodic enterprise extracts).
- **Core Generation Sequences:**
  1. *Master Dimension Data:* Generates global regions, warehouses, supplier profiles (with lead-time distributions), product catalog hierarchies (thousands of SKUs across categories/brands), and calendar dates.
  2. *Demand Planning:* Generates seasonal and promotional demand curves, generating FactDemandForecast at SKU-Warehouse-TargetMonth grain.
  3. *Procurement Execution:* Simulates purchase order placement, supplier fulfillment, delivery lead times (with realistic supplier variance), and dock receipt inspections, generating FactPurchaseOrder.
  4. *Sales Orders:* Simulates customer orders across wholesale, retail, and e-commerce channels with day-of-week seasonality, generating FactSales.
  5. *Stateful Inventory Snapshot:* Executes daily balance continuity equations:
     \\text{OnHand}_t = \\text{OnHand}_{t-1} + \\text{Receipts}_t + \\text{Adjustments}_t - \\text{Sales}_t - \\text{OutwardTransfers}_t
     Generates daily snapshots for all active SKU-Warehouse combinations (FactInventorySnapshot).
  6. *Inventory Movements & Returns:* Simulates inter-DC transfers, spoilage scrap, and customer return dispositions (FactInventoryMovement, FactCustomerReturns).
- **Output:** Structured files written to data/raw/ in Parquet and CSV formats.

---

### Stage 2: Landing / Raw Ingestion
- **Storage Target:** Local directory data/raw/<entity>/ (or Google Cloud Storage gs://<bucket>/raw/<entity>/).
- **File Naming Convention:** <entity>_YYYYMMDD_batch<ID>.parquet.
- **Enrichment:** Every file includes system audit columns:
  - _source_file_name (STRING)
  - _ingested_at (TIMESTAMP UTC)
  - _batch_id (STRING / UUID)
- **Immutability Policy:** Raw files are read-only and never modified or deleted. Re-ingestion creates a new timestamped file.

---

### Stage 3: Staging & Normalization
- **Mechanism:** dbt staging models (dbt/models/staging/stg_*.sql) or Python preprocessing pipelines.
- **Transformations Applied:**
  - **Data Type Casting:** String timestamps cast to DATE or TIMESTAMP; quantities to INT64; monetary values to NUMERIC(12, 2).
  - **Whitespace & Case Trimming:** UPPER(TRIM(product_code)), TRIM(supplier_id).
  - **Natural Key Deduplication:** Applies ROW_NUMBER() OVER (PARTITION BY business_key ORDER BY _ingested_at DESC) to retain the latest authoritative record.
  - **Default Null Replacement:** Replaces null foreign keys with standard sentinel values (-1 or 'UNKNOWN') to prevent orphan records in star schema joins.
  - **Basic Sanity Filters:** Flags or excludes corrupted records (e.g., negative unit prices, receipts predating PO creation dates).

---

### Stage 4: Transformation & Dimensional Modeling
- **Mechanism:** dbt-core execution DAG (dbt run).
- **Model Dependencies & Execution Flow:**

`
[stg_products]  ───►  [dim_product (SCD Type 2)]  ───┐
[stg_suppliers] ───►  [dim_supplier]              ───┤
[stg_warehouses]───►  [dim_warehouse]             ───┤
[stg_calendar]  ───►  [dim_date]                  ───┼──► [fact_sales]
                                                     ├──► [fact_purchase_order]
                                                     ├──► [fact_inventory_snapshot]
                                                     ├──► [fact_demand_forecast]
                                                     ├──► [fact_inventory_movement]
                                                     └──► [fact_customer_returns]
                                                                  │
              ┌───────────────────────────────────────────────────┘
              ▼
[fact_inventory_snapshot] ──► [fact_stockout (Derived continuous outage events)]
[fact_purchase_order]     ──► [fact_supplier_monthly_performance (Materialized mart)]
`

- **Key Business Transformations:**
  1. *Surrogate Key Assignment:* Assigns deterministic integer keys using FARM_FINGERPRINT() or surrogate key macros.
  2. *SCD Type 2 Tracking:* Tracks attribute changes in dim_product (e.g., cost adjustments, supplier changes) with is_current, alid_from, and alid_to timestamps.
  3. *Continuous Stockout Consolidation:* Groups consecutive zero-inventory snapshot dates into unified outage events with calculated duration and lost revenue estimates.
  4. *Materialized Supplier Performance Mart:* Aggregates monthly vendor receipts, computing OTIF rates and lead-time standard deviations.

---

### Stage 5: Analytical Warehouse Storage (BigQuery)
- **Target Dataset:** BigQuery nalytics (or dbt_prod / supply_chain_analytics).
- **Physical Layout & Performance Configurations:**
  - act_inventory_snapshot: Partitioned by SnapshotDate (DAY); Clustered by ProductKey, WarehouseKey.
  - act_sales: Partitioned by OrderDate (DAY); Clustered by ProductKey, CustomerChannelKey.
  - act_purchase_order: Partitioned by POCreationDate (DAY); Clustered by SupplierKey, ProductKey.
  - dim_*: Clustered by primary surrogate key.
- **Access Control:** Restricted via Google Cloud IAM; service accounts utilized for dbt transformations and read-only BI connections.

---

### Stage 6: Semantic Modeling & Power BI Refresh
- **Tool:** Microsoft Power BI Desktop.
- **Connection Mode:** **Import Mode** via native Google BigQuery connector (or local Parquet imports during local testing).
- **In-Memory Architecture:**
  - Data ingested into the VertiPaq in-memory engine.
  - Pure Star Schema: 1-to-many single-direction relationships from dimensions to fact tables.
  - Explicit DAX measures created in dedicated measure groups (e.g., _InventoryMeasures, _ProcurementMeasures, _ForecastMeasures).
  - Column optimization: High-cardinality technical IDs hidden from report fields; integer keys used for relationships.

---

### Stage 7: Executive & Operational Consumption
- **Delivery:** 5 role-based Power BI report pages + dynamic scenario simulation controls.
- **Reporting Cadence:** Interactive query access with <= 3-second visual response times.
- **Operational Outputs:**
  - Automated Red/Amber/Green alerts for SKUs below Reorder Point.
  - Multi-year supplier reliability scorecards.
  - Trailing 12-month inventory turnover and working-capital exposure trendlines.

---

## 3. Data Quality & Validation Gates

The data flow enforces four mandatory quality validation gates:

| Quality Gate | Location | Enforcing Tool | Rules / Assertions Enforced | Failure Action |
| :--- | :--- | :--- | :--- | :--- |
| **Gate 1: Format & Completeness** | Raw Landing | Python Validation Scripts | Valid Parquet schema, required columns present, non-empty files. | Quarantine malformed files; alert administrator. |
| **Gate 2: Staging Cleansing** | Staging | dbt Source Tests | Primary key uniqueness, non-null mandatory fields, valid date ranges. | Halt staging pipeline; log duplicate or invalid records. |
| **Gate 3: Referential Integrity** | Transformation | dbt Schema & Custom Tests | Foreign keys in facts must exist in conformed dimensions (
elationships test). | Block fact table build if orphaned records exceed tolerance (0%). |
| **Gate 4: Business Reconciliation** | Warehouse & Semantic Model | dbt Audits & DAX Assertions | Inventory balance continuity (I_t = I_{t-1} + R - S), non-negative available stock, Turns * DOI ≈ 365. | Flag reconciliation variance in audit log visual. |\n