# Logical Architecture: Enterprise Supply Chain & Inventory Optimization Hub

## 1. Architectural Principles & Vision
The Enterprise Supply Chain & Inventory Optimization Hub is designed following industry-standard Kimball enterprise data warehousing methodologies:
- **Kimball Dimensional Modeling:** Star schemas with conformed dimensions to support cross-process drill-through, consistent slicing, and fast analytical querying.
- **Layered Architecture:** Strict physical and logical separation of concerns between raw ingestion, staging validation, transformed dimensional models, and semantic reporting.
- **Scalability & Cost-Efficiency:** Engineered to support 5M–10M+ fact records using BigQuery date partitioning, integer clustering, and lean columnar data types.
- **Data Quality as Code:** Quality validation rules enforced via automated dbt schema tests, custom SQL integrity assertions, and ingestion quarantine boundaries.
- **Local-First Practical Development:** Development, prototyping, and initial data verification occur locally before deploying to cloud infrastructure.

---

## 2. Complete Architecture Layers & Responsibilities

The platform implements an 8-layer end-to-end data architecture:

`
[1. Source Systems]
        │
        ▼
[2. Landing / Raw Layer]
        │
        ▼
[3. Staging Layer]
        │
        ▼
[4. Transformation Layer (dbt)]
        │
        ▼
[5. Analytical Warehouse (BigQuery)]
        │
        ▼
[6. Semantic Model (VertiPaq / DAX)]
        │
        ▼
[7. Presentation / Power BI Reports]
        │
        ▼
[8. Business Personas / Users]
`

### Layer 1: Source Systems (Operational Systems & Simulation Engines)
- **Responsibility:** Represents operational enterprise systems generating supply chain data across disparate operational domains:
  - *Enterprise Resource Planning (ERP):* Sales orders, customer billing, purchase orders, vendor master records, and product master catalogs.
  - *Warehouse Management System (WMS):* Daily physical inventory balances, bin locations, put-away records, and cycle count discrepancies.
  - *Procurement & Logistics (TMS / Supplier Portals):* Inbound shipment manifests, dock receipt timestamps, carrier freight costs, and delivery tracking.
  - *Advanced Planning & Scheduling (APS):* Baseline statistical forecasts, consensus demand plans, and promotional calendars.
- **Form in Hub:** Vectorized Python 3.12 generation engine synthesizing realistic, correlated enterprise records adhering strictly to business rules and historical seasonality.

### Layer 2: Landing / Raw Layer (data/raw/ / GCS Bucket)
- **Responsibility:** Immutable landing zone for ingested files.
- **Rules:**
  - Files are written in format-preserving Parquet / CSV without schema modification.
  - Source data is append-only; historical raw payloads are never modified or overwritten.
  - Audit metadata is appended: _ingested_at (UTC timestamp), _source_system, and _batch_id.
- **Failure Handling:** If an inbound file is malformed or unreadable, it is logged and moved to a quarantine error bucket without interrupting existing pipelines.

### Layer 3: Staging Layer (data/staging/ / BigQuery stg_* Views/Tables)
- **Responsibility:** Cleanses, standardizes, and normalizes raw data into structured relational structures.
- **Tasks:**
  - Explicit data type casting (e.g., strings to dates, decimals to monetary amounts).
  - Business key validation and whitespace trimming.
  - Deduplication on source natural keys.
  - Handling nulls and replacing missing values with standardized business codes (e.g., -1 or 'UNKNOWN').
  - Applying initial row-level validation filters (e.g., dropping impossible negative order quantities).
- **Output:** Ephemeral or view-based staging tables (stg_sales_orders, stg_inventory_snapshots, stg_purchase_orders, etc.).

### Layer 4: Transformation Layer (dbt-core & Standard SQL)
- **Responsibility:** Implements core business logic, dimensional surrogate key generation, and dimensional modeling rules.
- **Tasks:**
  - Generation of integer surrogate keys using deterministic hashing or sequences.
  - Conformed dimension modeling (e.g., DimDate, DimProduct, DimSupplier, DimWarehouse).
  - Fact table transformation with referential integrity enforcement against conformed dimensions.
  - Derivation of FactStockout by consolidating consecutive days where AvailableQuantity <= 0.
  - Materialization of the analytical aggregate mart FactSupplierMonthlyPerformance to pre-calculate complex metrics (e.g., lead-time standard deviation).
  - Execution of automated data quality tests (unique, 
ot_null, 
elationships, ccepted_values).

### Layer 5: Analytical Warehouse (Google BigQuery)
- **Responsibility:** Central cloud storage and query engine hosting the conformed Kimball star schema.
- **Storage Strategy:**
  - Fact tables are partitioned by their primary transaction/snapshot date (e.g., SnapshotDate, OrderDate, POCreationDate).
  - Fact tables are clustered by primary dimension surrogate keys (e.g., ProductKey, WarehouseKey, SupplierKey).
  - Dimensions are materialized as clustered tables optimized for broadcast joins.
  - Enforces least-privilege access control via GCP IAM service accounts.

