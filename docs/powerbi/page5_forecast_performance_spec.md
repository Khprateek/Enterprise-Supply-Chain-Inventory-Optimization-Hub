# Power BI Report Canvas Architecture: Page 5 — Forecast Performance & Demand Sensing

This document details the visual design specifications, visual hierarchy, layout grid, measure bindings, interaction mechanics, and drill-through pathways for **Page 5: Forecast Performance & Demand Sensing**.

---

## 1. Page Objective & Operational Context

Page 5 serves as the core planning governance command center for **Demand Planners**, **S&OP (Sales & Operations Planning) Directors**, and **Supply Chain Analytics Leads**. It addresses:
1. *How accurately are statistical algorithms and consensus forecasts predicting customer consumption across the 24-month horizon?*
2. *Is the business operating with a systemic over-forecasting bias (driving excess holding capital) or under-forecasting bias (triggering stockouts)?*
3. *Which merchandise categories and specific SKUs exhibit severe forecast deviations requiring immediate safety stock or reorder point recalibration?*
4. *Why is WAPE (Weighted Absolute Percentage Error) mathematically mandated over traditional MAPE for this retail/FMCG portfolio?*

---

## 2. Canvas Layout & Visual Hierarchy (16:9 1920x1080 Grid)

```
+-------------------------------------------------------------------------------------------------------------+
| TOP HEADER & NAV BAR: Title | Planning Governance Badge | Model Horizon Slicer (Consensus/Stat/Adj)         |
+-------------------------------------------------------------------------------------------------------------+
| ROW 1: 5 HEADLINE METRIC CARDS                                                                              |
| [Total Actual Demand] [Consensus Forecast]    [Portfolio WAPE]        [Forecast Accuracy]     [Forecast Bias]
| 114.98 M units        118.57 M units          3.12%                   96.88% (Target >90%)    +3.12% Over (+3.59M)
+------------------------------------------------------+------------------------------------------------------+
| ROW 2 (LEFT, 7 cols): 24-MONTH DEMAND VS FORECAST    | ROW 2 (RIGHT, 5 cols): CATEGORY WAPE & BIAS LEDGER   |
| - Actual Demand (Emerald Solid Line) vs              | - Dry Grocery: 17.10M units, 2.89% WAPE, 97.1% Acc   |
|   Consensus Forecast (Teal Dashed Line)              | - Chilled Ready Meals: 12.70M, 2.94% WAPE, 97.1% Acc |
| - Seasonality peaks (Holiday Q4 spikes)              | - Personal Care: 17.17M, 2.98% WAPE, 97.0% Acc       |
| - Holt-Winters Multiplicative Seasonality tracking   | - Snacks & Confectionery: 17.12M, 3.01% WAPE, 97.0%  |
| - Insight: Holiday over-forecast (+3.9%)             | - Dairy & Refrigerated: 17.09M, 3.14% WAPE, 96.9%    |
|                                                      | - Beverages: 18.20M, 3.32% WAPE, 96.7% Acc           |
|                                                      | - Household Cleaning: 15.60M, 3.51% WAPE, 96.5% Acc  |
|                                                      | [Alert Box: Mathematical justification for WAPE]     |
+------------------------------------------------------+------------------------------------------------------+
| ROW 3: TOP FORECAST EXCEPTIONS (6 cols Left: Under-Forecasted | 6 cols Right: Over-Forecasted)              |
| [UNDER-FORECASTED: Stockout / Lost Sales Risk]       | [OVER-FORECASTED: Excess Working Capital Risk]       |
| - SKU-01328 (Beverages): Act 87.3K vs Fcst 72.8K     | - SKU-00242 (Beverages): Act 93.0K vs Fcst 108.9K    |
|   Var: -14,556 units (16.7% Under) -> Buffer Up      |   Var: +15,896 units (17.1% Over) -> Throttle PO     |
| - SKU-01410 (Dairy): Act 91.2K vs Fcst 78.8K         | - SKU-00070 (Beverages): Act 88.7K vs Fcst 104.1K    |
|   Var: -12,399 units (13.6% Under) -> Buffer Up      |   Var: +15,421 units (17.4% Over) -> Throttle PO     |
| - SKU-00971 (Dairy): Act 86.3K vs Fcst 75.7K         | - SKU-01546 (Dairy): Act 88.7K vs Fcst 103.7K        |
|   Var: -10,665 units (12.4% Under) -> Buffer Up      |   Var: +15,013 units (16.9% Over) -> Throttle PO     |
+-------------------------------------------------------------------------------------------------------------+
| FOOTER: Forecast Corpus: 179,424 Records | Metric: WAPE | Target: >90% | Drill-Through Link to Page 3        |
+-------------------------------------------------------------------------------------------------------------+
```

---

## 3. Visual Element Specifications & Measure Bindings

### 3.1 Headline Metric Cards (Row 1)

