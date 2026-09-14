# Power BI Report Canvas Architecture: Page 6 — Working Capital & Inventory Investment

This document details the visual design specifications, visual hierarchy, layout grid, measure bindings, interaction mechanics, and drill-through pathways for **Page 6: Working Capital & Inventory Investment**.

---

## 1. Page Objective & Operational Context

Page 6 functions as the strategic financial command screen for the **Chief Financial Officer (CFO)**, **VP of Supply Chain**, **Corporate Treasurer**, and **S&OP (Sales & Operations Planning) Executive Steering Committee**. It answers:
1. *How much enterprise capital is currently locked up in inventory assets across our supply chain?*
2. *What is our true annual carrying cost burden (cost of capital, physical warehousing, obsolescence, insurance)?*
3. *What is our comprehensive Cash Conversion Cycle (CCC) and what is the primary driver of cash drag?*
4. *How much trapped capital resides in severe excess forward coverage (>365 days)?*
5. *What are the actionable, prioritized S&OP levers to execute a phased $3.055B working capital release over the next 12 months?*

---

## 2. Canvas Layout & Visual Hierarchy (16:9 1920x1080 Grid)

```
+-------------------------------------------------------------------------------------------------------------+
| TOP HEADER & NAV BAR: Title | Capital Optimization Badge | Carrying Cost Rate Slicer (20% / 22% / 25%)      |
+-------------------------------------------------------------------------------------------------------------+
| ROW 1: 5 HEADLINE METRIC CARDS                                                                              |
| [Tied-Up Working Capital] [Annual Holding Cost]   [Cash Conversion Cycle] [Severe Excess Capital] [1-Yr Capital Release]
| $29.67 B                  $6.53 B / yr (@22%)     4,095.5 Days            $29.56 B (>365d)        $3.05 B (Save $672M/yr)
+------------------------------------------------------+------------------------------------------------------+
| ROW 2 (LEFT, 6 cols): CCC & CARRYING COST DECOMPOSITION| ROW 2 (RIGHT, 6 cols): CATEGORY CAPITAL PORTFOLIO  |
| - Cash Conversion Cycle:                             | - Personal Care: $4.69B Val, $1,030.9M Hold, $468.6M Rel
|   DIO 4,110.5d + DSO 30.0d - DPO 45.0d = 4,095.5d    | - Dry Grocery: $4.43B Val, $974.3M Hold, $442.9M Rel |
| - Annual Holding Cost Structure (22.0% Rate):        | - Dairy & Refrig: $4.37B Val, $960.5M Hold, $436.6M Rel
|   * Cost of Capital (10.5% WACC): $3,115.1M / yr     | - Beverages: $4.35B Val, $957.3M Hold, $435.1M Rel   |
|   * Storage & Utilities (4.5%): $1,335.0M / yr       | - Snacks & Confectionery: $4.15B Val, $912.1M Hold   |
|   * Obsolescence & Spoilage (4.0%): $1,186.7M / yr   | - Household Essentials: $4.12B Val, $905.8M Hold     |
|   * Taxes & Insurance (3.0%): $890.0M / yr           | - Chilled Ready Meals: $3.57B Val, $786.0M Hold      |
|   [Alert: 99.3% of CCC drag is excess inventory DIO] |   [Total 10% S&OP Liquidity Target: $3.055 B]        |
+------------------------------------------------------+------------------------------------------------------+
| ROW 3: PRIORITIZED S&OP CAPITAL RELEASE ROADMAP (3 Levers to Recover $3.055B)                              |
| [LEVER 1: 0–90 Days • Immediate Cap]  [LEVER 2: 90–180 Days • Network Rebalance] [LEVER 3: 180–360d • Liquidate] |
| - PO Freeze on Top 50 Excess SKUs      - Inter-facility Dynamic Transfers        - Secondary Channel Salvage|
| - Cash Preserved: $720.0 M             - Capital Reallocated: $485.0 M           - Net Cash Recovered: $1.85B|
| - Carrying Saved: $158.4 M / yr        - Stockout Lost Sales Saved: $18.05 M     - Carrying Saved: $407.0 M/yr|
+-------------------------------------------------------------------------------------------------------------+
| FOOTER: Catalog: 7,476 Pairs | Holding SLA: 22.0% | Hurdle Rate: 10.5% WACC | Drill-Through to Page 2 / 3   |
+-------------------------------------------------------------------------------------------------------------+
```

---

## 3. Visual Element Specifications & Measure Bindings

### 3.1 Headline Metric Cards (Row 1)

| Visual Card | Title | Primary Measure Binding | Benchmark / Context | Status Color |
| :--- | :--- | :--- | :--- | :--- |
| **Card 1** | **Tied-Up Working Capital** | `[Total Working Capital In Inventory]` ($29.67 B) | Closing on-hand stock ($29,667,524,616) | Neutral |
| **Card 2** | **Annual Holding Cost** | `[Annual Inventory Carrying Cost]` ($6.53 B / yr) | Baseline 22.0% Carrying SLA ($543.9M/mo) | Amber `#f59e0b` |
| **Card 3** | **Cash Conversion Cycle** | `[Cash Conversion Cycle Days]` (4,095.5 d) | DIO 4,110.5d + DSO 30.0d - DPO 45.0d | Rose `#f43f5e` |
| **Card 4** | **Severe Excess Capital** | `[Severe Excess Valuation]` ($29.56 B) | 99.6% of inventory has >365d forward cover | Rose `#f43f5e` |
| **Card 5** | **1-Yr Capital Release Target** | `[1-Yr Addressable Capital Release]` ($3.05 B) | Generates $672.1M/yr carrying cost reduction | Emerald `#10b981` |

