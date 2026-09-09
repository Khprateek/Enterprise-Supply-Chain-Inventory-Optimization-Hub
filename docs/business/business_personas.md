# Business Personas Specification: Enterprise Supply Chain & Inventory Optimization Hub

This document defines the five core operational and executive personas who will interact with the analytics platform. It articulates their decision boundaries, strategic/tactical questions, required data inputs, key performance indicators, and granularity requirements.

---

## 1. VP of Operations / Supply Chain Executive

### Role & Purpose
Senior executive accountable for end-to-end supply chain resiliency, working capital efficiency, customer fulfillment SLA adherence, and total operational cost across all global regions.

### Key Decisions Made
- **Working Capital Allocation:** Deciding overall capital exposure limits tied up in inventory across product categories and regions.
- **Network Balancing & Capacity Investment:** Approving regional warehouse expansions, redistribution of inventory across distribution centers (DCs), and capacity re-allocations.
- **Strategic Supplier Sourcing:** Reviewing tier-1 supplier performance for long-term contract renewals, volume splits, and dual-sourcing initiatives.
- **Service-Level Policy Setting:** Establishing company-wide target customer service levels (e.g., 95% vs. 98%) based on working capital trade-off models.

### Key Questions Asked
- What is our total inventory valuation and working-capital exposure across all regions?
- Are we meeting our enterprise service-level and On-Time In-Full (OTIF) targets without holding excessive buffer stock?
- How much cash is locked in slow-moving or dead inventory, and what is the trajectory of inventory turnover?
- Which regions or product categories present the highest risk of stockouts over the coming quarter?
- How would an inflationary shift in holding costs or supplier lead times affect our working capital?

### Data Required
- Aggregated inventory valuation by region, warehouse, and product category.
- High-level sales revenue, order fulfillment rates, and customer service level trends.
- Working capital metrics (inventory carrying cost, cash tied in excess stock).
- Supplier aggregate performance scorecards and lead-time trend indices.

### KPIs Cared About
- Total Inventory Value ($)
- Inventory Turns (annualized)
- Days of Inventory (DOI)
- Working-Capital Exposure / Excess Inventory Value ($)
- Enterprise Customer Service Level (%) / OTIF (%)
- Lost Sales Revenue due to Stockouts ($)

### Level of Detail (Grain) Required
- **Time:** Monthly, Quarterly, Year-to-Date (YTD), Year-over-Year (YoY).
- **Hierarchy:** Global &rarr; Region &rarr; Warehouse Facility &rarr; Product Category / Brand.
- **Presentation:** Summary KPI cards, trend sparklines, variance analysis, and scenario simulation toggles.

---

## 2. Regional Supply Planner

### Role & Purpose
Tactical planning professional responsible for balancing supply and demand across a defined geographic territory, ensuring regional distribution centers have adequate replenishment without overstocking.

### Key Decisions Made
- **Regional Replenishment Rebalancing:** Authorizing inter-facility transfers between central regional DCs and secondary distribution hubs.
- **Safety Stock Parameter Adjustments:** Modifying base safety stock levels for seasonal spikes, promotions, or known logistics disruptions in the region.
- **Forecast Override Validation:** Evaluating statistical baseline forecasts against regional commercial market intelligence and submitting adjustments.
- **Stockout Escalation & Allocation:** Rationing available inventory across channels (e-commerce vs. wholesale) when regional stockout risks materialize.

### Key Questions Asked
- Which regional distribution centers have critical stockout alerts in the next 14 to 30 days?
- Where do we have localized excess stock that could satisfy a pending deficit in another regional node?
- What are the primary drivers of regional forecast error—is there systemic under-forecasting (bias) in certain categories?
- Which high-velocity (Class A) SKUs have lead times trending upward from suppliers?

### Data Required
- Daily and weekly SKU-level inventory snapshots by warehouse within their region.
- Sales order demand history, backorders, and regional sales velocity.
- Statistical forecasts, actual demand consumption, and forecast error measures (WAPE, Bias).
- Open purchase order status, anticipated shipment arrivals, and transfer lead times.

