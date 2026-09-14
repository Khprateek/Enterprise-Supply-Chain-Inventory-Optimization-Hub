# Power BI Report Canvas Architecture: Page 4 ? Supplier Performance & Procurement

This document details the visual design specifications, visual hierarchy, layout grid, measure bindings, interaction mechanics, and drill-through pathways for **Page 4: Supplier Performance & Procurement**.

---

## 1. Page Objective & Operational Context

Page 4 serves as the operational command dashboard for **Procurement Managers**, **Category Sourcing Leads**, and **Supplier Relationship Managers**. It answers:
1. *Are suppliers meeting contractual On-Time In-Full (OTIF) service levels?*
2. *How much procurement spend is committed to high-risk or chronically delayed vendors?*
3. *What are the actual lead-time deviations (variance vs quoted contract SLA)?*
4. *What proportion of inbound shipments are failing dock receiving quality inspections?*

---

## 2. Canvas Layout & Visual Hierarchy (16:9 1920x1080 Grid)

```
+-------------------------------------------------------------------------------------------------------------+
| TOP HEADER & NAV BAR: Title | Executive Tabs (1..9) | Vendor Tier Slicer | PO Volume Badge (1.11M Lines)    |
+-------------------------------------------------------------------------------------------------------------+
| ROW 1: 5 HEADLINE METRIC CARDS                                                                              |
| [Procurement Spend]   [Supplier OTIF Rate]    [On-Time Delivery %]    [In-Full Line Fill %]   [Avg Lead-Time Delay]
| $34.05 B              35.8% (Target 85%)      39.9%                   85.4% (1.36B Units)     +1.6 Days Late        |
+------------------------------------------------------+------------------------------------------------------+
| ROW 2 (LEFT, 6 cols): VENDOR TIER COMPARISON         | ROW 2 (RIGHT, 6 cols): INBOUND RECEIVING QUALITY     |
| - Tier 1 Strategic (50 vendors): 64.9% OTIF, 8.2d LT | - Units Received: 1.36B (98.52% Accepted)            |
| - Tier 2 Preferred (150 vendors): 38.4% OTIF, 22.4d  | - Dock Rejections: 20.19M units (1.48% Defect Rate)  |
| - Tier 3 Tactical (300 vendors): 8.8% OTIF, 45.8d LT | - Delay Root Causes: Port/Customs 48%, Shortage 32%  |
|   Tactical vendors drive +4.0d delays & 68% stockouts|   Carrier 20% [Alert: 300 Tier 3 Vendors at Risk]    |
+------------------------------------------------------+------------------------------------------------------+
| ROW 3: CRITICAL SLA BREACH WATCHLIST (High Spend with OTIF < 15%)                                           |
| - SUP-0035 ($176.6M Spend, 8.5% OTIF, 47.9d LT, +3.9d Var) -> Action: Shift 30% Volume                     |
| - SUP-0057 ($153.2M Spend, 9.1% OTIF, 36.9d LT, +3.9d Var) -> Action: Penalty Fee Apply                    |
| - SUP-0436 ($133.7M Spend, 8.3% OTIF, 45.0d LT, +4.0d Var) -> Action: Dual-Source Mandate                  |
| - SUP-0472 ($127.5M Spend, 9.2% OTIF, 57.0d LT, +4.0d Var) -> Action: Audit SLA Breach                     |
| - SUP-0309 ($125.2M Spend, 8.2% OTIF, 28.9d LT, +3.9d Var) -> Action: Freeze New POs                       |
+-------------------------------------------------------------------------------------------------------------+
| FOOTER: Vendor Base (500 Suppliers) | $34.05B Spend across 1.11M Lines | Scorecard Mart: 11,852 Months     |
+-------------------------------------------------------------------------------------------------------------+
```

---

## 3. Visual Element Specifications & Measure Bindings

### 3.1 Headline Metric Cards (Row 1)

