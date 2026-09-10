# ADR-005: Selection of dbt as Primary Data Transformation Engine

## Status
Approved

## Date
2026-09-10

## Context
The platform requires a reliable, testable, and version-controlled transformation framework to convert raw landing data into cleansed staging models, conformed Kimball dimensions, transactional/snapshot fact tables, and materialized analytical marts.

Traditional transformation mechanisms (such as SQL stored procedures, ad-hoc Python scripts, or drag-and-drop GUI ETL tools) often suffer from lack of testing, opaque dependencies, poor version control, and brittle maintenance.

## Decision
We select **dbt (dbt-core with dbt-bigquery adapter)** as the primary data transformation and modeling engine.

Key responsibilities assigned to dbt:
1. **Dependency Resolution:**
   - Automatically builds and executes the model Directed Acyclic Graph (DAG) using `ref()` macros.
2. **Environment Portability:**
   - Targets `dev`, `test`, and `prod` datasets seamlessly via `profiles.yml` without modifying SQL code.
3. **Automated Testing as Code:**
   - Executes primary key uniqueness (`unique`), mandatory field null checks (`not_null`), referential integrity (`relationships`), and value range constraints (`accepted_values`) before committing models to downstream warehouse layers.
4. **Surrogate Key Generation & Deduplication:**
   - Manages surrogate key hashing and window-function deduplication in standard, readable SQL.
5. **Materialization Control:**
   - Manages table materialization strategies (`view`, `table`, `incremental`) transparently across development and production environments.

## Alternatives Considered
- **SQL Stored Procedures in BigQuery:** Supported natively, but lack built-in automated testing frameworks, have poor Git version-control integration, and require custom dependency sequencing logic.
- **Custom Python / Pandas ETL Scripts:** Powerful for raw file ingestion and synthetic data generation, but using Python for large-scale warehouse SQL transforms loses database-native pushdown execution, requires transferring multi-million-row datasets over the network, and increases code maintenance overhead.
- **Apache Spark / PySpark:** High compute and operational overhead; excessive for 5M?10M row analytical warehousing when BigQuery's native SQL engine processes queries in seconds.

## Consequences

### Positive
- Declarative SQL with automated lineage visualization and documentation generation.
- Automated data quality assertions catch corrupted or duplicate records before they reach Power BI.
- Modular staging, intermediate, and dimensional layer separation enforces clean code architecture.

### Considerations & Risks
- Requires developers to adhere to dbt directory conventions (`models/staging/`, `models/marts/`).
- Incremental model logic must be carefully defined with proper unique keys to avoid duplicate records during delta runs.

## Future Scalability Implications
dbt models are database-agnostic at the conceptual layer; if the enterprise warehouse transitions to Snowflake or another platform in the future, transformation logic remains largely reusable with minimal adapter adjustments.
