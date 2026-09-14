# Power BI Report Canvas Architecture: Page 7 — What-If Simulation & Scenario Planning

This document details the visual design specifications, visual hierarchy, layout grid, measure bindings, interaction mechanics, and drill-through pathways for **Page 7: What-If Simulation & Scenario Planning**.

---

## 1. Page Objective & Operational Context

Page 7 serves as the executive predictive sandbox and scenario modeling workspace for **Supply Chain Strategists**, **VP of Global Logistics**, and **S&OP (Sales & Operations Planning) Directors**. It enables decision-makers to:
1. *Simulate macroeconomic disruptions (demand surges, recessions, port bottlenecks) before committing procurement capital.*
2. *Dynamically recalibrate King's Dual-Variance Safety Stock and Reorder Points (ROP) across 7,476 SKU-warehouse pairs.*
3. *Quantify the non-linear working capital penalty associated with elevating customer Service Level Agreements (e.g., 95% $\rightarrow$ 98% $\rightarrow$ 99%).*
4. *Evaluate the combined financial impact on enterprise inventory investment and annual carrying cost burdens under various cost-of-capital regimes (18% to 28%).*

---

## 2. Canvas Layout & Visual Hierarchy (16:9 1920x1080 Grid)

```
+-------------------------------------------------------------------------------------------------------------+
| TOP HEADER & NAV BAR: Title | S&OP Simulation Badge | Engine: King's Dual-Variance Formula                  |
+-------------------------------------------------------------------------------------------------------------+
| PARAMETER SLIDER CONTROL BAR:                                                                               |
| [Demand Shock: -20%..+30%] [Lead-Time Shock: -5d..+15d] [Target SLA: 90/95/98/99%] [Holding Rate: 18%..28%] |
| Quick Presets: [Baseline] [Demand Surge] [Port Delay +7d] [98% SLA Target] [Combined Stress Shock] [Lean]   |
+-------------------------------------------------------------------------------------------------------------+
| ROW 1: 5 SIMULATED HEADLINE METRIC CARDS (With Dynamic Delta Badges)                                        |
| [Simulated Safety Stock]  [SS Valuation]          [Simulated ROP]         [Working Capital Delta] [Carrying Cost Delta]
| 879,165 units             $20.20 M                4.94 M units            +$0.00 M                +$0.00 M / yr
| (Delta: +0.0 K / 0.0%)    (Delta: +$0.00 M)       (4,937,336 units)       (Capital Buffer Req)    (Total: $4.44M/yr)
+------------------------------------------------------+------------------------------------------------------+
| ROW 2 (LEFT, 6 cols): PREDEFINED SCENARIO MATRIX     | ROW 2 (RIGHT, 6 cols): CATEGORY SENSITIVITY TABLE    |
| - Baseline (95% SLA, 0d LT): $20.20M SS, $4.44M Hold | - Beverages: $3.07M Base -> $4.57M Shock (+49.1%)    |
| - Demand Surge (+10%): $22.22M SS (+$2.02M Delta)    | - Dry Grocery: $3.07M Base -> $4.58M Shock (+49.1%)  |
| - Port Delay (+7d LT): $21.41M SS (+$1.21M Delta)    | - Dairy & Refrig: $3.03M Base -> $4.51M Shock (+49%) |
| - Target SLA (98% SLA): $25.10M SS (+$4.90M Delta)   | - Personal Care: $3.02M Base -> $4.50M Shock (+49%)  |
| - Stress Test (+15% D, +5d LT, 98%): $30.11M (+$9.9M)| - Snacks & Confection: $3.00M Base -> $4.47M Shock  |
| - Lean (-10% D, -3d LT, 90% SLA): $13.72M (-$6.48M)  | - Household: $2.78M Base -> $4.14M Shock (+49%)      |
| [Alert: 95%->98% SLA non-linear +24.3% capital jump] | - Chilled Ready Meals: $2.24M Base -> $3.33M Shock  |
+------------------------------------------------------+------------------------------------------------------+
| ROW 3: KING'S FORMULA MATHEMATICAL DECOMPOSITION                                                            |
| [Term 1: Demand Variance (LT x ?_D?)] [Term 2: Lead Time Variance (D? x ?_LT?)] [Term 3: Service Factor (Z)]|
| - Accounts for daily demand swings    - Accounts for port & carrier delays     - Normal curve multiplier    |
| - 64.2% of baseline variance          - 35.8% of baseline variance             - 95%=1.65, 98%=2.05, 99%=2.33
+-------------------------------------------------------------------------------------------------------------+
| FOOTER: Baseline SS: $20.20M | Baseline ROP: 4.94M units | Carrying: $4.44M/yr | Drill-Through to Page 8    |
+-------------------------------------------------------------------------------------------------------------+
```

