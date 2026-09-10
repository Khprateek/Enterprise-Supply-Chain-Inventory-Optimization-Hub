# ADR-006: Power BI Semantic Model Architecture & Storage Strategy

## Status
Approved

## Date
2026-09-10

## Context
The Enterprise Supply Chain & Inventory Optimization Hub requires an intuitive, high-performance reporting semantic model capable of serving 5 role-based dashboards to executive and operational personas across 5M?10M+ fact records.

A critical design choice is determining the storage mode (Import Mode vs. DirectQuery vs. Composite Models) and semantic modeling structure in Power BI Desktop to achieve sub-3-second visual interactions without excessive cloud warehouse query costs or DAX limitations.

## Decision
We select **Power BI Import Mode** as the primary storage and modeling strategy for Phase 1.

Key implementation principles:
1. **In-Memory Columnar Compression (VertiPaq):**
   - Import Mode loads the star schema into Power BI's VertiPaq engine, leveraging run-length encoding, dictionary encoding, and bit-packing compression.
   - For 5M?10M+ rows, an optimized star schema typically compresses down to under 500 MB in memory, easily fitting within standard Power BI Desktop and Pro capacities.
2. **Pure Star Schema Modeling:**
   - 1-to-many single-direction relationships from conformed dimensions to fact tables.
   - Bi-directional cross-filtering is strictly forbidden to prevent ambiguity, unpredictable filter propagation, and performance degradation.
3. **Explicit Measures & Technical Key Hiding:**
   - All surrogate keys, foreign keys, and technical timestamps are hidden from the report field list.
   - Business metrics are implemented exclusively via explicit DAX measures organized into dedicated measure folders (`_InventoryMeasures`, `_ProcurementMeasures`, etc.).
4. **Semi-Additive Handling in DAX:**
   - Inventory snapshots are evaluated using `CALCULATE(..., LASTDATE('DimDate'[Date]))` or `AVERAGEX()` over daily snapshots rather than unconstrained `SUM()`.

## Future Scalability Option: Composite Model Roadmap
- **Roadmap Path:** If data volumes expand beyond single-model memory limits (>25M?50M rows) or near-real-time intra-day tracking becomes an operational mandate, a **Composite Model** can be introduced:
  - Materialized summary tables (e.g., Monthly Supplier Performance, Monthly Category Inventory) in **Import Mode**.
  - Deep historical granular order-line transactions in **DirectQuery** to BigQuery with automatic aggregation redirection.
- **Architectural Boundary:** DirectQuery and Composite Models are documented strictly as future architectural options and are **not** claimed as implemented in Phase 1.

## Alternatives Considered
- **DirectQuery Mode for All Tables:** Queries BigQuery live on every visual interaction and slicer click. Rejected for Phase 1 because it creates significant visual latency (5?15+ seconds per visual), generates continuous query costs in BigQuery, and disables critical DAX time-intelligence and statistical distribution functions.
- **Single Flattened Wide Table (OBT):** Ingesting a single denormalized 50-column table into Power BI. Rejected because it destroys VertiPaq dictionary compression ratios, bloats model size by 500%?1000%, and breaks multi-fact cross-filtering.

## Consequences

### Positive
- Sub-2-second interactive filtering and drill-down across all 5 report pages.
- Full access to advanced DAX capabilities, including King's Dynamic Safety Stock formula, non-additive time logic, and what-if simulation parameters.
- Zero continuous query costs on BigQuery while users explore reports.

### Considerations & Risks
- Refresh duration: Model refresh requires importing data over the network from BigQuery. This will be optimized using column selection, integer keys, and partition pruning.

## Future Scalability Implications
Designing with pure star schemas and integer surrogate keys ensures that if a transition to Composite Models or Incremental Refresh is required later, the schema structure requires zero redesign.
