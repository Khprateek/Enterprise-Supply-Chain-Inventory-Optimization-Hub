# Power BI Report Canvas Architecture: Page 9 — Pipeline Health & Warehouse Data Governance

This document details the visual design specifications, visual hierarchy, layout grid, measure bindings, interaction mechanics, and telemetry monitoring for **Page 9: Pipeline Health & Warehouse Data Governance**.

---

## 1. Page Objective & Operational Context

Page 9 serves as the data observability and technical governance cockpit for the **Chief Data Officer (CDO)**, **Lead Analytics Engineers**, **Data Platform Architects**, and **Enterprise BI Administrators**. It guarantees reporting integrity by answering:
1. *Are all underlying BigQuery analytical warehouse tables refreshed within enterprise freshness SLAs (<6.0 hours)?*
2. *What is the total row volume and storage footprint across the Kimball warehouse layers?*
3. *What is the status and pass rate of the automated dbt test suite (schema, referential integrity, and custom business rules)?*
4. *Are there any data quality exceptions, quarantined records, or schema drifts affecting C-suite dashboards?*
5. *How efficiently is BigQuery partition pruning and clustering operating under production Power BI query workloads?*

---

## 2. Canvas Layout & Visual Hierarchy (16:9 1920x1080 Grid)

```
+-------------------------------------------------------------------------------------------------------------+
| TOP HEADER & NAV BAR: Title | Governance Badge | Freshness: Last Sync Today 02:30 UTC (2.5h ago) • Active   |
+-------------------------------------------------------------------------------------------------------------+
| ROW 1: 5 GOVERNANCE HEADLINE METRIC CARDS                                                                   |
| [Total Warehouse Volume]  [Data Freshness SLA]    [dbt Test Pass Rate]    [Data Quality Index]    [Partition Scan Red.]
| 9,551,197 Rows            2.5 Hours               100.0% Passed           99.98%                  95.8% Reduction
| (18 Tables • 205MB Parquet) (Target <6.0h • Met)   (131/131 Tests • 0 Fail)(0 Orphan Keys / Drift) (13.7MB vs 326.8MB)
+------------------------------------------------------+------------------------------------------------------+
| ROW 2 (LEFT, 7 cols): WAREHOUSE TABLES & PARTITIONS  | ROW 2 (RIGHT, 5 cols): DBT TEST SUITE INTEGRITY      |
| - FactInventorySnapshot: 5.46M rows (SnapshotDate)   | - Primary Key Uniqueness: 36 / 36 PASS               |
| - FactSales: 2.47M rows (OrderDate)                  | - Referential Integrity (FK): 28 / 28 PASS           |
| - FactPurchaseOrder: 1.11M rows (POCreationDate)     | - Mandatory Field Not Null: 45 / 45 PASS             |
| - FactDemandForecast: 179K rows (ForecastDate)       | - Accepted Categorical Values: 17 / 17 PASS          |
| - FactInventoryMovement: 175K rows (MovementDate)    | - Custom Business Rules SQL: 5 / 5 PASS              |
| - FactCustomerReturns: 103K rows (ReturnDate)        |   [Alert: Zero data quality quarantine exceptions]   |
| - DimProduct & SCD2 Snap: 11,000 rows                |                                                      |
+------------------------------------------------------+------------------------------------------------------+
| ROW 3: AUTOMATED ELT PIPELINE ORCHESTRATION RUN HISTORY (Cloud Composer / Airflow)                          |
| - RUN-20251231-0200 (02:00 UTC) -> 9.6 mins | 9,551,197 rows | SUCCESS (Extract -> ELT -> Test -> Refresh)  |
| - RUN-20251230-0200 (02:00 UTC) -> 9.3 mins | 9,541,200 rows | SUCCESS (Extract -> ELT -> Test -> Refresh)  |
| - RUN-20251229-0200 (02:00 UTC) -> 10.0 mins| 9,531,050 rows | SUCCESS (Extract -> ELT -> Test -> Refresh)  |
| - RUN-20251228-0200 (02:00 UTC) -> 9.0 mins | 9,520,880 rows | SUCCESS (Extract -> ELT -> Test -> Refresh)  |
| - RUN-20251227-0200 (02:00 UTC) -> 9.6 mins | 9,510,410 rows | SUCCESS (Extract -> ELT -> Test -> Refresh)  |
+-------------------------------------------------------------------------------------------------------------+
| FOOTER: BigQuery Standard SQL | dbt Core 1.8.0 | Incremental Refresh Active | Pages 1–9 Fully Certified      |
+-------------------------------------------------------------------------------------------------------------+
```