---

## 3. Visual Element Specifications & Measure Bindings

### 3.1 Headline Metric Cards (Row 1)

| Visual Card | Title | Primary Measure Binding | Benchmark / Baseline | Status Indicator |
| :--- | :--- | :--- | :--- | :--- |
| **Card 1** | **Simulated Safety Stock** | `[Simulated Dynamic Safety Stock Units]` | 879,165 units baseline | Neutral |
| **Card 2** | **Safety Stock Valuation** | `[Simulated Safety Stock Valuation]` ($20.20 M) | Baseline landed valuation | Purple `#a855f7` |
| **Card 3** | **Simulated Reorder Points** | `[Simulated Reorder Point Units]` (4.94 M units) | 4,937,336 units coverage | Blue `#3b82f6` |
| **Card 4** | **Working Capital Delta** | `[Simulated Safety Stock Capital Delta]` (+$0.00 M) | Net buffer cash expansion/contraction | Dynamic (Emerald / Rose) |
| **Card 5** | **Carrying Cost Delta** | `[Simulated Annual Carrying Cost Delta]` (+$0.00 M / yr) | Change in annual holding cost | Amber `#f59e0b` |

---

### 3.2 What-If Parameter Controls (Slider Bar)

1. **Demand Shock Multiplier (`[Scenario Demand Multiplier]`):**
   * Range: $-20\%$ to $+30\%$ in $5\%$ increments.
   * Modifies daily consumption: $D_{\text{sim}} = D_{\text{base}} \times (1 + \Delta_{\text{Demand}})$.
2. **Lead Time Shock Days (`[Scenario Lead Time Shock Days]`):**
   * Range: $-5$ days to $+15$ days in $1$-day increments.
   * Modifies effective transit time: $LT_{\text{sim}} = 25.8 + \Delta_{LT}$.
3. **Service Level Target (`[Service Level Target Pct]`):**
   * Discrete options: $90.0\%$ ($Z=1.28$), $95.0\%$ ($Z=1.65$), $98.0\%$ ($Z=2.05$), $99.0\%$ ($Z=2.33$).
4. **Annual Holding Cost Rate (`[Annual Carrying Cost Rate]`):**
   * Range: $18.0\%$ to $28.0\%$ in $1.0\%$ increments (Default: $22.0\%$).

---

### 3.3 Predefined Scenario Comparison Matrix (Row 2, Left)
* **Visual Type:** Power BI Table Visual with Scenario Benchmarks.
* **Predefined Scenario Profiles:**

| Scenario Profile | Key Assumptions | SS Valuation | Capital Delta | Reorder Point | Annual Carrying Cost |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Baseline Plan** | 95% SLA, 0d LT Shock, 22% Hold | **$20.20 M** | **$0.00 M** | 4,937 K units | **$4.44 M / yr** |
| **Demand Surge** | +10% Demand, 0d LT, 95% SLA | **$22.22 M** | **+$2.02 M** | 5,431 K units | **$4.89 M / yr** |
| **Port Disruption** | 0% Demand, +7d LT Shock, 24% Hold | **$21.41 M** | **+$1.21 M** | 6,091 K units | **$5.14 M / yr** |
| **Target SLA 98%** | 0% Demand, 0d LT, 98% SLA ($Z=2.05$) | **$25.10 M** | **+$4.90 M** | 5,151 K units | **$5.52 M / yr** |
| **Combined Stress** | +15% Demand, +5d LT, 98% SLA | **$30.11 M** | **+$9.91 M** | 6,882 K units | **$6.62 M / yr** |
| **Lean S&OP** | -10% Demand, -3d LT, 90% SLA ($Z=1.28$) | **$13.72 M** | **-$6.48 M** | 3,825 K units | **$2.74 M / yr** |

