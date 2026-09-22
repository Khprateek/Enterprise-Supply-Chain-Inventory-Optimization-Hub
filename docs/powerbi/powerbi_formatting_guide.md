# Power BI Formatting & Conditional Formatting Guide
## Enterprise Supply Chain & Inventory Optimization Hub — All Pages

> **Purpose:** Step-by-step instructions for number formats and conditional formatting across every visual.  
> One place to look for all formatting rules. Update this when adding new visuals.

---

## Part 0 — Fix the "$4.1 M" Format Issue (Do This First)

### Problem
Values in the Category Safety Stock table and other visuals show `4.1` instead of `$4.1 M`.

### Root Cause
The measure returns an **absolute dollar value** (e.g., `4,100,000`). Power BI needs a format string that (a) divides by 1,000,000 and (b) adds the `$` prefix and ` M` suffix.

### Fix — Option A: Set Format on the Measure Itself (Recommended)

Do this once per measure — it applies everywhere that measure is used.

1. In the **Fields pane**, click the measure name (e.g., `Simulated Safety Stock Valuation`)
2. The **Measure tools** ribbon appears at the top — click the **Format** dropdown (shows "General" by default)
3. Select **"Custom"** from the dropdown
4. Type the format string in the box that appears

| Value Type | Format String | Example Output |
|:---|:---|:---|
| Dollar millions (e.g., 4,100,000) | `"$"#,##0.00,," M"` | **$4.10 M** |
| Dollar millions, 1 decimal | `"$"#,##0.0,," M"` | **$4.1 M** |
| Dollar millions with +/- sign | `"+$"#,##0.00,," M";"-$"#,##0.00,," M"` | **+$4.10 M** or **-$2.05 M** |
| Dollar millions, no decimals | `"$"#,##0,," M"` | **$4 M** |
| Percentage (0.243 → 24.3%) | `"+0.0%;-0.0%"` | **+24.3%** |
| Units (thousands, e.g., 4,937,336) | `#,##0.00," K"` | **4,937.3 K** |
| Units (millions) | `#,##0.00,," M"` | **4.94 M** |
| Plain count (#,##0) | `#,##0` | **879,165** |

> **How the double-comma works:** In Power BI format strings, each `,` after the number divides by 1,000. Two commas `,,` = ÷ 1,000,000.

### Apply This Format to Each Measure Right Now

| Measure | Format String |
|:---|:---|
| `[Simulated Safety Stock Valuation]` | `"$"#,##0.00,," M"` |
| `[Baseline Safety Stock Valuation]` | `"$"#,##0.00,," M"` |
| `[SS Valuation Delta]` | `"+$"#,##0.00,," M";"-$"#,##0.00,," M"` |
| `[SS Valuation Delta Pct]` | `"+0.0%;-0.0%"` |
| `[Simulated Annual Carrying Cost]` | `"$"#,##0.00,," M"` |
| `[Baseline Annual Carrying Cost]` | `"$"#,##0.00,," M"` |
| `[Carrying Cost Delta]` | `"+$"#,##0.00,," M";"-$"#,##0.00,," M"` |
| `[Simulated Dynamic Safety Stock Units]` | `#,##0" units"` |
| `[Simulated Reorder Point Units]` | `#,##0.00,," M units"` |
| `[ROP Units Delta]` | `"+#,##0;-#,##0" units"` |
| `[Demand Variance Share Pct]` | `0.0%` |
| `[LT Variance Share Pct]` | `0.0%` |
| `[Sim Service Level Z Score]` | `0.00` |

### Fix — Option B: Format Inside the Table Visual Column

Use this if you only want the format in one specific table and not everywhere.

1. Select the **Table visual**
2. Open the **Format pane** (paint roller icon)
3. Scroll to **Specific column** → select the column name from the dropdown
4. Find **Values → Format** → type the format string

---

## Part 1 — Page 7: What-If Simulation

### 1.1 Card Visuals — Number Format (5 Cards)

For each card, click the card visual → **Format pane → Callout value → Display units → Custom** → set the format string:

| Card | Measure | Format String |
|:---|:---|:---|
| Card 1: SS Units | `[Simulated Dynamic Safety Stock Units]` | `#,##0" units"` |
| Card 2: SS Valuation | `[Simulated Safety Stock Valuation]` | `"$"#,##0.00,," M"` |
| Card 3: ROP | `[Simulated Reorder Point Units]` | `#,##0.00,," M units"` |
| Card 4: WC Delta | `[SS Valuation Delta]` | `"+$"#,##0.00,," M";"-$"#,##0.00,," M"` |
| Card 5: Carry Delta | `[Carrying Cost Delta]` | `"+$"#,##0.00,," M";"-$"#,##0.00,," M"` |

---

### 1.2 Card 4 — Working Capital Delta: Dynamic Color

**Goal:** Rose when positive (capital consumed), Emerald when negative (capital released), Purple at baseline.

**Steps:**
1. Select **Card 4** (Working Capital Delta)
2. Open **Format pane** → scroll to **Callout value**
3. Click the **fx** button next to **Color**
4. In the dialog that opens:
   - **Format style:** `Field value`
   - **What field should we base this on?** → select `[WC Delta Color]`
5. Click **OK**

---

### 1.3 Category Safety Stock Sensitivity Table — Conditional Formatting

#### Step 1: Format number columns
1. Select the table visual
2. Format pane → **Specific column** → pick each column:
   - `Base SS` column → Values format: `"$"#,##0.00,," M"`
   - `Simulated SS` column → Values format: `"$"#,##0.00,," M"`
   - `Delta ($)` column → Values format: `"+$"#,##0.00,," M";"-$"#,##0.00,," M"`
   - `Delta (%)` column → Values format: `"+0.0%;-0.0%"`

#### Step 2: Color the Delta ($) column
1. Select the table visual
2. Format pane → scroll to **Cell elements**
3. Set **Apply to:** `Delta ($)` column
4. Toggle **Background color** → ON → click the **fx** button
5. In the dialog:
   - **Format style:** `Rules`
   - Add Rule 1: If value **is greater than** `0` → set color to `#f43f5e` (Rose)
   - Add Rule 2: If value **is less than** `0` → set color to `#10b981` (Emerald)
   - Add Rule 3: If value **is** `0` → set color to `#a855f7` (Purple)
6. Click **OK**

#### Step 3: Color the Delta (%) column — same logic
Repeat Step 2 for the `Delta (%)` column using the same three rules.

#### Step 4: Bold the Simulated SS column
1. Format pane → **Specific column** → `Simulated SS`
2. Turn on **Font** → **Bold**

---

### 1.4 Scenario Comparison Matrix — Conditional Formatting

#### Step 1: Format number columns
1. Select the scenario matrix table visual
2. Format pane → **Specific column** → for each column:
   - `SS Valuation` → `"$"#,##0.00,," M"`  
     *(this column uses `DimScenario[SSValuationBenchmarkM]` which is already in millions, so use `"$"0.00" M"` instead)*
   - `Capital Delta` → `"+$"0.00" M";"-$"0.00" M"`  
     *(already in millions)*
   - `Reorder Point` → `#,##0" K"`  
     *(already in thousands)*
   - `Carrying Cost` → `"$"0.00" M"`  
     *(already in millions)*

> **Why different format strings?** The benchmark columns in `DimScenario` store values already scaled (e.g., `20.20` means $20.20 M). The simulation measures store raw dollars (e.g., `20200000`). Single-comma and no-comma formats apply to pre-scaled values.

#### Step 2: Color the Capital Delta column (Rose/Emerald)
1. Select the scenario matrix table
2. Format pane → **Cell elements** → Apply to: `Capital Delta`
3. Toggle **Font color** → ON → click **fx**
4. Format style: **Rules**
   - Rule 1: Value **> 0** → Font color `#f43f5e` (Rose) + **Bold**
   - Rule 2: Value **< 0** → Font color `#10b981` (Emerald) + **Bold**
   - Rule 3: Value **= 0** → Font color `#94a3b8` (Slate)
5. Click **OK**

#### Step 3: Highlight the Combined Stress row (highest risk)
1. Format pane → **Cell elements** → Apply to: all columns, Series: `Combined Stress`
2. Toggle **Background color** → ON → click **fx**
3. Format style: **Rules** → If ScenarioName = "Combined Stress" → Background `rgba(244,63,94,0.08)`  
   *(Light rose tint — note: Power BI Rules only support number columns, so skip this if ScenarioName is text and use conditional column color instead)*

---

### 1.5 Decomposition Panel Cards — Format

| Card | Measure | Format String | Color |
|:---|:---|:---|:---|
| Term 1: Demand Share | `[Demand Variance Share Pct]` | `0.0%` | Purple `#a855f7` title |
| Term 2: LT Share | `[LT Variance Share Pct]` | `0.0%` | Blue `#3b82f6` title |
| Term 3: Z Score | `[Sim Service Level Z Score]` | `0.00` | Emerald `#10b981` title |

For each card:
1. Select the card → Format pane → **Callout value** → **Color** → pick the color above

---

## Part 2 — Page 4: Supplier Performance

### 2.1 Headline KPI Cards

| Card | Measure | Format | Color Logic |
|:---|:---|:---|:---|
| OTIF Rate | `[Supplier OTIF Rate]` | `0.0%` | ≥92% Emerald, 85-92% Amber, <85% Rose |
| Avg Lead Time | `[Average Actual Lead Time Days]` | `0.0" days"` | ≤25d Emerald, 25-30d Amber, >30d Rose |
| Late Delivery % | `[Pct Late Deliveries]` | `0.0%` | ≤8% Emerald, 8-15% Amber, >15% Rose |
| Rejection Rate | `[PO Rejection Rate]` | `0.0%` | ≤2% Emerald, 2-5% Amber, >5% Rose |

**Steps for each KPI card color:**
1. Select the card visual
2. Format pane → **Callout value** → click **fx** next to **Color**
3. Format style: **Rules**
4. Add rules per the thresholds above using the hex codes:
   - Emerald: `#10b981`
   - Amber: `#f59e0b`
   - Rose: `#f43f5e`

---

### 2.2 Delay Root Cause Bar Chart — Bar Colors

**Goal:** Customs = Rose, Shortage = Amber, Carrier = Blue, Other = Slate

**Steps:**
1. Select the Clustered Bar Chart visual
2. Format pane → **Bars** → **Colors**
3. Turn off "Match series color" if on
4. Click **fx** next to **Default color**
5. Format style: **Rules** — field: `FactPurchaseOrder[DelayRootCauseCategory]`
   - Contains "Customs" → `#f43f5e` (Rose)
   - Contains "Shortage" → `#f59e0b` (Amber)
   - Contains "Carrier" → `#3b82f6` (Blue)
   - Contains "Other" → `#94a3b8` (Slate)
   - Contains "On Time" → `#10b981` (Emerald)
6. Click **OK**

---

### 2.3 Supplier SLA Breach Watchlist Table

#### Step 1: Format columns
- `OTIF Rate` column → `0.0%`
- `Avg LT Days` column → `0.0" d"`
- `Rejection Rate` column → `0.0%`
- `Risk Rating` column → plain text

#### Step 2: Color the Risk Rating column
1. Format pane → **Cell elements** → Apply to: `Risk Rating` column
2. Toggle **Background color** → ON → **fx**
3. Format style: **Rules** (field = risk rating measure or column)
   - Contains "Critical" → Background `rgba(244,63,94,0.15)`, Font `#f43f5e` **Bold**
   - Contains "Moderate" → Background `rgba(245,158,11,0.15)`, Font `#f59e0b`
   - Contains "Low" → Background `rgba(16,185,129,0.15)`, Font `#10b981`

#### Step 3: Color the OTIF Rate column
1. Format pane → **Cell elements** → Apply to: `OTIF Rate`
2. Toggle **Font color** → ON → **fx** → Format style: **Rules**
   - ≥ 0.92 → `#10b981` (Emerald)
   - 0.85 to 0.92 → `#f59e0b` (Amber)
   - < 0.85 → `#f43f5e` (Rose)

---

## Part 3 — Page 3: SKU Optimization

### 3.1 ABC/XYZ Matrix — Cell Colors

The matrix uses `[Matrix Badge Color]` and `[Matrix Badge Background]` measures (already defined in `sku_optimization_measures.dax`).

**Steps to apply:**
1. Select the Matrix visual
2. Format pane → **Cell elements** → Apply to: **Values**
3. Toggle **Background color** → ON → **fx**
4. Format style: **Field value** → select `[Matrix Badge Background]`
5. Toggle **Font color** → ON → **fx**
6. Format style: **Field value** → select `[Matrix Badge Color]`

---

### 3.2 Inventory Buffer Status Cards

| Measure / Column | Format | Color Rule |
|:---|:---|:---|
| `[Days of Inventory Outstanding (DIO)]` | `0" days"` | ≤30d Rose, 30-730d Emerald, >730d Amber |
| `[Storage Utilization Pct]` | `0.0%` | >90% Amber, <35% Rose, otherwise Emerald |
| `[Warehouse Health Status Color]` | — | Format by field value (already returns hex) |

---

## Part 4 — Page 2: Inventory Health

### 4.1 DIO Heatmap / Table

**Steps:**
1. Select the table or matrix visual
2. Format pane → **Cell elements** → Apply to: DIO column
3. Toggle **Background color** → ON → **fx** → Format style: **Color scale**
   - Minimum color: `#f43f5e` (Rose = depleted)
   - Center color: `#10b981` (Emerald = healthy)
   - Maximum color: `#f59e0b` (Amber = excess)
   - Set Minimum = 0, Center = 90, Maximum = 730

---

### 4.2 Stock Status Column

1. Format pane → **Cell elements** → Apply to: `Status` column
2. Toggle **Font color** → ON → **fx** → Rules
   - Contains "Excess" → `#f59e0b`
   - Contains "Depletion" → `#f43f5e`
   - Contains "Balanced" → `#10b981`

---

## Part 5 — Page 1: Control Tower

### 5.1 All Control Tower KPI Cards

**Universal rule for ALL KPI cards on Control Tower:**
1. Select each card → Format pane → Callout value → **fx** next to Color
2. Format style: **Rules**
3. Apply the traffic light thresholds per KPI type (Emerald/Amber/Rose)

### 5.2 Alert Ribbon / Status Indicators
These use string measures that return hex codes (e.g., `[Warehouse Health Status Color]`).
- Always use **Format by Field Value** (not Rules) for any measure that returns a hex string.

---

## Quick Reference: Hex Color Codes

| Color Name | Hex | Use Case |
|:---|:---|:---|
| Emerald | `#10b981` | Good / On-target / Capital released |
| Amber | `#f59e0b` | Warning / Excess / Moderate risk |
| Rose | `#f43f5e` | Bad / Depletion / Critical / Capital consumed |
| Blue | `#3b82f6` | Carrier / Neutral secondary |
| Purple | `#a855f7` | Simulation / Baseline / Branded accent |
| Slate | `#94a3b8` | Inactive / No data / Low-priority |

---

## Quick Reference: Common Format Strings

| Pattern | Format String | Example |
|:---|:---|:---|
| Dollar millions (measure returns raw $) | `"$"#,##0.00,," M"` | **$4.10 M** |
| Dollar millions (column already in M) | `"$"0.00" M"` | **$4.10 M** |
| Dollar millions with sign | `"+$"#,##0.00,," M";"-$"#,##0.00,," M"` | **+$4.10 M** |
| Dollar thousands | `"$"#,##0.0," K"` | **$4.1 K** |
| Percentage | `0.0%` | **24.3%** |
| Percentage with sign | `"+0.0%;-0.0%"` | **+24.3%** |
| Units full | `#,##0" units"` | **879,165 units** |
| Units in K | `#,##0," K units"` | **4,937 K units** |
| Units in M | `#,##0.00,," M units"` | **4.94 M units** |
| Days | `0.0" d"` | **25.8 d** |
| Z-score | `0.00` | **1.65** |
| Integer count | `#,##0` | **1,842` |
