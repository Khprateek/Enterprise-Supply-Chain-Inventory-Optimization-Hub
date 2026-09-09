# Architecture Overview: Enterprise Supply Chain & Inventory Optimization Hub

## 1. Architectural Principles & Vision
The Enterprise Supply Chain & Inventory Optimization Hub is designed following industry-standard enterprise data warehousing principles:
- **Kimball Dimensional Modeling:** Star schemas with conformed dimensions to support cross-process drill-through and consistent analytical slicing.
- **Layered Data Architecture:** Strict separation of concerns between raw ingestion, clean staging, transformed dimensional modeling, and presentation layers.
- **Scalability & Cost-Efficiency:** Designed to handle 5M–10M+ fact records efficiently using BigQuery date partitioning, integer clustering, and lean columnar selection.
- **Reproducibility & Version Control:** All transformations, schema definitions, and analytical queries are managed in Git.
- **Local-First Development:** Early engineering, schema prototyping, and test dataset generation are kept local before executing cloud infrastructure deployments.

---

## 2. Layered Architecture Flow

`
+-------------------------------------------------------------------+
|                        1. SOURCE SYSTEMS                          |
|  (ERP Orders, WMS Inventory Snapshots, Inbound POs, Forecasts)    |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                   2. RAW / LANDING (Local / Cloud)                |
|  Immutable ingested data files (Parquet / CSV), source schema     |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                            3. STAGING                             |
|  Normalized types, validated keys, deduplicated, cleaned data     |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|             4. TRANSFORMED / CONFORMED (dbt / SQL)                |
|  Surrogate key generation, business logic, dimensional attributes |
|  Analytical Marts: FactSupplierMonthlyPerformance (dbt-built)     |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|             5. ANALYTICAL WAREHOUSE (Google BigQuery)             |
|  Star Schema: Conformed Dimensions & Partitioned Fact Tables      |
|  (Partitioned by DateKey/SnapshotDate, Clustered by Foreign Keys)  |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|            6. POWER BI SEMANTIC MODEL (Power BI Desktop)          |
|  Phase 1: Pure Import Mode (VertiPaq In-Memory Columnar Storage)  |
|  One-to-many single-direction relationships, explicit DAX logic   |
|  [Future Scalability Option: Composite Model / DirectQuery]       |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|               7. EXECUTIVE & PLANNER REPORTING                    |
|  Executive KPIs, Operational Worklists, Safety Stock Optimizers   |
+-------------------------------------------------------------------+
`

---

## 3. Technology Components & Storage Strategy

### 3.1 Analytical Warehouse (Google BigQuery)
- **Role:** Central cloud analytical warehouse.
- **Rationale:** Serverless, highly scalable execution for multi-million-row analytical queries, native time-based partitioning, and seamless connectivity with Power BI.
- **Partitioning & Clustering Strategy (per ADR-002):**
  - FactInventorySnapshot: Daily partition on SnapshotDate; clustered on ProductKey and WarehouseKey.
  - FactSales: Partitioned by OrderDate; clustered on ProductKey and CustomerChannelKey.
  - FactPurchaseOrder: Partitioned by POCreationDate; clustered on SupplierKey and ProductKey.
- **Alternative:** Snowflake (identified as viable alternative if BigQuery is unavailable).

### 3.2 Transformation & Data Modeling (dbt & SQL)
- **Role:** Modular SQL transformation and dimensional data modeling.
- **Tools:** dbt-core and dbt-bigquery adapter.
- **Capabilities:** Automated schema generation, dependency graph (DAG) resolution, incremental table loading, and integrated data quality testing.
- **Materialized Analytical Marts:** dbt materializes FactSupplierMonthlyPerformance to accelerate multi-year vendor scorecards without re-computing non-linear statistical measures (e.g., standard deviation) across millions of PO lines dynamically.

