# Analytics Acceptance Criteria: Enterprise Supply Chain & Inventory Optimization Hub

This document defines the formal functional and analytical acceptance criteria that the Enterprise Supply Chain & Inventory Optimization Hub must satisfy. It establishes unambiguous standards for question answerability, KPI computation precision, dimensional grain, data integrity, and analytical performance.

---

## 1. Business Persona Capability Acceptance Criteria

### AC-01: Executive Visibility (VP of Operations)
- **Criterion:** The system must provide a macro-level executive summary displaying total enterprise inventory valuation, annualized inventory turns, overall customer service level (OTIF), total working-capital exposure, and annual holding costs.
- **Verification:** Filtering by Region or Category dynamically updates executive KPI cards within <= 3 seconds, showing both current month-end position and trailing 12-month trendlines.

### AC-02: Regional Supply Balancing (Regional Supply Planner)
- **Criterion:** Regional planners must be able to view inventory balances across all distribution centers in their territory, identify facilities with stock surpluses vs. deficits, and evaluate inter-warehouse transfer feasibility.
- **Verification:** System must identify SKUs with excess stock in Node A that match stockout or below-ROP conditions in Node B within the same geographic region.

### AC-03: Operational Floor Replenishment (Warehouse / Inventory Planner)
- **Criterion:** Warehouse planners must receive an actionable daily worklist identifying every SKU currently below its Reorder Point (ROP) or with zero on-hand stock.
- **Verification:** For every flagged SKU, the worklist must display On-Hand, Reserved, Available, In-Transit PO Units, Current ROP, and Net Deficit Units.

### AC-04: Inbound Vendor Reliability (Procurement Manager)
- **Criterion:** Procurement managers must have access to automated supplier scorecards evaluating vendor On-Time In-Full (OTIF %), average dock receipt lead time, and lead-time standard deviation.
- **Verification:** Scorecard must isolate suppliers with lead-time standard deviation > 5 days and highlight all open purchase order lines past their promised delivery date.

### AC-05: Advanced Modeling & Calibration (Supply Chain Analyst)
- **Criterion:** Analysts must be able to view statistical distributions of daily demand, coefficient of variation (CV), forecast error metrics (WAPE, Bias), and parameterized dynamic safety stock calculations.
- **Verification:** Calibrated safety stock outputs must adjust dynamically when changing service-level Z-factor assumptions (e.g., 95% vs. 98%).

---

## 2. Business Process & Dimensional Grain Acceptance Criteria

### AC-06: Explicit Grain Enforcement across Processes
- **Criterion:** Every business process implemented in the data warehouse must maintain an explicit, non-overlapping grain:
  1. Sales Fulfillment: One row per fulfilled sales order line item.
  2. Inventory Snapshots: One row per SKU per Warehouse Facility per Snapshot Date.
  3. Procurement & Receipts: One row per purchase order line item.
  4. Demand Forecasting: One row per SKU per Warehouse/Region per Forecast Date per Target Period.
  5. Inventory Movements: One row per discrete physical transfer/adjustment event.
  6. Stockout Incidents: One row per stockout occurrence per SKU per Warehouse.
  7. Customer Returns: One row per returned sales order line item.
- **Verification:** Automated primary key uniqueness tests in dbt must pass with 0 duplicate key errors across all fact tables.

### AC-07: Conformed Dimensional Integration
- **Criterion:** Dimensions must conform across all business processes. Slicing by DimDate, DimProduct, DimWarehouse, or DimRegion must produce mathematically consistent cross-process results.
- **Verification:** Filtering by a specific SKU must concurrently show its Sales COGS, Inventory On-Hand, Open PO Inbound pipeline, and Forecasted demand without broken relationships or Cartesian joins.

---

## 3. KPI Calculation & Mathematical Integrity Criteria

### AC-08: Semi-Additive Inventory Handling
- **Criterion:** Inventory balances (OnHandQuantity, InventoryValue, AvailableQuantity) must be treated strictly as semi-additive over time.
- **Verification:** Summing inventory across warehouses on a single snapshot date must equal total stock; aggregating across multiple dates must evaluate the ending snapshot balance (or daily average) rather than accumulating cumulative sums.

