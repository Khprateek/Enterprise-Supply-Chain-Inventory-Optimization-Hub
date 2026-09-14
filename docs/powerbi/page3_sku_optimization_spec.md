# Power BI Report Canvas Architecture: Page 3 ? SKU Optimization & Replenishment

This document details the visual design specifications, visual hierarchy, layout grid, measure bindings, interaction mechanics, and drill-through pathways for **Page 3: SKU Optimization & Replenishment**.

---

## 1. Page Objective & Operational Context

While Page 2 diagnoses macro-level inventory health across warehouses, **Page 3: SKU Optimization** provides granular decision support for **Demand Planners** and **Inventory Strategists**. It answers:
1. *Which items generate 70% of company revenue (Tier A) versus long-tail catalog drag (Tier C)?*
2. *Which products have highly predictable demand (X) versus volatile spikes (Z)?*
3. *What is the mathematically recommended safety stock and reorder point using King's formula?*
4. *Where does forecast error threaten high-value Tier A fulfillment?*

---

## 2. Canvas Layout & Visual Hierarchy (16:9 1920x1080 Grid)

```
+-------------------------------------------------------------------------------------------------------------+
| TOP HEADER & NAV BAR: Title | Executive Tabs (1..9) | Product Category Slicer | SLA Target Badge (95% SL)   |
+-------------------------------------------------------------------------------------------------------------+
| ROW 1: 5 HEADLINE METRIC CARDS                                                                              |
| [Active Catalog]      [Mean Daily Demand]     [Dyn Recommended SS]    [Mean Lead-Time Demand] [Portfolio WAPE]
| 10,000 SKUs (2.2K A)  157.3K units/day        1.84M units (King's)    3.42M units (21.7d LT)  21.8% (78.2% Acc)|
+------------------------------------------------------+------------------------------------------------------+
| ROW 2 (LEFT, 5 cols): ABC-XYZ 9-BOX MATRIX           | ROW 2 (RIGHT, 7 cols): SKU DETAIL DRILL-THROUGH CARD |
| - 3x3 Grid: Consumption Revenue (A/B/C) vs CoV (X/Y/Z)| - Selected SKU Code, Full Name, Brand, Unit Landed Cost
| - AX (792 SKUs) | AY (978 SKUs) | AZ (430 SKUs)      | - 4 Stat Cards: Net Rev, On-Hand, Daily Demand, Lead Time
| - BX (1,146)    | BY (1,478)    | BZ (676)           | - Replenishment Formula Box: DLT + SS = Reorder Point|
| - CX (1,864)    | CY (2,540)    | CZ (1,096)         | - Forecast Error WAPE & Stockout Status Alert        |
+------------------------------------------------------+------------------------------------------------------+
| ROW 3: TOP PRIORITY SKUs ? REPLENISHMENT PARAMETER LEDGER                                                   |
| - SKU Code, Product Name, Category, Matrix Tier, Net Revenue, Current On-Hand, Daily Demand,                 |
|   Supplier Lead Time, Recommended Safety Stock, Reorder Point, Forecast Error %                             |
+-------------------------------------------------------------------------------------------------------------+
| FOOTER: Portfolio Coverage (10,000 SKUs) | Formula: King's Dual-Variability | Confidence: 95% (Z=1.65)      |
+-------------------------------------------------------------------------------------------------------------+
```

---

## 3. Visual Element Specifications & Measure Bindings

### 3.1 Headline Metric Cards (Row 1)

| Visual Card | Title | Primary Measure Binding | Target / Context | Status Color |
| :--- | :--- | :--- | :--- | :--- |
| **Card 1** | **Total Active Catalog** | `[Active SKU Count]` (10,000) | 2,200 Tier A (70% Value) | Neutral |
| **Card 2** | **Mean Daily Demand** | `[Average Daily Demand Units]` (157.3K u/d) | Total Net Sales: $4.19B | Neutral |
| **Card 3** | **Dyn Recommended Safety Stock** | `[Simulated Dynamic Safety Stock Units]` (1.84M) | King's Formula at 95% SL (Z=1.65) | Emerald `#10b981` |
| **Card 4** | **Mean Lead-Time Demand (DLT)** | `[Mean Lead-Time Demand Units]` (3.42M) | Average Replenishment Lead Time: 21.7d | Neutral |
| **Card 5** | **Portfolio WAPE Forecast Error** | `[Forecast WAPE Pct]` (21.8%) | Core Catalog Accuracy: 78.2% | Blue `#3b82f6` |

### 3.2 ABC-XYZ 9-Box Matrix (Row 2, Left)
* **Visual Type:** Custom 9-Box Matrix Grid Visual.
* **Dimensions:** `DimProduct[ABCClassification]` (Rows) by `DimProduct[XYZClassification]` (Columns).
* **Grid Distributions:**
  - `AX (Stable High-Val)`: 792 SKUs (Continuous JIT Replenishment).
  - `AY (Variable High-Val)`: 978 SKUs (Dynamic Buffer).
  - `AZ (Volatile High-Val)`: 430 SKUs (Critical Stockout Risk; Planner Focus).
  - `BX / BY / BZ (Mid-Tier)`: 3,300 SKUs (Standard Min-Max / Periodic Review).
  - `CX / CY / CZ (Long-Tail)`: 5,500 SKUs (1,096 CZ items flagged for delisting/rationalization).

### 3.3 Interactive SKU Detail Card (Row 2, Right)
* **Visual Type:** Selected Entity Card with dynamic formula breakdown.
* **Dynamic Title:** Selected `DimProduct[ProductSKU]` and `DimProduct[ProductName]`.
* **King's Replenishment Engine Breakdown:**
  $$	ext{DLT} = 	ext{AvgDailyDemand} 	imes 	ext{AvgLeadTime}$$
  $$	ext{SafetyStock} = Z 	imes \sqrt{	ext{LeadTime} 	imes \sigma_{	ext{Demand}}^2 + 	ext{Demand}^2 	imes \sigma_{	ext{LT}}^2}$$
  $$	ext{ReorderPoint} = 	ext{DLT} + 	ext{SafetyStock}$$
* **Example Benchmark (`SKU-00010` ? PrimeSelect Biscuits):**
  - Daily Demand: 128.8 units/day
  - Supplier Lead Time: 10.0 days
  - Demand During Lead Time: **1,288 units**
  - Recommended Safety Stock: **373 units**
  - Recommended Reorder Point: **1,661 units**
  - Current On-Hand: 387,019 units (Healthy buffer)

### 3.4 Priority SKU Replenishment Parameter Ledger (Row 3, Bottom)
* **Visual Type:** Power BI Interactive Table.
* **Fields:** `DimProduct[ProductSKU]`, `DimProduct[ProductName]`, `DimProduct[CategoryName]`, `Matrix Badge`, `[Total Net Sales Revenue]`, `[Current On-Hand Quantity]`, `[Daily Demand]`, `[Average Actual Lead Time Days]`, `[Safety Stock Units]`, `[Reorder Point Units]`, `[Forecast WAPE Pct]`.
* **Interactivity:** Selecting any row populates the detailed diagnostic card in Row 2.

---

## 4. Navigation & Drill-Through Pathways

1. **Category Filtering:** Selecting any category in the top slicer filters the 9-box matrix and ledger to that specific merchandise department.
2. **Supplier Performance Drill-Through:** Right-clicking any SKU in the ledger enables drill-through to **Page 4: Supplier Performance** (passing `PrimarySupplierKey`) to examine vendor OTIF, lead time variability, and SLA compliance.
