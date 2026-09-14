# Power BI Report Canvas Architecture: Page 1 ? Executive Control Tower

This document details the visual design specifications, visual hierarchy, layout grid, measure bindings, interaction mechanics, and drill-through pathways for **Page 1: Executive Control Tower**.

---

## 1. Page Objective & Persona Context

The **Executive Control Tower** is the primary entry point for executive leadership (VP of Operations, Chief Supply Chain Officer, Chief Financial Officer). It prioritizes **decision support** and **exception management**, answering:
1. *What is our total working-capital investment in inventory today, and is it growing faster than sales?*
2. *Are we meeting our contractual customer delivery SLAs (OTIF)?*
3. *Where are critical stockouts creating immediate revenue loss?*
4. *Which geographic regions require leadership attention?*

---

## 2. Canvas Layout & Visual Hierarchy (16:9 Standard 1920x1080)

```
+-------------------------------------------------------------------------------------------------------------+
| HEADER & NAVIGATION BAR: Title | Executive Tabs (1..9) | Global Region Slicer | As-Of Date Badge            |
+-------------------------------------------------------------------------------------------------------------+
| ROW 1: 6 HEADLINE KPI CARDS                                                                                 |
| [Inventory Value]  [Annualized Turns]  [Customer OTIF]  [Stockout Rate]  [Forecast Accuracy] [Carrying Cost]|
| $29.67 B           0.09x (DIO 4,110d)  86.4% (+1.4%)    0.13% (913 evts) 78.2% (WAPE 21.8%)  $6.53 B        |
+------------------------------------------------------+------------------------------------------------------+
| ROW 2 (LEFT, 7 cols): REGIONAL OPERATING MATRIX      | ROW 2 (RIGHT, 5 cols): INVENTORY RISK PROFILE        |
| - 6 Operating Regions (Midwest, East, West, EU, APAC)| - Healthy Active (0?60d): $18.98B (64%)              |
| - DCs Count, Current Valuation, FY24-25 COGS         | - Slow Moving (61?120d): $6.53B (22%)                |
| - Regional Customer OTIF & Stockout Risk Tier        | - Stagnant At-Risk (121?180d): $3.56B (12%)          |
|                                                      | - Dead Stock (180d+): $594M (2%) [Callout: Action]   |
+------------------------------------------------------+------------------------------------------------------+
| ROW 3 (LEFT, 7 cols): 24-MONTH VELOCITY TREND        | ROW 3 (RIGHT, 5 cols): TOP STOCKOUT EXCEPTIONS       |
| - Dual-axis / Area trend:                            | - Top 5 Outage Incidents by Estimated Lost Revenue:  |
|   1. Average Monthly Inventory Valuation ($M)        |   * SKU-01650 (Dairy @ DC-068): $301.7K lost         |
|   2. Monthly Net Sales Revenue ($M)                  |   * SKU-00881 (Household @ DC-032): $257.9K lost     |
|   Highlights working capital growth vs revenue cycle |   * SKU-00907 (Meals @ DC-080): $224.0K lost         |
+------------------------------------------------------+------------------------------------------------------+
| FOOTER: Data Freshness Timestamp | VertiPaq Storage Mode | Dynamic Security Scope | Drill-Through Prompt    |
+-------------------------------------------------------------------------------------------------------------+
```

---

## 3. Visual Element Specifications & Measure Bindings

### 3.1 Headline KPI Cards (Row 1)

| Visual Card | Title | Primary Measure Binding | Comparison / Secondary Measure | Target / Status Color |
| :--- | :--- | :--- | :--- | :--- |
| **Card 1** | **Inventory Value** | `[Inventory Value]` ($29.67 B) | Trailing 30-day average delta (+4.2%) | Blue `#3b82f6` |
| **Card 2** | **Inventory Turns** | `[Inventory Turnover Ratio]` (0.09x) | `[Days of Inventory Outstanding (DIO)]` (4,110d) | Purple `#a855f7` |
| **Card 3** | **Customer OTIF** | `[Customer OTIF Rate Pct]` (86.4%) | Target SLA (85.0%) $	o$ +1.4% | Emerald Green `#10b981` |
| **Card 4** | **Stockout Rate** | `[Daily Stockout Rate Pct]` (0.13%) | `[Estimated Lost Sales Revenue]` ($18.05M) | Rose `#f43f5e` |
| **Card 5** | **Forecast Accuracy** | `[Forecast Accuracy Pct]` (78.2%) | `[Forecast WAPE Pct]` (21.8%) | Blue `#3b82f6` |
| **Card 6** | **Carrying Cost** | `[Annual Inventory Carrying Cost]` ($6.53 B) | `[Dead Stock Valuation]` ($594M target release) | Amber `#f59e0b` |

### 3.2 Regional Distribution Matrix (Row 2, Left)
* **Visual Type:** Power BI Matrix / Table Visual.
* **Rows:** `DimRegion[RegionName]`.
* **Columns / Values:**
  - `[Facility Count] = DISTINCTCOUNT(DimWarehouse[WarehouseKey])`
  - `[Inventory Value]`
  - `[Total Cost of Goods Sold]`
  - `[Customer OTIF Rate Pct]` (Conditional formatting: Green $\ge 85\%$, Red $< 80\%$)
  - `[Regional Risk Tier] = SWITCH(TRUE(), [Customer OTIF Rate Pct] < 0.85, "High", [Daily Stockout Rate Pct] > 0.001, "Moderate", "Normal")`

### 3.3 Inventory Risk Classification (Row 2, Right)
* **Visual Type:** 100% Stacked Bar / Decomposition Progress Visual.
* **Categories:**
  - `Healthy Active (0?60d)`: \$18.98 B (64%)
  - `Slow Moving (61?120d)`: \$6.53 B (22%)
  - `Stagnant At-Risk (121?180d)`: \$3.56 B (12%)
  - `Dead Stock (180d+)`: \$594.0 M (2%)
* **Decision Callout:** Executive alert directing management to release \$594M in stagnant inventory, saving \$130.7M in carrying cost.

### 3.4 24-Month Working Capital vs Sales Velocity Trend (Row 3, Left)
* **Visual Type:** Line and Area Chart (Dual-Axis).
* **Shared Axis:** `DimDate[MonthYear]`.
* **Column / Area Values:** `[Average Daily Inventory Valuation]` (Blue Area).
* **Line Values:** `[Total Net Sales Revenue]` (Green Line).
* **Analytical Story:** Clearly shows annual sales seasonality peaks (November?December holiday surge) alongside steady inventory build-up.

### 3.5 Critical Stockout Exceptions (Row 3, Right)
* **Visual Type:** Exception Card Grid / Top-N Table.
* **Filter:** Top 5 by `[Estimated Lost Sales Revenue]`.
* **Fields:** `DimProduct[ProductSKU]`, `DimProduct[CategoryName]`, `DimWarehouse[WarehouseCode]`, `FactStockout[StockoutDurationDays]`, `FactStockout[StockoutAttributedReason]`, `FactStockout[EstimatedLostRevenueAmount]`.

---

## 4. Navigation & Cross-Filtering Interactions

1. **Regional Cross-Filtering:** Clicking any row in the Regional Operating Matrix filters all cards, trend lines, and stockout exception lists to that specific region.
2. **Drill-Through Target:**
   - Right-clicking a Region enables drill-through to **Page 2: Inventory Health** (passing `RegionKey`).
   - Right-clicking an Exception SKU enables drill-through to **Page 3: SKU Optimization** (passing `ProductKey`).
