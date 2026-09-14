# Power BI Report Canvas Architecture: Page 8 — Planner Workbench & Operational Replenishment

This document details the visual design specifications, visual hierarchy, layout grid, measure bindings, interaction mechanics, and drill-through pathways for **Page 8: Planner Workbench & Operational Replenishment**.

---

## 1. Page Objective & Operational Context

Page 8 serves as the daily operational execution cockpit for **Supply Chain Planners**, **Inventory Controllers**, **Dock Expediting Specialists**, and **Procurement Buyers**. Unlike executive summary dashboards, Page 8 is structured strictly as an **action-oriented decision engine** that answers:
1. *Which specific SKUs are in an immediate stockout outage requiring emergency cross-dock expediting?*
2. *Which items have breached their Reorder Point (ROP) and require inbound PO tracking?*
3. *Which inbound purchase orders ($1.21B total open spend) are scheduled to deliver into already severely overstocked facilities and must be canceled or deferred?*
4. *Which distribution centers have surplus inventory capable of fulfilling neighboring DC stockouts via internal rebalancing transfers?*

---

## 2. Canvas Layout & Visual Hierarchy (16:9 1920x1080 Grid)

```
+-------------------------------------------------------------------------------------------------------------+
| TOP HEADER & NAV BAR: Title | Action-Oriented Badge | Planner Slicer (All / Regional / Warehouse Planners)  |
+-------------------------------------------------------------------------------------------------------------+
| ROW 1: 5 OPERATIONAL HEADLINE METRIC CARDS                                                                  |
| [Active Action Triggers]  [Critical Stockouts]    [Open Inbound PO Value] [PO Cancel/Defer Opp]   [Rebalance Pool]
| 7,287 Items               1 SKU (DC-097 Outage)   $1.23 B (39,672 Lines)  $1.21 B (7,285 Items)   485.0 M units
| (Catalog Pairs to Review) (0 Units On Hand)       (In-Transit Orders)     (Suppress Excess Spend) (Internal Xfer)
+------------------------------------------------------+------------------------------------------------------+
| ROW 2 (LEFT, 8 cols): OPERATIONAL ACTION LEDGER      | ROW 2 (RIGHT, 4 cols): PLANNER QUEUES & CONTROLS     |
| Filter Pills: [All: 7,287] [Expedite: 1] [Cancel: 7,285] - Queue 1: Emergency Expedite (1 SKU, 1.6K units)  |
| - SKU-01020 (Dishwashing @ DC-097): 0 On-Hand, 0d DOS| - Queue 2: Inbound ROP Monitoring (1 SKU, 11.6K units)|
|   Open PO: 1,600 units -> Action: [⚡ Expedite Dock]  | - Queue 3: Cancel / Defer Open POs (7,285 SKUs, $1.21B)|
| - SKU-01219 (Skincare @ DC-003): 2.6K On-Hand, 18.2d | - Queue 4: Network Transfers (100 DCs, $485M pool)   |
|   Open PO: 11,600 units -> Action: [Track Carrier]   | [Planner Console: Batch Execute Priority Directives]  |
| - SKU-04290 (Crisps @ DC-056): 252K Stock, 15.6K DOS |                                                      |
|   Open PO: $1.45M (34.5K units) -> Action: [🚫 Cancel]                                                      |
| - SKU-02024 (Yogurt @ DC-083): 272K Stock, 34.4K DOS                                                        |
|   Open PO: $1.41M (34.4K units) -> Action: [🚫 Cancel]                                                      |
| - SKU-04979 (Spices @ DC-064): 210K Stock, 26.1K DOS                                                        |
|   Open PO: $1.25M (28.0K units) -> Action: [🚫 Cancel]                                                      |
+------------------------------------------------------+------------------------------------------------------+
| ROW 3: EXCEPTION RESOLUTION PLAYBOOK & ROOT CAUSE STANDARD OPERATING PROCEDURES                             |
| [SOP-01: Stockout Expedite (<4h)]     [SOP-02: PO Deferral / Kill (<24h)]    [SOP-03: Network Transfer (<48h)]
| - Cross-dock priority unloading       - Automated ERP PO suppression line    - Internal stock transfer over  |
| - Direct to packing line bypass       - Freezes up to $1.21B redundant spend - external supplier procurement  |
+-------------------------------------------------------------------------------------------------------------+
| FOOTER: Planners: 5 Assigned | Catalog: 7,476 Pairs | Open POs: 39,672 Lines | Link to Page 9 Pipeline      |
+-------------------------------------------------------------------------------------------------------------+
```

---

## 3. Visual Element Specifications & Measure Bindings

### 3.1 Headline Metric Cards (Row 1)

| Visual Card | Title | Primary Measure Binding | Operational Benchmark | Status Color |
| :--- | :--- | :--- | :--- | :--- |
| **Card 1** | **Active Action Triggers** | `[Total Planner Action Count]` (7,287) | SKU-warehouse pairs breaching thresholds | Neutral |
| **Card 2** | **Critical Stockouts** | `[Critical Stockout SKU Count]` (1) | On-hand quantity = 0 (`SKU-01020` @ `DC-097`) | Rose `#f43f5e` |
| **Card 3** | **Open Inbound PO Value** | `[Total Open In-Transit PO Amount]` ($1.23 B) | 39,672 active purchase order lines | Blue `#3b82f6` |
| **Card 4** | **PO Cancel/Defer Opportunity** | `[Overstocked Open PO Amount]` ($1.21 B) | 7,285 items with >365d supply & open POs | Amber `#f59e0b` |
| **Card 5** | **Network Rebalance Pool** | `[Rebalance Transfer Candidate Volume]` (485.0 M) | Inter-facility transfer candidates | Emerald `#10b981` |