---

## 3. Visual Element Specifications & Measure Bindings

### 3.1 Headline Metric Cards (Row 1)

| Visual Card | Title | Primary Measure / Telemetry Binding | SLA Target / Baseline | Status Color |
| :--- | :--- | :--- | :--- | :--- |
| **Card 1** | **Total Warehouse Volume** | `[Total Warehouse Row Count]` (9,551,197) | 18 physical tables across Raw, Staging, Marts | Neutral |
| **Card 2** | **Data Freshness SLA** | `[Pipeline Freshness Latency Hours]` (2.5 h) | SLA Target: $< 6.0$ Hours | Emerald `#10b981` |
| **Card 3** | **dbt Test Pass Rate** | `[dbt Test Pass Rate Pct]` (100.0%) | 131 tests executed (0 failures, 0 warnings) | Emerald `#10b981` |
| **Card 4** | **Data Quality Index** | `[Data Quality Health Index Pct]` (99.98%) | 0 orphan foreign keys; zero schema drift | Sky `#0ea5e9` |
| **Card 5** | **Partition Scan Reduction** | `[BigQuery Scan Reduction Pct]` (95.8%) | 13.7 MB scanned vs 326.8 MB unpartitioned | Emerald `#10b981` |

---

### 3.2 Warehouse Tables Volume & Partitioning Matrix (Row 2, Left)
* **Visual Type:** Power BI Table Visual with layer badges and partitioning telemetry.
* **Fields:** `Table Layer`, `Table Name`, `Table Grain`, `Row Count`, `Partition Column`, `Clustering Keys`, `Sync Status`.

#### Table Footprint Breakdown:

| Table Name | Layer | Grain | Row Count | Partition Column | Clustering Keys | Status |
| :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| **FactInventorySnapshot** | Marts Fact | Daily SKU-Warehouse snapshot | **5,464,956** | `SnapshotDate` (Day) | `WarehouseKey`, `ProductKey` | Synced |
| **FactSales** | Marts Fact | Sales Order Line | **2,472,932** | `OrderDate` (Day) | `ProductKey`, `WarehouseKey` | Synced |
| **FactPurchaseOrder** | Marts Fact | PO Line Item | **1,110,903** | `POCreationDate` (Day) | `SupplierKey`, `ReceivingWarehouseKey` | Synced |
| **FactDemandForecast** | Marts Fact | Monthly SKU-Warehouse forecast | **179,424** | `ForecastDate` (Month) | `ProductKey`, `WarehouseKey` | Synced |
| **FactInventoryMovement** | Marts Fact | Inventory Transaction Line | **175,440** | `MovementDate` (Day) | `WarehouseKey`, `ProductKey` | Synced |
| **FactCustomerReturns** | Marts Fact | Return Line Item | **103,324** | `ReturnDate` (Day) | `ProductKey`, `CustomerChannelKey` | Synced |
| **BridgeProductSupplier** | Bridge | Multi-source Supplier Matrix | **13,333** | None (Import Mode) | `ProductKey`, `SupplierKey` | Synced |
| **FactSupplierMonthlyPerf**| Marts Fact | Monthly Supplier Scorecard | **11,852** | `MonthStartDate` (Month)| `SupplierKey` | Synced |
| **DimProduct & SCD2 Snap** | Dimension | Product Master & Historical SCD2 | **11,000** | None (Import Mode) | `CategoryName`, `ProductSKU` | Synced |
| **DimCustomerChannel** | Dimension | Customer Account Master | **5,000** | None (Import Mode) | `ChannelTier`, `ChannelName` | Synced |
| **DimDate** | Dimension | Calendar Day Master (4 Years) | **1,461** | None (Import Mode) | `Year`, `Quarter`, `Month` | Synced |
| **FactStockout** | Marts Fact | Stockout Outage Incident | **913** | `StartDate` (Day) | `ProductKey`, `WarehouseKey` | Synced |
| **DimSupplier** | Dimension | Supplier Master & Sourcing Profile| **500** | None (Import Mode) | `SupplierTier`, `SupplierCode` | Synced |
| **DimWarehouse** | Dimension | Fulfillment Facility Master | **100** | None (Import Mode) | `RegionKey`, `WarehouseCode` | Synced |
| **DimEmployeePlanner** | Dimension | Inventory & Demand Planners | **40** | None (Import Mode) | `Department`, `PlannerCode` | Synced |
| **SecurityUser** | Security | RLS Role Mapping Table | **8** | None (Import Mode) | `UserEmail`, `RoleName` | Synced |
| **DimRegion** | Dimension | Geographic Sales Theaters | **6** | None (Import Mode) | `Theater`, `RegionCode` | Synced |
| **DimScenario** | Dimension | Simulation Parameter Table | **5** | None (Import Mode) | `ScenarioID` | Synced |