### 3.3 Semantic Modeling & Business Intelligence (Power BI Desktop)
- **Role:** Enterprise reporting, self-service analytics, and visual decision support.
- **Storage Mode Strategy (per ADR-002):**
  - **Phase 1 Primary Mode:** **Pure Import Mode**. VertiPaq in-memory columnar compression is the primary storage engine for the 5M–10M+ row star schema.
  - **Model Design:** Pure Star Schema; snowflake schemas and bi-directional cross-filtering are avoided. Technical keys are hidden, and integer surrogate keys are used exclusively.
  - **Future Scalability Option:** A Composite Model (Import Mode for high-level aggregates + DirectQuery for deep granular historical detail) is documented as an architectural roadmap option should data volumes exceed single-model capacity limits, but is not claimed as implemented in Phase 1.

### 3.4 Data Generation & Pipeline Utilities (Python 3.12)
- **Role:** Deterministic generation of enterprise-scale synthetic data, local file management, and orchestration support.
- **Stateful Continuity Rule (per ADR-002):** The inventory generator implements an authentic balance equation:
  \\text{Current On-Hand} = \\text{Previous On-Hand} + \\text{Receipts} + \\text{Adjustments} - \\text{Sales} - \\text{Outward Transfers/Returns}

---

## 4. Dimensional Model Blueprint (Kimball Approach)

### Conformed Dimensions
- DimDate: Standard calendar attributes, fiscal periods, working days, and seasonal indicators.
- DimProduct: SKU, product name, brand, category, subcategory, unit cost, unit price, handling type.
- DimSupplier: Supplier name, country, lead-time tier, contract SLA terms, contact details.
- DimWarehouse: Warehouse/DC code, facility name, region, storage capacity, operating type.
- DimRegion: Geographic hierarchy, country, market territory, currency.
- DimCustomerChannel: Sales channel (Wholesale, Retail, E-Commerce), customer segments.
- DimEmployeePlanner: Supply chain planner, operational role, department.
- DimScenario: Baseline vs. simulated parameter sets for what-if sensitivity analysis.

### Approved Core Fact Tables & Marts (per ADR-002)
1. **FactSales (Transactional Fact):** One row per fulfilled sales order line item.
2. **FactInventorySnapshot (Periodic Daily Snapshot Fact):**
   - **Grain:** One row per SKU \times Warehouse \times Snapshot Date (Option A - full daily snapshot).
   - **Scale:** Millions of rows; partitioned by SnapshotDate, clustered on ProductKey and WarehouseKey.
3. **FactPurchaseOrder (Accumulating / Transactional Fact):** One row per purchase order line item tracking order, promised delivery, actual receipt, and quantities.
4. **FactSupplierMonthlyPerformance (Materialized Analytical Mart):**
   - **Grain:** One row per Supplier \times Month.
   - **Source:** Derived directly from FactPurchaseOrder via dbt transformations.
5. **FactDemandForecast (Periodic Planning Fact):** One row per SKU \times Warehouse/Region \times Forecast Date \times Target Period.
6. **FactInventoryMovement (Transactional Event Fact):** One row per physical transfer, adjustment, cycle count correction, or scrap event.
7. **FactStockout (Derived Outage Event Fact):**
   - **Grain:** One row per consolidated outage event per SKU \times Warehouse.
   - **Derivation Rule:** Derived from FactInventorySnapshot when AvailableQuantity <= 0. Consolidates consecutive stockout days into a single event with duration, estimated lost demand, and estimated lost revenue.
8. **FactCustomerReturns (Transactional Fact):** One row per returned sales order line item with disposition status.

---

## 5. Security & Governance Principles
- No secrets or credentials (API keys, service account JSON files, .env files) committed to version control.
- Clear folder structure separating raw untracked data (data/raw/, data/staging/) from code and documentation.
- Architecture decisions tracked transparently in docs/decisions/ ([ADR-001](file:///d:/JOB/1.Buid_Skill/Work/Enterprise%20Supply%20Chain%20&%20Inventory%20Optimization%20Hub/docs/decisions/ADR-001-technology-stack.md), [ADR-002](file:///d:/JOB/1.Buid_Skill/Work/Enterprise%20Supply%20Chain%20&%20Inventory%20Optimization%20Hub/docs/decisions/ADR-002-data-volume-and-storage-strategy.md)).\n