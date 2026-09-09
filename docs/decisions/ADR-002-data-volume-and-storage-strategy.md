# ADR-002: Data Volume, Table Granularity & Power BI Storage Strategy

## Status
Approved

## Date
2026-09-10

## Context
The Enterprise Supply Chain & Inventory Optimization Hub is designed to process multi-million-row fact tables (5M–10M+ rows across core processes) to deliver accurate visibility into inventory valuation, working-capital exposure, supplier performance, and customer service levels.

During the requirements translation phase, four critical architectural decisions emerged that directly govern table granularity, physical materialization, event derivation, and BI storage modes:
1. **Inventory Snapshot Granularity:** Determining whether daily snapshots should be captured across all active SKU-Warehouse combinations or filtered to active movers.
2. **Supplier Scorecard Materialization:** Deciding whether monthly supplier performance metrics (OTIF, lead-time standard deviation) should be materialized in the data warehouse or computed dynamically over transactional purchase order lines.
3. **Stockout Representation:** Determining whether stockout incidents should be modeled as independent transactional inputs or derived systematically from daily inventory state transitions.
4. **Power BI Semantic Model Storage Mode:** Selecting between pure Import Mode, DirectQuery, or Composite Models for serving 5M–10M+ rows in Power BI Desktop.

---

## Decisions

### 1. Decision: Full Daily Snapshot for Active SKU-Warehouse Combinations (Option A)
- **Approved Grain:** **One row per SKU \times Warehouse \times Snapshot Date.**
- **Rationale:** Inventory is fundamentally a semi-additive measure across calendar time. Aggregating across time requires true snapshot states. Accurate calculation of Average Inventory, Days of Inventory (DOI), Inventory Turns, Stockout Frequency, and Working-Capital Exposure requires complete daily time-series continuity without temporal gaps.
- **Physical Design in BigQuery:**
  - **Partitioning:** Daily partition on SnapshotDate.
  - **Clustering:** Clustered on ProductKey and WarehouseKey.
  - **Key Strategy:** Integer surrogate keys (DateKey, ProductKey, WarehouseKey).
- **Data Generation & Continuity Rule:** Daily inventory must exhibit authentic operational continuity across dates:
  \\text{Current On-Hand} = \\text{Previous On-Hand} + \\text{Receipts} + \\text{Adjustments} - \\text{Sales} - \\text{Outward Transfers/Returns}
- **Scale Strategy:** While the target production volume spans millions of snapshot rows, early development may utilize a representative subset while strictly preserving the exact production schema and grain.

### 2. Decision: Materialized Monthly Supplier Performance Aggregate Table
- **Approved Structure:** Materialized aggregate table (FactSupplierMonthlyPerformance) maintained in dbt and BigQuery.
- **Approved Grain:** **One row per Supplier \times Month.**
- **Source of Truth:** Raw transactional fact FactPurchaseOrder remains the immutable source of truth.
- **Metrics Included:** Total PO count, PO line count, ordered quantity, received quantity, on-time delivery count, OTIF line count, OTIF rate (%), mean dock receipt lead time, lead-time standard deviation (Sigma LT), late delivery count, line fill rate (%), and vendor risk indices.
- **Rationale:** Computing statistical lead-time standard deviation and OTIF across millions of historical PO lines on-the-fly inside visual DAX queries degrades interactive dashboard performance. Materializing a monthly aggregate mart dramatically speeds up multi-year supplier trend scorecards while preserving 100% mathematical reconciliation with the underlying transactional lines.

### 3. Decision: Dedicated FactStockout Event Table Derived from Inventory State
- **Approved Structure:** Dedicated outage event fact table (FactStockout) derived deterministically from FactInventorySnapshot.
- **Derivation Rule:** Triggered when AvailableQuantity <= 0 for an active commercial SKU.
- **Event Consolidation Rule:** The event-detection pipeline must consolidate consecutive days of zero stock into a single, continuous stockout event:
  - *Example:* If an SKU has zero available stock from October 3 through October 7 (5 consecutive snapshot days), this produces **one** record in FactStockout with StartDate = 2026-10-03, EndDate = 2026-10-07, and DurationDays = 5.