### Layer 6: Semantic Model (Microsoft Power BI Semantic Model)
- **Responsibility:** In-memory business semantic layer translating dimensional warehouse tables into enterprise metrics.
- **Architecture:**
  - Modeled strictly as a pure Star Schema with 1-to-many, single-direction relationships from dimensions to facts.
  - Technical surrogate keys and foreign keys are hidden from end-user reporting fields.
  - DAX measure tables housing explicitly formulated business metrics (Turnover, DOI, Service Level, King\'s Dynamic Safety Stock, WAPE).
  - VertiPaq columnar in-memory compression maximizing query throughput.

### Layer 7: Presentation & Reporting Layer (Power BI Desktop Reports)
- **Responsibility:** Delivers role-tailored visual decision support tools across 5 interactive report pages:
  1. *Executive Overview:* Macro KPIs, working-capital exposure, enterprise turns, service levels.
  2. *Inventory Health & Aging:* Aging brackets (0–30, 31–60, 61–90, 91–180, 180+), excess inventory, dead stock.
  3. *SKU Optimization:* ABC-XYZ segmentation matrix, dynamic safety stock, reorder point triggers.
  4. *Supply & Procurement:* Vendor scorecards, OTIF tracking, lead-time distribution, overdue PO alerts.
  5. *Demand Forecasting:* Forecast accuracy, WAPE, forecast bias, and lost sales analysis.
  - Interactive what-if parameter sliders (Z-score service level, lead-time shock, carrying cost rate).

### Layer 8: End Users & Personas
- **Responsibility:** Execution of operational, tactical, and strategic decisions based on governed analytics:
  - *VP of Operations:* Strategic capital allocation and service-level trade-offs.
  - *Regional Supply Planner:* Inventory rebalancing and forecast override reviews.
  - *Warehouse Planner:* Daily replenishment order generation and dead-stock disposition.
  - *Procurement Manager:* Supplier contract SLA enforcement and purchase order expediting.
  - *Supply Chain Analyst:* Replenishment algorithm parameter tuning and statistical validation.

---

## 3. Technology Evaluation: Confirm or Challenge

| Technology | Selected Role | Problem Solved | Alternatives Evaluated | Why Selected Over Alternatives |
| :--- | :--- | :--- | :--- | :--- |
| **Google BigQuery** | Cloud Analytical Warehouse | Need for scalable, serverless SQL engine capable of querying 5M–10M+ rows with sub-second partition pruning and zero infrastructure management. | Snowflake, PostgreSQL, DuckDB, AWS Redshift | **Confirmed.** Serverless auto-scaling requires zero compute cluster provisioning; native date partitioning and clustering directly match daily snapshot scale; client libraries (google-cloud-bigquery) and dbt-bigquery are already installed and verified in the environment. |
| **dbt (dbt-core)** | Transformation & Modeling | Complex multi-stage Kimball SQL transformations, surrogate key generation, dependency resolution (DAGs), and automated testing. | Stored Procedures, Custom Python scripts, Apache Airflow pure SQL | **Confirmed.** Declarative SQL modeling with built-in version-controlled documentation, lineage graph visualization, and native assertions (unique, 
ot_null, 
elationships) eliminates fragile bespoke orchestration scripts. |
| **Python 3.12** | Synthetic Data & Pipeline Engine | Need to generate high-fidelity, correlated multi-million-row supply chain datasets exhibiting authentic seasonality, Poisson demand, and stateful balance continuity. | Mockaroo, DB-native SQL random generation, Java/Scala | **Confirmed.** Vectorized execution via NumPy, Pandas, and PyArrow generates millions of rows in seconds. Enables stateful tracking of continuous inventory balance equations (I_t = I_{t-1} + R + A - S - M) that SQL random functions cannot simulate. |
| **Microsoft Power BI Desktop** | Semantic Modeling & BI | Enterprise semantic modeling, VertiPaq in-memory compression, non-additive time-series DAX measures, and interactive visual reporting. | Tableau, Apache Superset, Looker Studio, Metabase | **Confirmed.** Power BI\'s VertiPaq engine delivers superior in-memory performance on 10M-row star schemas; expressive DAX easily models complex dynamic formulas (King\'s safety stock, semi-additive inventory end-of-period balances); installed locally on Windows host. |
| **Git & GitHub** | Version Control & CI/CD Foundation | Code versioning, branch isolation, code review transparency, and reproducible analytics engineering. | Manual zip archives, Local file versioning, Bitbucket | **Confirmed.** Industry standard for analytics engineering. Enables atomic commits, transparent Architecture Decision Record (ADR) tracking, and clear separation between master and feature branches. |

---

## 4. Key Architectural Trade-Offs & Boundaries

1. **No Premature Cloud Cost:** Prototyping, staging schemas, and data validation pipelines remain local first. BigQuery provisioning and cloud loading occur only after local validation passes.
2. **No Monolithic Tables:** The presentation layer consumes a Kimball star schema. Single giant flat tables are explicitly prohibited to prevent memory bloating and broken aggregations.
3. **No Unaccounted Metrics:** Every visual card and chart traces directly back to the formal 20-metric KPI Catalog ([docs/business/kpi_catalog.md](../business/kpi_catalog.md)) and Business Questions ([docs/business/business_questions.md](../business/business_questions.md)).\n