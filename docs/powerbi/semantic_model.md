# Power BI Semantic Model Specification: Enterprise Supply Chain & Inventory Optimization Hub

## 1. Storage Architecture & Large-Table Strategy

### 1.1 Architecture Selection: Import Mode (VertiPaq)
In accordance with ADR-006, the semantic model employs **Power BI Import Mode** as its primary storage engine.

* **Rationale & Technical Evidence:**
  - The total enterprise dataset comprises **9,551,189 rows** (5.46M inventory snapshots, 2.47M sales lines, 1.11M purchase order lines) occupying **~205 MB** in compressed Parquet.
  - Power BI's columnar in-memory VertiPaq engine utilizes bit-packing, dictionary encoding, and run-length encoding (RLE). In VertiPaq, an integer-keyed star schema of this volume compresses down to **~120 MB ? 180 MB** in RAM, easily operating within standard Power BI Desktop and Power BI Pro (1 GB model ceiling).
  - **DirectQuery Evaluation:** DirectQuery sends live SQL to BigQuery on every slicer change, visual cross-filter, and card calculation. With 20+ visuals across an executive dashboard, DirectQuery would generate dozens of concurrent queries per user interaction, introducing 3?10s query latency and continuous BigQuery on-demand scanning costs ($6.25/TB).
  - **Conclusion:** Import Mode delivers sub-second visual responsiveness, enables complex DAX (iterators, statistical variance, King's safety stock model, semi-additive time logic), and incurs zero operational query costs during user consumption.

### 1.2 Large-Table & Refresh Strategy

| Table Name | Record Count | Storage Mode | Refresh Strategy | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `FactInventorySnapshot` | 5,464,956 | **Import** | Daily Incremental (Lookback: 3 days) | High-volume daily snapshot. Daily incremental refresh updates only latest partitions while preserving history. |
| `FactSales` | 2,472,932 | **Import** | Daily Incremental (Lookback: 3 days) | Transactional order lines. Incremental refresh captures recent order status modifications. |
| `FactPurchaseOrder` | 1,110,903 | **Import** | Daily Incremental (Lookback: 7 days) | Replenishment lines. 7-day lookback safely accounts for delayed receiving dock scans. |
| `FactDemandForecast` | 179,424 | **Import** | Full Refresh (Monthly batch) | Low row count; full refresh takes < 3 seconds. |
| `FactInventoryMovement` | 175,440 | **Import** | Full Refresh (Daily batch) | Low row count; full refresh takes < 3 seconds. |
| `FactCustomerReturns` | 103,324 | **Import** | Full Refresh (Daily batch) | Low row count; full refresh takes < 2 seconds. |
| `FactStockout` | 913 | **Import** | Full Refresh (Daily batch) | Consolidated outage episodes; sub-second refresh. |
| `FactSupplierMonthlyPerformance` | 11,852 | **Import** | Full Refresh (Monthly batch) | Pre-aggregated mart; sub-second refresh. |
| Conformed Dimensions (8 tables) | ~16,651 | **Import** | Full Refresh (Daily batch) | Dimensions are small (< 1 MB total); full refresh ensures complete SCD2 and hierarchy integrity. |

---

## 2. Relational Architecture & Role-Playing Dates

### 2.1 Pure Star Schema Topology
The model strictly adheres to 1-to-many, single-direction relationships from conformed dimensions to fact tables.
- **Bi-Directional Filtering:** Strictly forbidden across all fact relationships to prevent circular ambiguity, unexpected filter propagation, and slow DAX query plans.
- **Bridge Isolation:** `BridgeProductSupplier` joins 1-to-many to `DimSupplier` on `SupplierKey`, isolated from transactional fact relationships to prevent fan traps.

### 2.2 Role-Playing Date Disambiguation
Each fact table contains multiple operational milestone dates. To maintain a single conformed `DimDate` table without relationship loops, exactly **one relationship is Active**; secondary dates are **Inactive** and activated on-demand using DAX `USERELATIONSHIP()`:

| Fact Table | Active Date Relationship | Inactive Date Relationships (DAX Activated) |
| :--- | :--- | :--- |
| **`FactSales`** | `OrderDateKey` -> `DimDate[DateKey]` | `ShipDateKey`, `DeliveryDateKey` |
| **`FactInventorySnapshot`** | `SnapshotDateKey` -> `DimDate[DateKey]` | None |
| **`FactPurchaseOrder`** | `POCreationDateKey` -> `DimDate[DateKey]` | `PromisedDeliveryDateKey`, `ActualDockReceiptDateKey` |
| **`FactDemandForecast`** | `TargetPeriodDateKey` -> `DimDate[DateKey]` | `ForecastGeneratedDateKey` |
| **`FactInventoryMovement`** | `MovementDateKey` -> `DimDate[DateKey]` | None |
| **`FactStockout`** | `StartDateKey` -> `DimDate[DateKey]` | `EndDateKey` |
| **`FactCustomerReturns`** | `ReturnDateKey` -> `DimDate[DateKey]` | `OriginalOrderDateKey` |
| **`FactSupplierMonthlyPerformance`** | `YearMonthDateKey` -> `DimDate[DateKey]` | None |

---

## 3. Date Table Architecture (`DimDate`)

The date table is designated and marked as the official **Date Table** in Power BI (`dataCategory: "Time"` on `DimDate[FullDate]`), ensuring native DAX time-intelligence functions (`DATESYTD`, `DATEADD`, `SAMEPERIODLASTYEAR`) calculate correctly.

### 3.1 Period Sorting & Hierarchies
* `MonthName` is sorted by `MonthNumber`.
* `QuarterName` is sorted by `QuarterNumber`.
* `DayName` is sorted by `DayOfWeek`.
* `MonthYear` is sorted by `DateKey`.
* **Calendar Hierarchy:** `YearNumber` -> `QuarterName` -> `MonthName` -> `FullDate`
* **Fiscal Hierarchy:** `FiscalYear` -> `FiscalQuarter` -> `FullDate`

---

## 4. Structured Measure Library

All business calculations are implemented as explicit DAX measures organized into 8 display folders:

```
Measures/
??? Inventory/
?   ??? [Current On Hand Quantity]
?   ??? [Current Available Quantity]
?   ??? [Current Reserved Quantity]
?   ??? [Current Inbound Pipeline Quantity]
?   ??? [Current Inventory Valuation]
?   ??? [Average Daily Inventory Units]
?   ??? [Average Daily Inventory Valuation]
?   ??? [Dead Stock Valuation]
?   ??? [Dead Stock Valuation Pct]
?   ??? [Days of Inventory Outstanding (DIO)]
?   ??? [Inventory Turnover Ratio]
??? Sales/
?   ??? [Total Ordered Quantity]
?   ??? [Total Shipped Quantity]
?   ??? [Total Cancelled Quantity]
?   ??? [Total Gross Sales Revenue]
?   ??? [Total Discount Amount]
?   ??? [Total Net Sales Revenue]
?   ??? [Total Cost of Goods Sold]
?   ??? [Gross Profit Amount]
?   ??? [Gross Profit Margin Pct]
?   ??? [Average Discount Pct]
?   ??? [Total Sales Order Count]
?   ??? [Total Sales Line Count]
?   ??? [Average Order Cycle Time Days]
??? Service/
?   ??? [Sales OTIF Line Count]
?   ??? [Customer OTIF Rate Pct]
?   ??? [Unit Fill Rate Pct]
?   ??? [Stockout Incident Count]
?   ??? [Total Stockout Days]
?   ??? [Estimated Lost Demand Units]
?   ??? [Estimated Lost Sales Revenue]
?   ??? [Daily Stockout Rate Pct]
??? Forecast/
?   ??? [Total Forecasted Quantity]
?   ??? [Baseline Statistical Quantity]
?   ??? [Planner Adjustment Quantity]
?   ??? [Total Forecast Value]
?   ??? [Absolute Forecast Error Units]
?   ??? [Forecast WAPE Pct]
?   ??? [Forecast Accuracy Pct]
?   ??? [Forecast Bias Pct]
??? Procurement/
?   ??? [Total Procurement Spend]
?   ??? [Total PO Ordered Quantity]
?   ??? [Total PO Received Quantity]
?   ??? [Total PO Rejected Quantity]
?   ??? [Total Purchase Order Count]
?   ??? [Total PO Line Count]
?   ??? [Completed PO Line Count]
?   ??? [Open In-Transit PO Line Count]
?   ??? [Overdue PO Line Count]
?   ??? [Average Contract Lead Time Days]
?   ??? [Average Actual Lead Time Days]
?   ??? [Average Lead Time Variance Days]
?   ??? [PO Delivered On-Time Count]
?   ??? [PO Delivered In-Full Count]
?   ??? [PO OTIF Line Count]
?   ??? [Procurement OTIF Rate Pct]
?   ??? [Procurement On-Time Rate Pct]
?   ??? [Procurement In-Full Rate Pct]
?   ??? [Inbound Defect Rate Pct]
??? Supplier/
?   ??? [Active Supplier Count]
?   ??? [Supplier Monthly OTIF Avg Pct]
?   ??? [Scorecard Average Lead Time Days]
?   ??? [Critical SLA Breach Count]
?   ??? [Critical SLA Breach Pct]
??? Working Capital/
?   ??? [Annual Carrying Cost Rate]
?   ??? [Annual Inventory Carrying Cost]
?   ??? [Total Working Capital In Inventory]
?   ??? [Potential Working Capital Release]
??? Simulation/
    ??? [Scenario Demand Multiplier]
    ??? [Scenario Lead Time Shock Days]
    ??? [Simulated Demand Quantity]
    ??? [Simulated Dynamic Safety Stock Units]
    ??? [Simulated Reorder Point Units]
```

---

## 5. Model Hygiene & Governance Rules

1. **Hidden Technical Columns:** All surrogate keys (`*Key`), foreign keys, natural keys not required for display, and technical dates are set to `isHidden = true`.
2. **Explicit Measures Only:** Report authors must use explicit DAX measures; implicit aggregations (`Don't Summarize`) are disabled on all numeric fact columns.
3. **Format Strings:** All currency measures formatted as `$#,##0.00`, percentages as `0.00%`, and counts as `#,##0`.
4. **No Many-to-Many Relationships:** Every relationship in the core star schema is strictly 1-to-many.