- **Attributes Captured:** StockoutEventKey, ProductKey, WarehouseKey, StartDateKey, EndDateKey, StockoutDurationDays, EstimatedLostDemandUnits, EstimatedLostRevenueAmount, and SeverityTier.
- **Rationale:** Treats inventory state as the empirical ground truth, prevents artificial duplicate event inflation, and provides direct metrics for outage duration and unfulfilled lost sales.

### 4. Decision: Phase 1 Power BI Import Mode as Primary Semantic Model
- **Approved Mode:** **Pure Import Mode** in Power BI Desktop for Phase 1.
- **Rationale:**
  - Modern Power BI VertiPaq columnar in-memory compression easily handles 5M–10M+ rows when properly architected with integer surrogate keys, lean column widths, hidden technical keys, and pure star-schema relationships.
  - Avoids DirectQuery performance penalties, DAX formula limitations, and continuous query load on the underlying cloud data warehouse during visual interactions.
- **Future Scalability Option (Documented Architecture Pathway):**
  - If fact volume expands beyond single-node memory limits, near-real-time intra-day requirements emerge, or Power BI Premium/Fabric capacity is introduced, a **Composite Model** (high-level aggregations in Import Mode + granular historical lines in DirectQuery) can be evaluated.
  - **Boundary:** DirectQuery and Composite models are documented strictly as future architectural scaling options and are NOT claimed as implemented in Phase 1.

---

## Alternatives Considered

| Decision Area | Alternative Considered | Why Rejected |
| :--- | :--- | :--- |
| **Inventory Snapshot** | Weekly snapshots or snapshotting only items with movement (Option B) | Distorts daily average inventory calculations, introduces sparse date matrices, complicates daily ROP triggers, and fails to capture short-duration stockouts. |
| **Supplier Scorecard** | Dynamic calculation via DAX measures exclusively over FactPurchaseOrder | Calculating standard deviation of lead time over hundreds of thousands of PO lines inside interactive Power BI visuals causes severe visual latency (>10s) and poor user experience. |
| **Stockout Representation** | Independent manual source or treating every single zero-stock day as an independent incident | Independent manual logs introduce severe reconciliation discrepancies with inventory data; treating every zero day as an event inflates stockout frequency by 500%–1000% and distorts true outage duration. |
| **Power BI Storage Mode** | Immediate Composite Model with DirectQuery | Introduces unnecessary architectural complexity, restricts DAX functionality, creates external query costs on BigQuery, and is unjustified given VertiPaq efficiency on 5M–10M rows. |

---

## Trade-offs & Consequences

### Positive
- **Analytical Rigor:** Full daily snapshot continuity guarantees 100% precision for semi-additive metrics, turnover ratios, and Days of Inventory (DOI).
- **Dashboard Responsiveness:** Pre-materialized monthly supplier aggregates and in-memory VertiPaq storage ensure sub-2-second interactive dashboard filtering.
- **Data Reconciliation:** Deriving FactStockout directly from FactInventorySnapshot eliminates discrepancies between reported stockouts and physical inventory balances.
- **Cost & Complexity Control:** Pure Import mode avoids premature cloud query execution costs during development and analysis.

### Considerations & Risks
- **Fact Table Volume:** Daily snapshots across thousands of SKUs and dozens of facilities will scale to 10M+ rows over multi-year horizons. This necessitates disciplined date partitioning and integer clustering in BigQuery.
- **Data Generation Logic:** The synthetic data generator must implement stateful inventory balance equations rather than independent random number generation to satisfy continuity requirements.

---

## Future Scalability Implications
- As data history extends beyond 3 years or row counts surpass 25M–50M rows, Power BI Incremental Refresh (partitioning historical data in VertiPaq) and BigQuery materialized aggregations can be seamlessly enabled without redesigning the Kimball dimensional model.\n