| Visual Card | Title | Primary Measure Binding | Benchmark / Context | Status Color |
| :--- | :--- | :--- | :--- | :--- |
| **Card 1** | **Total Actual Demand** | `[Actual Demand Units]` (114.98 M) | Fulfilled customer orders (731 days) | Neutral |
| **Card 2** | **Consensus Forecast** | `[Forecast Demand Units]` (118.57 M) | Planned baseline + adjustments | Teal `#0d9488` |
| **Card 3** | **Portfolio WAPE Error** | `[Forecast WAPE]` (3.12%) | Weighted Absolute % Error | Emerald `#10b981` |
| **Card 4** | **Forecast Accuracy** | `[Forecast Accuracy Pct]` (96.88%) | Target: > 90.0% (Enterprise SLA) | Emerald `#10b981` |
| **Card 5** | **Systemic Forecast Bias** | `[Forecast Bias Pct]` (+3.12%) | +3,588,571 units buffer over-forecast | Amber `#f59e0b` |

### 3.2 24-Month Demand vs Forecast Trend (Row 2, Left)
* **Visual Type:** Dual-Line Time Series Chart.
* **X-Axis:** `DimDate[YearMonth]` (Jan 2024 to Dec 2025, 24 periods).
* **Y-Axis Series:**
  - `[Actual Demand Units]` (Solid Emerald Line `#10b981`).
  - `[Forecast Demand Units]` (Dashed Teal Line `#0d9488`).
* **Analytical Insights:**
  - Seasonal holiday spikes occurring in November–December (peaking at ~6.1M–6.2M units/month).
  - Forecast models track trend slope closely, maintaining an intentional conservative safety buffer (+3.12% overall bias).

### 3.3 Merchandise Category Accuracy Ledger (Row 2, Right)
* **Visual Type:** Ranked Table Visual with conditional indicators.
* **Dimensions:** `DimProduct[ProductCategory]`.
* **Category Metrics Breakdown:**
  1. **Dry Grocery:** 17.10M units actual, **2.89% WAPE**, **97.1% accuracy**, +2.89% bias.
  2. **Chilled Ready Meals:** 12.70M units actual, **2.94% WAPE**, **97.1% accuracy**, +2.94% bias.
  3. **Personal Care:** 17.17M units actual, **2.98% WAPE**, **97.0% accuracy**, +2.98% bias.
  4. **Snacks & Confectionery:** 17.12M units actual, **3.01% WAPE**, **97.0% accuracy**, +3.01% bias.
  5. **Dairy & Refrigerated:** 17.09M units actual, **3.14% WAPE**, **96.9% accuracy**, +3.14% bias.
  6. **Beverages:** 18.20M units actual, **3.32% WAPE**, **96.7% accuracy**, +3.32% bias.
  7. **Household Cleaning:** 15.60M units actual, **3.51% WAPE**, **96.5% accuracy**, +3.51% bias.

#### Technical Rationale: WAPE vs MAPE
* **MAPE (Mean Absolute Percentage Error)**:
  $$\text{MAPE} = \frac{1}{n} \sum \left| \frac{A - F}{A} \right|$$
  - **Fatal Flaw:** Whenever actual demand $A = 0$ (such as stockout days, intermittent slow-movers, or newly introduced SKUs), division-by-zero occurs. Even with $A \approx 1$, small denominators generate artificial errors $>1000\%$, distorting enterprise portfolio rollups.
* **WAPE (Weighted Absolute Percentage Error)**:
  $$\text{WAPE} = \frac{\sum |A - F|}{\sum A}$$
  - **Enterprise Advantage:** Aggregates total absolute error across the enterprise before dividing by total actual volume. Low-volume intermittent volatility is weighted proportionately, ensuring mathematically stable, volume-weighted metrics across all hierarchy levels.

### 3.4 Forecast Exceptions Watchlist (Row 3, Bottom)

#### Left Grid: Under-Forecasted SKUs (Stockout & Lost Sales Risk)
* **Filter:** Negative Forecast Error ($A > F$), ordered by absolute variance descending.
* **Action:** Trigger immediate buffer recalibration and expediting.
* **Key Exceptions:**
  1. `SKU-01328` (Beverages): Actual 87,339 vs Forecast 72,783 $\rightarrow$ **-14,556 units (-16.7%)**.
  2. `SKU-01410` (Dairy & Refrigerated): Actual 91,182 vs Forecast 78,783 $\rightarrow$ **-12,399 units (-13.6%)**.
  3. `SKU-00971` (Dairy & Refrigerated): Actual 86,335 vs Forecast 75,670 $\rightarrow$ **-10,665 units (-12.4%)**.

#### Right Grid: Over-Forecasted SKUs (Excess Inventory & Working Capital Risk)
* **Filter:** Positive Forecast Error ($F > A$), ordered by absolute variance descending.
* **Action:** Throttle upcoming PO release and prevent warehouse over-saturation.
* **Key Exceptions:**
  1. `SKU-00242` (Beverages): Actual 92,961 vs Forecast 108,857 $\rightarrow$ **+15,896 units (+17.1%)**.
  2. `SKU-00070` (Beverages): Actual 88,719 vs Forecast 104,140 $\rightarrow$ **+15,421 units (+17.4%)**.
  3. `SKU-01546` (Dairy & Refrigerated): Actual 88,735 vs Forecast 103,748 $\rightarrow$ **+15,013 units (+16.9%)**.

---

## 4. Navigation & Cross-Filtering Interactions

1. **Category Selection:** Clicking any merchandise category in the ledger dynamically filters both the 24-month trend line and the exception cards for that category.
2. **SKU Drill-Through:** Right-clicking any exception SKU opens a drill-through path directly to **Page 3 (SKU Optimization & Replenishment)** to review safety stock coverage, reorder points, and supplier lead-time buffers.