| Visual Card | Title | Primary Measure Binding | Benchmark / Target | Status Color |
| :--- | :--- | :--- | :--- | :--- |
| **Card 1** | **Total Procurement Spend** | `[Total Procurement Spend]` ($34.05 B) | 1,110,903 PO lines | Neutral |
| **Card 2** | **Supplier OTIF Rate** | `[Procurement OTIF Rate Pct]` (35.8%) | Target: 85.0% (Critical Gap) | Amber `#f59e0b` |
| **Card 3** | **On-Time Delivery Rate** | `[Procurement On-Time Rate Pct]` (39.9%) | Arrival $\le$ Promised Date | Purple `#a855f7` |
| **Card 4** | **In-Full Line Fill Rate** | `[Procurement In-Full Rate Pct]` (85.4%) | 1.36B units received | Emerald `#10b981` |
| **Card 5** | **Avg Lead-Time Delay** | `[Average Lead Time Variance Days]` (+1.6d) | Actual 25.8d vs Quoted 24.2d | Rose `#f43f5e` |

### 3.2 Vendor Classification Tier Comparison (Row 2, Left)
* **Visual Type:** Tiered Comparison Cards.
* **Dimensions:** `DimSupplier[SupplierTier]` (Strategic, Preferred, Tactical).
* **Tier Metrics:**
  - **Tier 1 Strategic (50 vendors):** **64.9% OTIF**, 8.2 days mean lead time, **0.0 days variance**, 98.2% fill rate.
  - **Tier 2 Preferred (150 suppliers):** **38.4% OTIF**, 22.4 days mean lead time, **+1.2 days variance**, 84.1% fill rate.
  - **Tier 3 Tactical (300 vendors):** **8.8% OTIF**, 45.8 days mean lead time, **+4.0 days late**, 73.6% fill rate.
* **Analytical Finding:** Tier 3 tactical suppliers are responsible for **68% of downstream warehouse stockout incidents**, directly tying poor procurement compliance to customer revenue losses.

### 3.3 Inbound Receiving Quality & Root Causes (Row 2, Right)
* **Visual Type:** Dual KPI & Progress Bar Visual.
* **Measures:**
  - `[Total PO Received Quantity]` = 1,364,506,058 units.
  - `[Total PO Rejected Quantity]` = 20,185,926 units (QA failure).
  - `[Inbound Defect Rate Pct]` = **1.48%**.
* **Delay Root Causes Breakdown:**
  - Customs & Port Congestion (Overseas): **48%** (+7 to +14 days delay).
  - Raw Material Shortage (Tier 3): **32%** (+3 to +5 days delay).
  - Carrier & Freight Inefficiency: **20%** (+1 to +2 days delay).

### 3.4 Critical SLA Breach Watchlist (Row 3, Bottom)
* **Visual Type:** Power BI Table Visual with action recommendations.
* **Filter:** `[Procurement OTIF Rate Pct] < 15%` ordered by `[Total Procurement Spend]` descending.
* **Top Vendors at Risk:**
  1. `SUP-0035` (Global Vendor 0035 Co.): \$176.6M Spend, 8.5% OTIF, 47.9d LT (+3.9d Var) $	o$ **Shift 30% Volume**.
  2. `SUP-0057` (Global Vendor 0057 Co.): \$153.2M Spend, 9.1% OTIF, 36.9d LT (+3.9d Var) $	o$ **Apply Penalty Fees**.
  3. `SUP-0436` (Global Vendor 0436 Co.): \$133.7M Spend, 8.3% OTIF, 45.0d LT (+4.0d Var) $	o$ **Dual-Source Mandate**.
  4. `SUP-0472` (Global Vendor 0472 Co.): \$127.5M Spend, 9.2% OTIF, 57.0d LT (+4.0d Var) $	o$ **Audit SLA Breach**.
  5. `SUP-0309` (Global Vendor 0309 Co.): \$125.2M Spend, 8.2% OTIF, 28.9d LT (+3.9d Var) $	o$ **Freeze New POs**.

---

## 4. Navigation & Cross-Filtering Interactions

1. **Tier Slicing:** Selecting Tier 1 Strategic partners isolates vendors capable of short-lead time JIT delivery.
2. **Purchase Order Drill-Through:** Right-clicking any supplier code opens a line-item receiving ledger showing individual PO creation dates, promised delivery dates, and actual dock receipt timestamps.