---

### 3.2 Cash Conversion Cycle & Carrying Cost Decomposition (Row 2, Left)
* **Visual Type:** Decomposition Tile & Progress Visual.
* **Cash Conversion Cycle Formula:**
  $$\text{CCC} = \text{DIO} + \text{DSO} - \text{DPO}$$
  - **DIO (Days of Inventory Outstanding)**: **4,110.5 days** (based on average inventory valuation of \$14.75B over daily COGS of \$3.589M). On peak closing inventory (\$29.67B), spot DIO reaches **8,267.1 days**.
  - **DSO (Days Sales Outstanding)**: **30.0 days** (standard wholesale/retail customer credit terms).
  - **DPO (Days Payables Outstanding)**: **45.0 days** (supplier vendor credit terms).
  - **Net CCC**: **4,095.5 days** (99.3% of working capital cycle is consumed by inventory dwell time).

* **Carrying Cost Breakdown (at 22.0% Annual Holding Rate = $6,526.9 M / yr)**:
  1. **Cost of Capital (WACC / Hurdle Rate) — 10.5%**: **$3,115.1 M / yr** (47.7% of total holding cost; alternative ROI forgone).
  2. **Storage, Utilities & Physical Handling — 4.5%**: **$1,335.0 M / yr** (20.5% of total; warehouse space, cold-chain energy, racking, labor).
  3. **Obsolescence, Spoilage & Expiry — 4.0%**: **$1,186.7 M / yr** (18.2% of total; expiration of perishables and packaging obsolescence).
  4. **Taxes, Insurance & Inventory Shrink — 3.0%**: **$890.0 M / yr** (13.6% of total; property taxes, casualty insurance, transit loss).

---

### 3.3 Merchandise Category Working Capital Portfolio (Row 2, Right)
* **Visual Type:** Power BI Table Visual with data bars and conditional formatting.
* **Dimensions:** `DimProduct[CategoryName]`.
* **Category Metrics Breakdown:**

| Category Name | Current Valuation | Annual Hold Cost (22%) | Daily COGS | Category DIO | 1-Yr S&OP Release Target (10%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Personal Care & Hygiene** | **$4.69 B** | $1,030.9 M | $536.5 K | 8,735 days | **$468.6 M** |
| **Dry Grocery** | **$4.43 B** | $974.3 M | $546.2 K | 8,108 days | **$442.9 M** |
| **Dairy & Refrigerated** | **$4.37 B** | $960.5 M | $537.6 K | 8,121 days | **$436.6 M** |
| **Beverages** | **$4.35 B** | $957.3 M | $544.8 K | 7,987 days | **$435.1 M** |
| **Snacks & Confectionery** | **$4.15 B** | $912.1 M | $533.0 K | 7,779 days | **$414.6 M** |
| **Household Essentials** | **$4.12 B** | $905.8 M | $493.1 K | 8,349 days | **$411.7 M** |
| **Chilled Ready Meals** | **$3.57 B** | $786.0 M | $397.4 K | 8,990 days | **$357.3 M** |
| **Enterprise Total** | **$29.67 B** | **$6,526.9 M** | **$3,589.0 K** | **8,267 days** | **$3,055.0 M** |

---

### 3.4 Prioritized S&OP Capital Release Roadmap (Row 3, Bottom)
* **Visual Type:** 3-Column Milestone Cards detailing phased execution levers.

#### Lever 1: PO Release Freeze on Top 50 Excess SKUs (0–90 Days)
* **Action:** Immediately suppress automated ERP purchase orders on 50 SKUs exhibiting $>1,000$ days forward supply (e.g., `SKU-09681`, `SKU-05051`).
* **Cash Preserved:** **$720.0 M**.
* **Annual Carrying Cost Saved:** **$158.4 M / year**.

#### Lever 2: Inter-facility Rebalancing & Dynamic Transfers (90–180 Days)
* **Action:** Rebalance excess stocks from saturated hubs (`DC-027`, `DC-086`, `DC-054`) into under-stocked regional fulfillment centers.
* **Working Capital Reallocated:** **$485.0 M**.
* **Stockout Lost Revenue Recovered:** **$18.05 M / year** (eliminates 913 stockout outage incidents).

#### Lever 3: Secondary Channel Liquidation & B2B Markdowns (180–360 Days)
* **Action:** Partner with secondary off-price liquidators and B2B distributors to offload slow-moving inventory with $>2$ years coverage at discounted landed cost.
* **Net Cash Liquidity Generated:** **$1,850.0 M**.
* **Annual Carrying Cost Saved:** **$407.0 M / year**.

#### Total Program Impact:
* **Total 1-Year Addressable Liquidity Recovered:** **$3.055 B**.
* **Total Annual Carrying Cost Reduction:** **$672.1 M / year** ($56.0M monthly EBITDA improvement).

---

## 4. Navigation & Cross-Filtering Interactions

1. **Carrying Rate Slicer:** Modifying the carrying cost parameter (20%, 22%, 25%) recalculates holding costs and savings dynamically via `SELECTEDVALUE(DimScenario[AnnualCarryingCostRatePct], 22.0)`.
2. **Category Cross-Filter:** Clicking any merchandise category in the ledger filters both the CCC decomposition and the release levers to isolate that specific category's exposure.
3. **Cross-Page Drill-Through:** Right-clicking any category provides a drill-through path to **Page 2: Inventory Health** (to examine facility-level pallet distribution) or **Page 3: SKU Optimization** (to review specific SKU safety stock formulas).
