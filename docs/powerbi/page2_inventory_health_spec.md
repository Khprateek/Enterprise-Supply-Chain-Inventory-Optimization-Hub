# Power BI Report Canvas Architecture: Page 2 ? Inventory Health & Velocity

This document details the visual design specifications, visual hierarchy, layout grid, measure bindings, interaction mechanics, and drill-through pathways for **Page 2: Inventory Health**.

---

## 1. Page Objective & Operational Context

While Page 1 provides global executive oversight, **Page 2: Inventory Health** is the tactical diagnostic screen for **Regional Supply Planners** and **Inventory Controllers**. It answers:
1. *How is inventory valuation distributed across our 100 fulfillment facilities?*
2. *Which warehouses are experiencing dangerous stock build-ups versus stock depletion?*
3. *What proportion of our catalog is locked in severe excess (>365 days forward supply)?*
4. *Which specific SKU-Warehouse pairs are creating the greatest working-capital exposure?*

---

## 2. Canvas Layout & Visual Hierarchy (16:9 1920x1080 Grid)

```
+-------------------------------------------------------------------------------------------------------------+
| TOP HEADER & NAV BAR: Title | Executive Tabs (1..9) | Facility/Warehouse Slicer | As-Of Date Badge (Dec 2025)|
+-------------------------------------------------------------------------------------------------------------+
| ROW 1: 5 HEADLINE METRIC CARDS                                                                              |
| [On-Hand Units]       [Inventory Valuation]   [Avg Pallet Fill %]     [Severe Excess Capital] [Stockout Exposure]
| 1,263,327,408 units   $29.67 B                73.8% (Optimal)         $29.56 B (>365d Supply) $18.05M (913 evts)|
+------------------------------------------------------+------------------------------------------------------+
| ROW 2 (LEFT, 7 cols): WAREHOUSE HEALTH MATRIX        | ROW 2 (RIGHT, 5 cols): SUPPLY VELOCITY TIERS         |
| - Facility Code, Operating Region, Storage Capacity   | - Severe Excess (>365d): 7,310 SKUs ($29.56B, 99.6%) |
| - Current On-Hand Valuation, Daily COGS, Facility DIO | - Surplus Stock (181?365d): 122 SKUs ($90.3M, 0.3%)  |
| - Health Status Badging (Excess vs Balanced vs Risk)  | - Moderate Buffer (91?180d): 32 SKUs ($13.2M, 0.04%) |
|                                                      | - Optimal Range (30?90d): 10 SKUs ($1.8M, 0.01%)     |
|                                                      | - Low Stock Risk (<30d): 2 SKUs ($72.7K) [Alert]     |
+------------------------------------------------------+------------------------------------------------------+
| ROW 3: TOP 5 CAPITAL EXPOSURE EXCEPTIONS (Severe Excess SKUs Grid)                                          |
| - SKU-09681 (Shampoo @ DC-080): $14.92M (334K units, 343K days DIO)                                         |
| - SKU-05051 (Butter @ DC-043): $14.69M (331K units, 296K days DIO)                                          |
| - SKU-07760 (Chocolate @ DC-032): $14.60M (335K units, 239K days DIO)                                       |
| - SKU-05669 (Haircare @ DC-041): $14.48M (337K units, 289K days DIO)                                        |
| - SKU-03162 (Dishwashing @ DC-029): $14.24M (347K units, 47K days DIO)                                      |
+-------------------------------------------------------------------------------------------------------------+
| FOOTER: Active Catalog (7,476 Pairs) | 100 Storage Nodes | 731-Day Consumption Grain | Drill-Through Prompt  |
+-------------------------------------------------------------------------------------------------------------+
```

---

## 3. Visual Element Specifications & Measure Bindings

### 3.1 Headline Metric Cards (Row 1)

