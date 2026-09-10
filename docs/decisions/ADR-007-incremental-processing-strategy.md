# ADR-007: Incremental Data Processing & Partitioning Strategy

## Status
Approved

## Date
2026-09-10

## Context
At enterprise scale, the Supply Chain & Inventory Optimization Hub processes millions of fact rows (e.g., daily inventory snapshots across thousands of SKUs and dozens of facilities accumulate millions of rows annually). 

Executing full table re-computations and full data reloads on every batch run creates exponential increases in BigQuery compute costs, network bandwidth consumption, and pipeline execution time. An incremental processing strategy is essential for sustainable operations.

## Decision
We establish an **incremental processing and partitioning strategy** spanning both the transformation layer (dbt) and the analytical warehouse (BigQuery).

Key architectural specifications:
1. **BigQuery Table Partitioning:**
   - `FactInventorySnapshot` is partitioned by day on `SnapshotDate`.
   - `FactSales` is partitioned by day on `OrderDate`.
   - `FactPurchaseOrder` is partitioned by day on `POCreationDate`.
   - Partition expiration policies will preserve at least 3 years of active historical data.
2. **dbt Incremental Materialization Pattern:**
   - Core high-volume facts (`fact_inventory_snapshot`, `fact_sales`) utilize dbt's `incremental` materialization strategy:
     ```sql
     {{ config(
         materialized='incremental',
         unique_key=['ProductKey', 'WarehouseKey', 'SnapshotDate'],
         partition_by={'field': 'SnapshotDate', 'data_type': 'date'},
         cluster_by=['ProductKey', 'WarehouseKey']
     ) }}
     SELECT ...
     FROM {{ ref('stg_inventory_snapshots') }}
     {% if is_incremental() %}
       WHERE SnapshotDate >= (SELECT MAX(SnapshotDate) FROM {{ this }})
     {% endif %}
     ```
   - **Lookback Window:** Incremental runs incorporate a 3-day trailing lookback window (`CURRENT_DATE() - 3`) to capture late-arriving WMS cycle count adjustments and retroactively updated dock receipts without requiring a full rebuild.
3. **Dimension Refresh Strategy:**
   - Conformed dimensions (`DimProduct`, `DimSupplier`, `DimWarehouse`, `DimRegion`) remain `table` materializations due to relatively small row counts (thousands of rows), ensuring complete historical integrity and simplified SCD Type 2 handling.
4. **Power BI Incremental Refresh Readiness:**
   - Semantic model tables are designed with explicit `RangeStart` and `RangeEnd` parameter compatibility so that Power BI Incremental Refresh can be enabled on Premium/Fabric capacities in the future without modifying underlying table schemas.

## Alternatives Considered
- **Full Refresh on Every Run:** Dropping and rebuilding multi-million-row fact tables on every batch cycle. Rejected because it wastes significant cloud compute resources, increases query runtimes from seconds to dozens of minutes, and creates unnecessary pipeline fragility.
- **Append-Only Without Lookback:** Ingesting new rows without upserting late-arriving adjustments. Rejected because supply chain operations frequently experience late dock receipts, retroactive inventory reconciliation, and delayed returns processing, which would cause permanent record divergence.

## Consequences

### Positive
- Pipeline execution time scales with daily delta volume rather than cumulative historical volume.
- Minimizes BigQuery data scan costs by updating only target daily partitions.
- Accommodates realistic supply chain operational realities (late dock receipts and adjustments) via the 3-day trailing lookback window.

### Considerations & Risks
- Unique keys must be defined with 100% precision across composite business keys to prevent duplicate records during incremental merges.
- Full refreshes (`dbt run --full-refresh`) must be scheduled periodically (e.g., quarterly) to ensure complete alignment after major schema or business rule migrations.

## Future Scalability Implications
Partitioning and incremental delta merging allow the platform to scale smoothly to tens of millions of rows while keeping daily ETL runtimes under 5 minutes.
