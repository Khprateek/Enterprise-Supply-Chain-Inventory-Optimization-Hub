# Architecture Overview: Enterprise Supply Chain & Inventory Optimization Hub

## 1. Architectural Principles & Vision
The Enterprise Supply Chain & Inventory Optimization Hub is designed following industry-standard enterprise data warehousing principles:
- **Kimball Dimensional Modeling:** Star schemas with conformed dimensions to support cross-process drill-through and consistent analytical slicing.
- **Layered Data Architecture:** Strict separation of concerns between raw ingestion, clean staging, transformed dimensional modeling, and presentation layers.
- **Scalability & Cost-Efficiency:** Designed to handle 5M–10M+ fact records efficiently using partitioning and clustering strategies.
- **Reproducibility & Version Control:** All transformations, schema definitions, and analytical queries are managed in Git.
- **Local-First Development:** Early engineering, schema prototyping, and test dataset generation are kept local before executing cloud infrastructure deployments.

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
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|             5. ANALYTICAL WAREHOUSE (Google BigQuery)             |
|  Star Schema: Conformed Dimensions & Partitioned Fact Tables      |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|            6. POWER BI SEMANTIC MODEL (Power BI Desktop)          |
|  One-to-many single-direction relationships, explicit DAX logic    |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|               7. EXECUTIVE & PLANNER REPORTING                    |
|  Executive KPIs, Operational Worklists, Safety Stock Optimizers   |
+-------------------------------------------------------------------+
`

## 3. Technology Components

### 3.1 Analytical Warehouse (Google BigQuery)
- **Role:** Central cloud analytical warehouse.
- **Rationale:** Serverless, highly scalable execution for multi-million-row analytical queries, native time-based partitioning (e.g., date-partitioned snapshots and sales), and seamless connectivity with Power BI.
- **Alternative:** Snowflake (identified as viable alternative if BigQuery is unavailable).

### 3.2 Transformation & Data Modeling (dbt & SQL)
- **Role:** Modular SQL transformation and dimensional data modeling.
- **Tools:** dbt-core and dbt-bigquery adapter.
- **Capabilities:** Automated schema generation, dependency graph (DAG) resolution, incremental table loading, and integrated data quality testing.

### 3.3 Semantic Modeling & Business Intelligence (Power BI Desktop)
- **Role:** Enterprise reporting, self-service analytics, and visual decision support.
- **Model Design:** Pure Star Schema; snowflake schemas and bi-directional cross-filtering are avoided to maximize VertiPaq engine performance.
- **Measures:** Formatted DAX measures grouped into dedicated measure tables with clear naming conventions.

### 3.4 Data Generation & Pipeline Utilities (Python 3.12)
- **Role:** Deterministic generation of enterprise-scale synthetic data, local file management, and orchestration support.
- **Libraries:** Pandas, PyArrow, NumPy, Google Cloud BigQuery client library.

## 4. Dimensional Model Blueprint (Kimball Approach)
The analytical warehouse schema is organized around distinct business processes:

### Conformed Dimensions (Planned)
- DimDate: Standard calendar attributes, fiscal periods, working days, and seasonal indicators.
- DimProduct: SKU, product name, brand, category, subcategory, unit cost, unit price, handling type.
- DimSupplier: Supplier name, country, lead-time tier, contract SLA terms, contact details.
- DimWarehouse: Warehouse/DC code, facility name, region, storage capacity, operating type.
- DimRegion: Geographic hierarchy, country, market territory, currency.
- DimCustomerChannel: Sales channel (Wholesale, Retail, E-Commerce), customer segments.
- DimEmployeePlanner: Supply chain planner, operational role, department.
- DimScenario: Baseline vs. simulated parameter sets for what-if sensitivity analysis.

### Candidate Fact Tables (Planned)
- FactSales: Transactional grain representing fulfilled customer order lines.
- FactInventorySnapshot: Periodic snapshot grain capturing stock-on-hand, allocated stock, and available stock per SKU-warehouse-day.
- FactPurchaseOrder: Accumulating or transactional grain tracking PO creation, expected delivery, receipt date, and quantity received.
- FactForecast: Periodic forecast grain capturing planned demand targets for forecast accuracy evaluation.
- FactInventoryMovement: Detailed event grain recording stock transfers, adjustments, and receipts.
- FactStockout: Event grain capturing stockout occurrences, unfulfilled demand, and duration.
- FactReturns: Transactional grain recording customer returns, reason codes, and condition.

*Note: Individual fact and dimension schemas will be formally designed, reviewed, and finalized in Phase 2.*

## 5. Security & Governance Principles
- No secrets or credentials (API keys, service account JSON files, .env files) committed to version control.
- Clear folder structure separating raw untracked data (data/raw/, data/staging/) from code and documentation.
- Architecture decisions tracked transparently in docs/decisions/.