* **Analytical Finding:** Elevating the customer service level from 95% to 98% incurs a **+$4.90M (+24.3%) capital penalty**, demonstrating the steep non-linear cost curve in standard normal tail probabilities.

---

### 3.4 Category Safety Stock Capital Sensitivity Ledger (Row 2, Right)
* **Visual Type:** Interactive Ranked Category Ledger.
* **Dimensions:** `DimProduct[CategoryName]`.
* **Category Response under Combined Stress Shock (+15% Demand, +5d LT, 98% SLA):**

| Category Name | Baseline SS ($) | Simulated SS ($) | Dollar Delta ($) | Percentage Increase (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Dry Grocery** | $3.07 M | **$4.58 M** | +$1.51 M | **+49.1%** |
| **Beverages** | $3.07 M | **$4.57 M** | +$1.50 M | **+49.1%** |
| **Dairy & Refrigerated** | $3.03 M | **$4.51 M** | +$1.48 M | **+49.0%** |
| **Personal Care & Hygiene** | $3.02 M | **$4.50 M** | +$1.48 M | **+49.0%** |
| **Snacks & Confectionery** | $3.00 M | **$4.47 M** | +$1.47 M | **+49.1%** |
| **Household Essentials** | $2.78 M | **$4.14 M** | +$1.36 M | **+49.0%** |
| **Chilled Ready Meals** | $2.24 M | **$3.33 M** | +$1.10 M | **+49.0%** |
| **Total Portfolio** | **$20.20 M** | **$30.11 M** | **+$9.91 M** | **+49.1%** |

---

### 3.5 King's Safety Stock Mathematical Decomposition (Row 3, Bottom)

$$\text{Safety Stock} = Z \times \sqrt{ (LT \times \sigma_D^2) + (D^2 \times \sigma_{LT}^2) }$$

Where:
1. **Demand Volatility Term ($LT \times \sigma_D^2$)**:
   - Represents variance generated by day-to-day customer order fluctuations during average lead time.
   - Represents **64.2%** of total system variance in the baseline model.
   - Standard deviation of demand is modeled as $\sigma_D \approx 0.45 \times \text{AvgDailyDemand}$.
2. **Supplier Lead Time Unreliability Term ($D^2 \times \sigma_{LT}^2$)**:
   - Represents variance generated by port delays, vendor stockouts, and carrier delivery unreliability.
   - Represents **35.8%** of total system variance in the baseline model.
   - Modeled with $\sigma_{LT} = 2.5\text{ days}$.
3. **Service Level Factor ($Z$-Score)**:
   - Sets stockout probability: $P(\text{Stockout}) = 1 - \text{SLA}$.
   - $Z_{90\%} = 1.28$, $Z_{95\%} = 1.65$, $Z_{98\%} = 2.05$, $Z_{99\%} = 2.33$.

---

## 4. Navigation & Cross-Filtering Interactions

1. **Parameter Slider Integration:** Moving sliders updates DAX measures dynamically using `SELECTEDVALUE` against disconnected parameter tables (`DimScenario` and Power BI What-If parameter series).
2. **Scenario Quick Preset Buttons:** Clicking any preset loads corresponding values into the parameters simultaneously.
3. **Planner Workbench Drill-Through:** Right-clicking any category or scenario outcome enables drill-through to **Page 8 (Planner Workbench)** to inspect operational SKU replenishment triggers.