### AC-09: Division-by-Zero and Outlier Protection
- **Criterion:** All ratio-based KPIs (Inventory Turns, Days of Inventory, Fill Rate, WAPE, Forecast Bias, Backorder Rate) must include explicit safeguards against zero or null denominators.
- **Verification:**
  - When Trailing COGS = 0, Days of Inventory must return NULL or a flagged value (e.g., 999+ / Inactive) without breaking dashboard visuals.
  - When Actual Demand = 0, WAPE and Forecast Bias calculations must gracefully return NULL or handle non-demand intervals cleanly.

### AC-10: Mathematical Reconciliation of Turns and DOI
- **Criterion:** Annualized Inventory Turns and Days of Inventory (DOI) must reconcile mathematically:
  \\text{Turns} \\approx \\frac{365}{\\text{DOI}}
- **Verification:** For any selected product category, multiplying calculated Turns by calculated DOI must equal approximately 365 (within rounding tolerance).

### AC-11: King\'s Dynamic Safety Stock Formula Fidelity
- **Criterion:** Safety stock calculations must account for both demand variability and supplier lead-time variability using the combined uncertainty model:
  SS = Z \\times \\sqrt{(\\overline{LT} \\times \\sigma_D^2) + (\\overline{D}^2 \\times \\sigma_{LT}^2)}
- **Verification:**
  - If lead-time variability is zero (fixed lead time), formula simplifies to  \\times \\sigma_D \\times \\sqrt{LT}$.
  - If demand variability is zero, formula simplifies to  \\times \\overline{D} \\times \\sigma_{LT}$.

---

## 4. Business Questions Resolution Criteria

### AC-12: Complete Operational Questions Coverage
- **Criterion:** The analytical system must provide the data models, measures, and visual attributes necessary to answer all 40 questions detailed in docs/business/business_questions.md.
- **Verification:** Every question must have an established query path or report visual layout that directly presents the required metrics at the designated analytical grain.

---

## 5. Data Source Feasibility & Boundary Criteria

### AC-13: Zero External Unplanned Data Dependencies
- **Criterion:** No KPI, measure, or report visual may depend on data attributes that are not captured in the planned transactional processes:
  - Inventory metrics depend solely on FactInventorySnapshot and DimProduct.
  - Sales and turnover metrics depend solely on FactSales, DimDate, and DimProduct.
  - Procurement and OTIF metrics depend solely on FactPurchaseOrder and DimSupplier.
  - Forecast error metrics depend solely on FactForecast paired with FactSales.
  - Movement and adjustment metrics depend solely on FactInventoryMovement.
  - Stockout metrics depend solely on FactStockout and zero-inventory snapshot logs.
  - Return metrics depend solely on FactReturns.
- **Verification:** Source data lineage audit confirms 100% of required fields map to planned schema entities.

---

## 6. Analytical Scale & Performance Acceptance Criteria

### AC-14: Target Volume Validation
- **Criterion:** The data architecture must scale to enterprise volume:
  - Minimum of 5 million total fact rows across core facts.
  - Target of 10M+ rows across FactInventorySnapshot, FactSales, and FactPurchaseOrder.
  - Realistically sized dimension tables (thousands of SKUs, dozens of warehouses/suppliers).
- **Verification:** Fact row counts verified via BigQuery table metadata and dbt run test logs.

### AC-15: Query Response Time SLA
- **Criterion:** Power BI visual rendering and analytical filtering across 5M–10M+ rows must satisfy an interactive user experience SLA:
  - Executive KPI cards and summary visuals: <= 2.5 seconds.
  - Granular SKU matrix filtering and drill-through: <= 5.0 seconds.
- **Verification:** Power BI Performance Analyzer recordings confirm all visual queries execute within specified latency thresholds.

---

## 7. What-If Simulation Acceptance Criteria

### AC-16: Interactive Scenario Modeling
- **Criterion:** The reporting interface must support interactive parameter simulation for:
  1. Service-Level Target Slider (Z-factor: 90% to 99.5%).
  2. Supplier Lead-Time Disruption Delta (+/- 1 to 14 days).
  3. Annual Carrying Cost Rate assumption (15% to 30%).
- **Verification:** Changing parameter sliders immediately recalculates required Safety Stock units, total working-capital impact ($), and annual carrying cost ($) in real time.\n