---

### 3.3 dbt Test Suite & Integrity Breakdown (Row 2, Right)
* **Visual Type:** Test Group Cards with pass/fail telemetry.
* **Test Suites Executed:**
  1. **Primary Key Uniqueness (36 Tests — 100% Pass)**:
     - Guarantees strict entity uniqueness on surrogate keys across all dimensions, bridge tables, and fact lines.
  2. **Referential Integrity (28 Tests — 100% Pass)**:
     - Enforces zero orphan foreign keys (`relationships` tests linking `ProductKey`, `WarehouseKey`, `SupplierKey`, `CustomerChannelKey`, and `DateKey` back to Kimball dimensions).
  3. **Mandatory Field Completeness (45 Tests — 100% Pass)**:
     - Asserts `not_null` constraints on critical business fields (Quantities, Unit Costs, Prices, Order Dates, Status Flags).
  4. **Categorical Domain Integrity (17 Tests — 100% Pass)**:
     - Asserts `accepted_values` for ABC tiers (`A`, `B`, `C`), XYZ tiers (`X`, `Y`, `Z`), Supplier Tiers (`Tier 1 Strategic`, `Tier 2 Preferred`, `Tier 3 Tactical`), and PO Statuses.
  5. **Custom Business Rule Singular SQL Tests (5 Tests — 100% Pass)**:
     - `assert_inventory_non_negative.sql`: Validates on-hand stock is never negative.
     - `assert_sales_quantities_balance.sql`: Confirms $Q_{\text{ordered}} = Q_{\text{shipped}} + Q_{\text{cancelled}}$.
     - `assert_chronological_dates.sql`: Enforces $T_{\text{order}} \le T_{\text{ship}} \le T_{\text{delivery}}$.
     - `assert_positive_value.sql`: Checks positive standard landed cost and unit prices.
     - `assert_stockout_durations_valid.sql`: Asserts stockout duration $\ge 1$ day.

---

### 3.4 Automated ELT Pipeline Orchestration Run History (Row 3, Bottom)
* **Visual Type:** Power BI Table Visual with run execution telemetry.
* **Orchestration Tool:** Google Cloud Composer (Apache Airflow 2.7.3).
* **Schedule:** Daily at `02:00 UTC` (`0 2 * * *`).
* **Pipeline Execution Stages:**
  1. **Stage 1 (Extract & Ingest)**: Cloud Storage Parquet raw ingestion into BigQuery external staging tables (~1.8 minutes).
  2. **Stage 2 (dbt Transformations)**: Executes 36 models (`staging` $\rightarrow$ `intermediate` $\rightarrow$ `marts`) in BigQuery (~4.2 minutes).
  3. **Stage 3 (dbt Test Suite)**: Automated execution of 131 integrity tests (~1.1 minutes).
  4. **Stage 4 (Semantic Refresh)**: Power BI incremental refresh via REST API using partition pruning (~2.5 minutes).
  - **Total Pipeline Execution Duration**: **9.6 minutes** (Well within the 6.0-hour business SLA).

---

## 4. Navigation & Cross-Filtering Interactions

1. **Layer Slicing:** Selecting any layer (`Marts`, `Staging`, `Dimension`) filters the table volume matrix to inspect specific data tiers.
2. **Global Navigation:** Tabs 1 through 9 provide instant, bidirectional navigation across all 9 report pages.
3. **Cross-Certification:** Confirms the complete end-to-end analytical stack from BigQuery to dbt to Power BI is certified and production-ready.