| Visual Card | Title | Primary Measure Binding | Target / Context | Status Color |
| :--- | :--- | :--- | :--- | :--- |
| **Card 1** | **Total On-Hand Units** | `[On-Hand Quantity]` (1,263,327,408) | Closing balance on `2025-12-31` | Neutral |
| **Card 2** | **Inventory Valuation** | `[Inventory Value]` ($29.67 B) | Standard Landed Inventory Cost | Indigo `#6366f1` |
| **Card 3** | **Avg Pallet Fill %** | `[Storage Utilization Pct]` (73.8%) | Target: 70%?85% capacity | Emerald `#10b981` |
| **Card 4** | **Severe Excess Capital** | `[Severe Excess Valuation]` ($29.56 B) | Forward coverage > 365 days | Amber `#f59e0b` |
| **Card 5** | **Stockout Exposure** | `[Estimated Lost Sales Revenue]` ($18.05 M) | 444,221 Lost Units (913 events) | Rose `#f43f5e` |

### 3.2 Warehouse Health & Concentration Matrix (Row 2, Left)
* **Visual Type:** Power BI Table / Matrix Visual.
* **Fields:** `DimWarehouse[WarehouseCode]`, `DimRegion[RegionName]`, `DimWarehouse[StorageCapacityPallets]`, `[Inventory Value]`, `[Daily COGS]`, `[Days of Inventory Outstanding (DIO)]`, `[Warehouse Health Status]`.
* **Top Nodes Identified:**
  - `DC-027` (NA West): 85,000 pallets, \$408.2M Valuation, \$38.9K Daily COGS, 10,482d DIO.
  - `DC-086` (NA Midwest): 72,000 pallets, \$398.7M Valuation, \$26.8K Daily COGS, 14,869d DIO.
  - `DC-054` (APAC SE Asia): 90,000 pallets, \$396.1M Valuation, \$45.0K Daily COGS, 8,809d DIO.
  - `DC-065` (Europe West): 65,000 pallets, \$375.3M Valuation, \$37.8K Daily COGS, 9,929d DIO.
  - `DC-068` (NA Midwest): 80,000 pallets, \$368.4M Valuation, \$56.8K Daily COGS, 6,490d DIO.

### 3.3 Supply Velocity & Health Distribution (Row 2, Right)
* **Visual Type:** Stacked Category List / Bar Visual.
* **DAX Classification:** Evaluated at SKU-Warehouse level based on DIO:
  - *Severe Excess (>365 Days):* **7,310 SKUs** (\$29.56 B / 99.6% of valuation).
  - *Surplus Stock (181?365 Days):* **122 SKUs** (\$90.31 M / 0.30% of valuation).
  - *Moderate Buffer (91?180 Days):* **32 SKUs** (\$13.22 M / 0.04% of valuation).
  - *Optimal Range (30?90 Days):* **10 SKUs** (\$1.79 M / 0.01% of valuation).
  - *Low Stock / Stockout Risk (<30 Days):* **2 SKUs** (\$72.7 K / Critical Reorder Required).
* **Operational Insight:** Immediate opportunity to throttle PO replenishment on the top 50 excess SKUs to release **\$720M in working capital** over 90 days.

### 3.4 Top Capital Exposure Exceptions (Row 3, Bottom)
* **Visual Type:** Multi-Column Card Grid displaying the top 5 capital-draining SKUs:
  1. `SKU-09681` (TerraHarvest Shampoo @ `DC-080`): **\$14.92 M valuation** (334K units on hand, 1.0 unit/day demand).
  2. `SKU-05051` (GoldenField Butter @ `DC-043`): **\$14.69 M valuation** (331K units on hand, 1.1 units/day demand).
  3. `SKU-07760` (VitalPulse Chocolate @ `DC-032`): **\$14.60 M valuation** (335K units on hand, 1.4 units/day demand).
  4. `SKU-05669` (ZenithHome Haircare @ `DC-041`): **\$14.48 M valuation** (337K units on hand, 1.2 units/day demand).
  5. `SKU-03162` (UrbanEats Dishwashing @ `DC-029`): **\$14.24 M valuation** (347K units on hand, 7.3 units/day demand).

---

## 4. Navigation & Cross-Filtering Interactions

1. **Facility Slicing:** Selecting any warehouse in the top dropdown or warehouse table slices the entire page (health tiers, cards, and excess lists) to that specific facility.
2. **Drill-Through Target:** Right-clicking any SKU exception enables drill-through to **Page 3: SKU Optimization** (passing `ProductKey` and `WarehouseKey`) to inspect safety stock, ABC/XYZ tiers, and replenishment parameters.