### KPIs Cared About
- Regional Stockout Rate (%)
- SKU-Warehouse Fill Rate (%)
- Weighted Absolute Percentage Error (WAPE) & Forecast Bias (%)
- Days of Inventory (DOI) by Warehouse
- Inter-facility Transfer Volume & Cost
- Recommended Safety Stock vs. Actual Stock On Hand

### Level of Detail (Grain) Required
- **Time:** Daily (for current alerts) and Weekly (for 12-week forward planning horizons).
- **Hierarchy:** Region &rarr; Warehouse / DC &rarr; Product Subcategory &rarr; SKU.
- **Presentation:** Operational exception grids, forward stock projection curves, and ABC/XYZ matrices.

---

## 3. Warehouse / Inventory Planner

### Role & Purpose
Operational frontline professional stationed at or dedicated to a specific warehouse or fulfillment center. Focuses on daily stock health, storage capacity utilization, immediate stockouts, lot/movement tracking, and physical inventory reconciliations.

### Key Decisions Made
- **Immediate Reorder Triggers:** Generating purchase requisitions or expedited pull requests when stock breaches the calculated Reorder Point (ROP).
- **Dead Stock Liquidation / Quarantining:** Flagging stagnant inventory (>90/180 days with zero movement) for clearance, secondary-market liquidation, or write-off.
- **Space & Slotting Optimization:** Reallocating warehouse floor and rack capacity based on SKU velocity and physical dimension profiles.
- **Physical Count & Discrepancy Adjustments:** Investigating inventory movement variances, shrinkage, and returns processing.

### Key Questions Asked
- What specific SKUs are currently below their Reorder Point or Safety Stock threshold today?
- How many units of stock are on hand, reserved/allocated for open sales orders, and in transit to this facility?
- Which pallets/SKUs have not moved in over 90, 180, or 360 days (dead stock)?
- What inbound PO receipts are scheduled for delivery today and over the next 48 hours?
- How much customer return volume was processed this week, and how much returned inventory was returned to active stock?

### Data Required
- SKU-level daily physical inventory balances (On-Hand, Reserved, Available, In-Transit).
- Detailed inventory movement logs (receipts, picks, transfers in/out, adjustments, returns).
- Purchase order line-item status (Open, Shipped, Received, Inspected).
- Product physical attributes (dimensions, pallet requirements, storage class).

### KPIs Cared About
- Current Stockout Count / Immediate Stockout Risk SKUs
- Reorder Point (ROP) Breaches
- Dead Stock Value ($) and Dead Stock Volume (Units)
- Warehouse Capacity Utilization (%)
- Inventory Adjustment / Shrinkage Rate (%)
- Return-to-Stock Ratio (%)

### Level of Detail (Grain) Required
- **Time:** Real-time / Daily operational grain.
- **Hierarchy:** Individual Warehouse &rarr; Storage Zone &rarr; SKU / Item Code.
- **Presentation:** Priority task lists, action-oriented tabular worklists, threshold warning flags (Red/Amber/Green).

---

## 4. Procurement / Sourcing Manager

### Role & Purpose
Commercial and operational manager responsible for vendor relationships, purchase order execution, supplier contract compliance, lead-time reliability, and inbound supply risk mitigation.

### Key Decisions Made
- **Supplier Allocation & Order Placement:** Splitting PO quantities between primary and secondary vendors based on historical lead-time reliability and unit cost.
- **Expedited Freight Approvals:** Authorizing premium logistics expediting when vendor delays threaten critical Class A SKU stockouts.
- **SLA Penalty & Contract Enforcement:** Enforcing contractual penalties or renegotiating lead-time SLAs based on empirical On-Time In-Full (OTIF) scorecards.
- **Minimum Order Quantity (MOQ) & Batch Optimization:** Negotiating order batch sizes and economic order quantities (EOQ) with suppliers to balance holding costs vs. volume discounts.

