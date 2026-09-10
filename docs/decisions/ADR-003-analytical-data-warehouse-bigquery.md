# ADR-003: Selection of Google BigQuery as Cloud Analytical Data Warehouse

## Status
Approved

## Date
2026-09-10

## Context
The Enterprise Supply Chain & Inventory Optimization Hub requires a cloud analytical data warehouse capable of storing, partitioning, and querying multi-million-row fact tables (5M?10M+ rows across sales, daily inventory snapshots, and purchase orders) with sub-second analytical response times, zero operational compute maintenance, and seamless connectivity to Power BI Desktop and dbt.

## Decision
We select **Google BigQuery** as the cloud analytical data warehouse.

Key technical implementation choices in BigQuery:
1. **Partitioning:**
   - `FactInventorySnapshot` is partitioned by day on `SnapshotDate`.
   - `FactSales` is partitioned by day on `OrderDate`.
   - `FactPurchaseOrder` is partitioned by day on `POCreationDate`.
2. **Clustering:**
   - Up to four clustering columns are applied per fact table to minimize data scanned during multi-dimensional slicing (e.g., `ProductKey`, `WarehouseKey`, `SupplierKey`).
3. **Surrogate Keys:**
   - Integer surrogate keys (`INT64`) are used for dimension and fact foreign keys, avoiding high-byte-width string joins.
4. **Access Control:**
   - Granular IAM service account security isolating development, staging, and production datasets.

## Alternatives Considered
- **Snowflake:** Highly capable multi-cluster warehouse; however, BigQuery provides truly serverless pay-per-query/slot pricing with zero warehouse pause/resume administration. Furthermore, Google Cloud BigQuery client libraries and `dbt-bigquery` are already installed and verified in the development environment.
- **PostgreSQL / Self-Managed RDBMS:** Suitable for small relational workloads, but lacks native columnar compression, scales poorly on 10M+ fact joins without complex index tuning, and creates compute bottlenecks during Power BI model refreshes.
- **DuckDB:** Outstanding for embedded local analysis, but lacks managed multi-user cloud governance, IAM service account role-based access, and enterprise cloud BI sharing capabilities.

## Consequences

### Positive
- Serverless architecture eliminates compute infrastructure management, cluster sizing, and warehouse spin-up latency.
- Native day-based partitioning and clustering dramatically reduce query costs and accelerate Power BI import refresh operations.
- Native integration with `dbt-bigquery` adapter allows declarative version-controlled schema management.

### Considerations & Risks
- Cloud execution requires valid Google Cloud project credentials and service account configuration.
- To prevent accidental query costs during development, local prototyping and smaller sample datasets will be utilized before executing multi-million-row cloud pipeline runs.

## Future Scalability Implications
As fact table history grows beyond 3 years or 50M+ rows, BigQuery's partitioned architecture allows historical partitions to be archived or set to long-term storage pricing without breaking the dimensional query interface.