---

### 3.2 Operational Action Ledger (Row 2, Left)
* **Visual Type:** Power BI Table Visual with action buttons and conditional color formatting.
* **Fields:** `DimProduct[ProductSKU]`, `DimProduct[ProductName]`, `DimProduct[CategoryName]`, `DimWarehouse[WarehouseCode]`, `[On-Hand Quantity]`, `[Days of Supply]`, `[Open Inbound PO Units]`, `[Operational Status]`, `[Recommended Action]`.

#### Primary Exception Records:
1. **Critical Outage Expedite**:
   - `SKU-01020` (*CascadeBrook Dishwashing Liquids* @ `DC-097`):
     - On-Hand: **0 units**, Available: **0 units**, Daily Demand: **121.7 units/day**, ROP: **3,820 units**.
     - In-Transit PO: **1,600 units**.
     - Action: **⚡ Emergency Dock Expedite** (Cross-dock receipt priority).
2. **Buffer Replenishment Tracking**:
   - `SKU-01219` (*VelvetGlow Skincare Lotions* @ `DC-003`):
     - On-Hand: **2,617 units**, Days of Supply: **18.2 days** (below 25.8d lead time), ROP: **3,918 units**.
     - In-Transit PO: **11,600 units**.
     - Action: **Track Carrier ETA** (Ensure dock receipt prior to safety stock depletion).
3. **Top PO Cancellation / Deferral Candidates (Suppressing Redundant Capital Spend)**:
   - `SKU-04290` (*Potato Crisps* @ `DC-056`): 252,605 on hand (15,630 days supply), Open PO: **$1.45M (34,450 units)** $\rightarrow$ **🚫 Cancel PO**.
   - `SKU-02024` (*Greek Yogurt* @ `DC-083`): 272,434 on hand (34,407 days supply), Open PO: **$1.41M (34,350 units)** $\rightarrow$ **🚫 Cancel PO**.
   - `SKU-04979` (*Spices & Seasonings* @ `DC-064`): 210,104 on hand (26,105 days supply), Open PO: **$1.25M (28,000 units)** $\rightarrow$ **🚫 Cancel PO**.
   - `SKU-08739` (*Carbonated Soft Drinks* @ `DC-084`): 269,066 on hand (285,050 days supply), Open PO: **$1.21M (27,250 units)** $\rightarrow$ **🚫 Cancel PO**.

---

### 3.3 Daily Operational Action Queues (Row 2, Right)
* **Visual Type:** Action Cards with Volume Badges.

1. **Queue 1 • Emergency Expedite (Red Badge)**:
   - Items with zero on-hand stock and inbound deliveries in transit.
   - Count: **1 SKU** (1,600 units).
2. **Queue 2 • Inbound ROP Monitoring (Amber Badge)**:
   - Items with on-hand stock below safety threshold where open POs are en route.
   - Count: **1 SKU** (11,600 units).
3. **Queue 3 • Cancel / Defer Inbound POs (Purple Badge)**:
   - Items with $>365$ days of existing forward supply that have active purchase orders in transit.
   - Count: **7,285 SKUs**, representing **$1,207.8 M ($1.21B)** in preventable cash commitments.
4. **Queue 4 • Network Rebalancing Transfers (Blue Badge)**:
   - Cross-regional redistribution from high-inventory facilities (`DC-027`, `DC-086`) to stockout nodes.
   - Pool: **$485.0 M valuation** across 100 DCs.

---

### 3.4 Exception Resolution Standard Operating Procedures (Row 3, Bottom)

1. **SOP-01 • Cross-Dock Priority Receiving (SLA < 4 Hours)**:
   - When an inbound shipment arrives for an active stockout item (`SKU-01020`), warehouse gate check-in flags the carrier for priority dock door assignment. Material is routed straight to customer order fulfillment, bypassing high-bay storage racks.
2. **SOP-02 • Automated PO Suppression & Deferral (SLA < 24 Hours)**:
   - Planners issue batch cancellation or 60-day delivery deferral notices to suppliers for items in Queue 3, freezing $1.21B in working capital and avoiding physical warehouse overflow.
3. **SOP-03 • Dynamic Network Rebalancing (SLA < 48 Hours)**:
   - System checks nearby regional distribution centers before external purchase orders are cut, executing inter-warehouse truckload transfers to satisfy demand with captive surplus inventory.

---

## 4. Navigation & Cross-Filtering Interactions

1. **Planner Filter Integration:** Slicing by `DimEmployeePlanner[JobRole]` or `PlannerName` filters the entire operational ledger to show only SKUs and warehouses assigned to that specific planner persona (supported by dynamic RLS).
2. **Queue Filter Pills:** Clicking any queue button (`Expedite`, `Reorder`, `Cancel PO`) dynamically filters the action ledger to display only those records.
3. **Cross-Page Drill-Through:** Right-clicking any SKU links directly to **Page 3 (SKU Optimization)** for replenishment recalibration or **Page 4 (Supplier Performance)** to evaluate vendor compliance.