### Key Questions Asked
- Which suppliers have the highest variance between quoted contract lead time and actual dock receipt lead time?
- What is the current supplier OTIF compliance rate across vendors, and who are the bottom performers?
- Which active purchase orders are currently overdue or at severe risk of late arrival?
- How much open purchase order committed spend is pending delivery by vendor and month?
- Does supplier lead-time unreliability force us to hold artificially inflated safety stock on key components?

### Data Required
- Purchase order header and line-item details (PO Date, Promised Date, Revised Date, Dock Receipt Date).
- Quantity ordered vs. quantity received vs. quantity rejected.
- Supplier master data (country, payment terms, contracted lead time, tier, primary contact).
- Unit purchasing costs, freight terms, and price variances.

### KPIs Cared About
- Supplier On-Time In-Full (OTIF %)
- Average Dock-to-Stock Lead Time (Days)
- Lead-Time Standard Deviation / Variability (Days)
- Purchase Order Line Fulfillment / Defect Rate (%)
- Total Committed Open PO Spend ($)
- Late Delivery Count & Average Delay (Days)

### Level of Detail (Grain) Required
- **Time:** Weekly and Monthly aggregations; individual PO line grain for dispute resolution.
- **Hierarchy:** Supplier &rarr; Vendor Contract Tier &rarr; Product Category &rarr; Individual SKU.
- **Presentation:** Vendor scorecards, lead-time distribution histograms, overdue PO trackers.

---

## 5. Supply Chain Analytics / BI Engineer

### Role & Purpose
Cross-functional quantitative analyst responsible for maintaining analytical models, building statistical forecasting benchmarks, parameterizing replenishment algorithms (safety stock, ROP), and delivering decision support tools.

### Key Decisions Made
- **Algorithm Calibration:** Selecting and tuning safety stock formulas (e.g., King’s formula vs. traditional normal distribution) based on demand and lead-time distributions.
- **Segmentation Criteria:** Setting threshold boundaries for ABC (revenue/consumption volume) and XYZ (coefficient of variation of demand) SKU matrices.
- **Data Quality & Model Governance:** Validating integrity across dimensions and facts, monitoring data pipeline lag, and adjusting statistical anomaly detection limits.
- **What-If Simulation Modeling:** Calibrating parameter elasticity for demand surges, supplier disruption scenarios, and carrying cost adjustments.

### Key Questions Asked
- Does our empirical demand distribution follow a normal, Poisson, or gamma distribution for low-velocity SKUs?
- What is the correlation between supplier lead-time variance and stockout incidence across warehouses?
- Are our ABC/XYZ classifications drifting over time, and do they warrant recalibration?
- What is the discrepancy between dbt analytical warehouse metrics and Power BI semantic model outputs?
- What is the sensitivity of total working capital to a 1-day reduction in average supplier lead time?

### Data Required
- Granular historical daily sales, forecasts, inventory snapshots, and purchase order receipts across a 2–3 year horizon.
- Probability distribution statistics (mean, variance, standard deviation, skewness) of daily demand and lead times.
- Dimensional hierarchies, surrogate keys, slowly changing dimension (SCD) histories, and data quality test logs.

### KPIs Cared About
- Coefficient of Variation (CV) of Demand
- Safety Stock Coverage (Target vs. Actual)
- Weighted Absolute Percentage Error (WAPE) & Mean Absolute Scaled Error (MASE)
- Data Quality Pass Rate (%) & Pipeline Ingestion Freshness
- Model Query Latency & Power BI Visual Refresh Time (seconds)

### Level of Detail (Grain) Required
- **Time:** Granular transactional/snapshot level (Day, Week, Month) with drill-down to individual timestamped events.
- **Hierarchy:** Full enterprise hierarchy (Enterprise &rarr; Region &rarr; Facility &rarr; Channel &rarr; Category &rarr; SKU &rarr; Lot/PO).
- **Presentation:** Advanced statistical scatter plots, distribution curves, simulation parameter sliders, and audit logs.
