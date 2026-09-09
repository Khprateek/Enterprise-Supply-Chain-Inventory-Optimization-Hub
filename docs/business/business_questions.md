# Business Questions Catalog: Enterprise Supply Chain & Inventory Optimization Hub

This document defines 40 operationally meaningful business questions that the analytics platform must answer. Each question is mapped to its primary persona, required KPIs/metrics, analysis grain, and the resulting business decision or operational action.

---

## Domain 1: Executive Working Capital & Network Performance

### Q01: What is the total enterprise inventory valuation and how is it distributed across global operating regions?
- **Primary Persona:** VP of Operations
- **Key Metrics:** Total Inventory Value ($), Average Inventory Value ($), Regional Share of Inventory (%).
- **Analysis Grain:** Enterprise / Region / Monthly Snapshot.
- **Action Triggered:** Rebalance strategic capital allocation and set regional inventory budget ceilings.

### Q02: What is the company-wide annualized inventory turnover ratio, and how has it trended over the past 12 months?
- **Primary Persona:** VP of Operations
- **Key Metrics:** Inventory Turns (Turnover Ratio), Annualized COGS ($), Average Inventory Value ($).
- **Analysis Grain:** Enterprise / Fiscal Month.
- **Action Triggered:** Identify macro velocity slowdowns and enforce working capital reduction targets.

### Q03: How much capital is currently locked up in unproductive inventory (excess stock + dead stock) across product categories?
- **Primary Persona:** VP of Operations, Regional Supply Planner
- **Key Metrics:** Working-Capital Exposure ($), Excess Inventory Value ($), Dead Stock Value ($).
- **Analysis Grain:** Product Category / Brand / Current Snapshot.
- **Action Triggered:** Mandate cross-functional liquidation initiatives and curtail procurement budgets for overstocked categories.

### Q04: What is our total annual inventory carrying cost, and which facilities contribute the most to storage overhead?
- **Primary Persona:** VP of Operations, Supply Chain Analyst
- **Key Metrics:** Inventory Carrying Cost ($), Average Inventory Value ($), Storage Utilization (%).
- **Analysis Grain:** Warehouse Facility / Annualized.
- **Action Triggered:** Review facility lease costs, optimize regional storage footprints, and rationalize slow-moving inventory.

### Q05: Are we meeting our enterprise customer service level target of 96% without holding disproportionate safety stock?
- **Primary Persona:** VP of Operations
- **Key Metrics:** Customer Service Level (%), Fill Rate (%), Days of Inventory (DOI), Dynamic Safety Stock (Units).
- **Analysis Grain:** Enterprise / Customer Channel / Monthly.
- **Action Triggered:** Assess the trade-off between customer satisfaction SLAs and inventory holding costs.

### Q06: What is the estimated lost sales revenue resulting from stockout events across commercial channels?
- **Primary Persona:** VP of Operations, Regional Supply Planner
- **Key Metrics:** Estimated Lost Revenue ($), Stockout Incidents Count, Impacted Customer Orders.
- **Analysis Grain:** Customer Channel (Wholesale, Retail, E-Commerce) / Quarter.
- **Action Triggered:** Prioritize inventory allocation to high-margin channels during constrained supply periods.

---

## Domain 2: Inventory Health, Aging, Excess & Dead Stock

### Q07: Which specific warehouses have the highest concentration of excess inventory?
- **Primary Persona:** Regional Supply Planner, Warehouse Planner
- **Key Metrics:** Excess Inventory Value ($), Excess Units, Warehouse Capacity Utilization (%).
- **Analysis Grain:** Warehouse Facility / SKU / Snapshot Date.
- **Action Triggered:** Halt inbound PO deliveries to congested facilities and trigger inter-warehouse transfers.

### Q08: Which SKUs currently qualify as Dead Stock (>180 days with zero sales or outward movement)?
- **Primary Persona:** Warehouse / Inventory Planner, Procurement Manager
- **Key Metrics:** Dead Stock Value ($), Days Since Last Movement, On-Hand Units.
- **Analysis Grain:** SKU / Warehouse / Snapshot Date.
- **Action Triggered:** Initiate salvage markdown, return-to-vendor (RTV) requests, or scrap write-off authorizations.

### Q09: Which SKUs have a Days of Inventory (DOI) exceeding 120 days against a supplier lead time of less than 30 days?
- **Primary Persona:** Regional Supply Planner, Supply Chain Analyst
- **Key Metrics:** Days of Inventory (Days), Supplier Lead Time (Days), Inventory Value ($).
- **Analysis Grain:** SKU / Warehouse / Snapshot Date.
- **Action Triggered:** Cancel or push out future purchase order delivery dates with suppliers.

### Q10: How much inventory is in an aging band of 91–180 days, and what is the risk of it turning into dead stock?
- **Primary Persona:** Warehouse / Inventory Planner
- **Key Metrics:** Aging Stock Value by Bracket (0-30, 31-60, 61-90, 91-180, 180+ days), On-Hand Units.
- **Analysis Grain:** SKU / Warehouse / Category.
- **Action Triggered:** Coordinate with sales and marketing to launch promotional bundles before shelf-life deterioration.

### Q11: Where are inter-warehouse inventory rebalancing transfers feasible to resolve localized stock imbalances?
- **Primary Persona:** Regional Supply Planner
- **Key Metrics:** Available Stock at Node A, Deficit / Below-ROP at Node B, Inter-Facility Transit Cost ($).
- **Analysis Grain:** SKU Pair (Origin Warehouse -> Destination Warehouse).
- **Action Triggered:** Execute stock transfer orders rather than issuing new external purchase orders.

### Q12: What proportion of total inventory value is tied up in slow-moving items versus fast-moving items?
- **Primary Persona:** Supply Chain Analyst
- **Key Metrics:** Inventory Value by Velocity Tier ($), Share of Total Inventory (%), Inventory Turns.
- **Analysis Grain:** SKU Velocity Class / Product Category.
- **Action Triggered:** Adjust replenishment policies: shift slow-movers to make-to-order or central DC stocking.

---

## Domain 3: Stockout Risk, Safety Stock & Replenishment Execution

### Q13: Which SKUs are currently below their Reorder Point (ROP) and require an immediate replenishment purchase order?
- **Primary Persona:** Warehouse / Inventory Planner, Procurement Manager
- **Key Metrics:** Net Available Inventory (OnHand + OnOrder - Reserved), Reorder Point (Units), Deficit Units.
- **Analysis Grain:** SKU / Warehouse Facility / Daily Operational Grain.
- **Action Triggered:** Generate and release emergency purchase orders or replenishment requisitions.

### Q14: Which SKUs have zero available stock today while open sales order backorders exist?
- **Primary Persona:** Warehouse / Inventory Planner, Regional Supply Planner
- **Key Metrics:** On-Hand Units (0), Backordered Units, Unfulfilled Sales Order Count, Customer Order Value at Risk ($).
- **Analysis Grain:** SKU / Warehouse / Daily.
- **Action Triggered:** Expedite pending dock receipts and notify commercial customer account managers.

### Q15: Which SKUs are projected to stock out within the next 14 days based on current burn rate and inbound PO schedules?
- **Primary Persona:** Regional Supply Planner
- **Key Metrics:** Projected Stockout Date, Days of Supply Remaining, Inbound PO Expected Arrival Date.
- **Analysis Grain:** SKU / Warehouse / Daily Forward Projection.
- **Action Triggered:** Request premium air-freight expediting from suppliers on critical path shipments.

### Q16: How does actual on-hand stock compare against recommended dynamic safety stock levels across warehouses?
- **Primary Persona:** Supply Chain Analyst, Regional Supply Planner
- **Key Metrics:** On-Hand Units, Recommended Dynamic Safety Stock (SS), Buffer Surplus/Deficit (Units).
- **Analysis Grain:** SKU / Warehouse Facility.
- **Action Triggered:** Recalibrate ERP min/max inventory master data to align with statistical recommendations.

### Q17: What is the historical stockout frequency and stockout duration across our top 100 revenue-generating SKUs?
- **Primary Persona:** Regional Supply Planner, VP of Operations
- **Key Metrics:** Stockout Rate (%), Stockout Incidents Count, Total Stockout Duration (Days).
- **Analysis Grain:** Top 100 Class A SKUs / Quarterly.
- **Action Triggered:** Re-evaluate safety stock Z-scores for mission-critical revenue drivers.

### Q18: Which warehouses have experienced the highest number of stockout events due to internal inventory record inaccuracies?
- **Primary Persona:** Warehouse / Inventory Planner
- **Key Metrics:** Stockout Events attributed to Record Discrepancy, Cycle Count Adjustment Variance ($).
- **Analysis Grain:** Warehouse Facility / Monthly.
- **Action Triggered:** Mandate physical cycle counts and audit inventory put-away processes.

---

## Domain 4: SKU Segmentation & Demand Volatility (ABC-XYZ)

### Q19: Which SKUs fall into the critical 'AZ' segment (High Revenue Contribution, High Demand Volatility)?
- **Primary Persona:** Regional Supply Planner, Supply Chain Analyst
- **Key Metrics:** Annual Consumption Value ($), Revenue Share (%), Coefficient of Variation (CV) of Demand.
- **Analysis Grain:** SKU / Global Enterprise Grain.
- **Action Triggered:** Apply rigorous collaborative planning, dynamic safety stock buffers, and weekly executive reviews.

### Q20: What is the revenue and volume distribution across the full ABC-XYZ matrix (AX, AY, AZ, BX, BY, BZ, CX, CY, CZ)?
- **Primary Persona:** Supply Chain Analyst, VP of Operations
- **Key Metrics:** SKU Count, Inventory Value ($), Sales Revenue ($), Inventory Turns by ABC-XYZ Segment.
- **Analysis Grain:** Segment Matrix (9 Cells).
- **Action Triggered:** Formulate differentiated replenishment strategies per quadrant (e.g., automated Kanban for AX; consignment/MTO for CZ).

### Q21: Which 'CX' products (Low Revenue, Steady Predictable Demand) are being over-managed with excessive manual overrides?
- **Primary Persona:** Regional Supply Planner
- **Key Metrics:** SKU Count, Forecast Accuracy (%), Planner Override Count, Days of Inventory.
- **Analysis Grain:** Product Subcategory / SKU.
- **Action Triggered:** Automate replenishment using statistical min/max rules to free up planner capacity.

### Q22: How many SKUs transitioned across ABC classes over the past four quarters (portfolio volatility)?
- **Primary Persona:** Supply Chain Analyst
- **Key Metrics:** Previous ABC Tier, Current ABC Tier, Revenue Growth Rate (%).
- **Analysis Grain:** SKU / Trailing 4 Quarters.
- **Action Triggered:** Identify emerging growth products requiring promotion to higher service-level policies.

### Q23: Which product categories have the highest proportion of high-variability (Z-class) products?
- **Primary Persona:** Regional Supply Planner
- **Key Metrics:** Percentage of SKUs in Z-Class (%), Mean CV of Demand, Stockout Rate (%).
- **Analysis Grain:** Product Category / Brand.
- **Action Triggered:** Negotiate shorter supplier lead times and higher supplier flexibility for volatile categories.

### Q24: What is the working capital requirement to support an ABC-differentiated service level policy (e.g., 99% for A, 95% for B, 90% for C)?
- **Primary Persona:** VP of Operations, Supply Chain Analyst
- **Key Metrics:** Simulated Safety Stock Investment ($), Service Level Target (%), Inventory Carrying Cost ($).
- **Analysis Grain:** ABC Class / Enterprise.
- **Action Triggered:** Adopt differentiated SLA targets to release up to 15% in working capital.

---

## Domain 5: Demand Forecasting Performance, Error & Bias

### Q25: Which SKUs exhibit severe forecast bias (systematic over-forecasting by >15% or under-forecasting by >15%)?
- **Primary Persona:** Regional Supply Planner, Supply Chain Analyst
- **Key Metrics:** Forecast Bias (%), Mean Error, Forecast Quantity vs. Actual Shipped Quantity.
- **Analysis Grain:** SKU / Warehouse / Trailing 3 Months.
- **Action Triggered:** Audit baseline statistical algorithms and remove persistent commercial optimism or pessimism.

### Q26: What is the Weighted Absolute Percentage Error (WAPE) across product categories over the past 6 months?
- **Primary Persona:** Regional Supply Planner, VP of Operations
- **Key Metrics:** WAPE (%), Total Absolute Error Units, Total Actual Sales Units.
- **Analysis Grain:** Product Category / Fiscal Month.
- **Action Triggered:** Target forecast improvement workshops on the worst-performing product categories.

### Q27: Where do planner manual overrides degrade forecast accuracy compared to the unconstrained statistical baseline?
- **Primary Persona:** Supply Chain Analyst
- **Key Metrics:** Baseline Statistical WAPE (%) vs. Final Consensus WAPE (%), Forecast Value Add (FVA %).
- **Analysis Grain:** Planner / Product Category / Monthly.
- **Action Triggered:** Enforce override governance; restrict manual touches to verified market disruptions or promotions.

### Q28: How does forecast accuracy vary by customer channel (E-Commerce vs. Wholesale Distributors vs. Retail Stores)?
- **Primary Persona:** Regional Supply Planner
- **Key Metrics:** Channel-Specific WAPE (%), Bias (%), Fill Rate (%).
- **Analysis Grain:** Customer Channel / Monthly.
- **Action Triggered:** Establish dedicated forecasting models tailored to distinct channel ordering dynamics.

### Q29: Which high-volume Class A SKUs have had deteriorating forecast accuracy over three consecutive planning cycles?
- **Primary Persona:** Regional Supply Planner
- **Key Metrics:** 3-Month WAPE Trend, Forecast Bias Direction, Revenue at Risk ($).
- **Analysis Grain:** Class A SKUs / Trailing 3 Planning Cycles.
- **Action Triggered:** Initiate collaborative customer joint business planning (JBP) and point-of-sale (POS) data integration.

### Q30: What is the relationship between forecast error (WAPE) and stockout incidence across distribution centers?
- **Primary Persona:** Supply Chain Analyst
- **Key Metrics:** Correlation Coefficient, WAPE (%), Stockout Incidents Count.
- **Analysis Grain:** Warehouse / Product Category.
- **Action Triggered:** Quantify the financial return on investment for upgrading enterprise demand planning tools.

---

## Domain 6: Procurement & Supplier Reliability

### Q31: Which suppliers have the lowest On-Time In-Full (OTIF) delivery compliance over the trailing 90 days?
- **Primary Persona:** Procurement Manager
- **Key Metrics:** Supplier OTIF (%), On-Time Delivery Rate (%), In-Full Delivery Rate (%), Total Inbound PO Spend ($).
- **Analysis Grain:** Supplier / Vendor Tier / Trailing 90 Days.
- **Action Triggered:** Issue formal vendor corrective action requests (CAR) and implement contractual SLA penalties.

### Q32: Which suppliers exhibit high lead-time variability (standard deviation > 5 days), and what is the impact on safety stock?
- **Primary Persona:** Procurement Manager, Supply Chain Analyst
- **Key Metrics:** Mean Actual Lead Time (Days), Lead-Time Std Dev (Sigma LT), Required Dynamic Safety Stock (Units).
- **Analysis Grain:** Supplier / Product Category.
- **Action Triggered:** Prioritize suppliers with reliable lead times even if their unit purchase cost is marginally higher.

### Q33: Which open purchase orders are currently overdue for dock arrival, and what customer orders are impacted?
- **Primary Persona:** Procurement Manager, Warehouse / Inventory Planner
- **Key Metrics:** Overdue Days, Open PO Quantity, Committed PO Spend ($), Linked Backordered Sales Orders.
- **Analysis Grain:** PO Line Item / Supplier / Receiving Warehouse.
- **Action Triggered:** Contact supplier logistics team immediately for tracking updates and expedite container transport.

### Q34: What is the gap between contracted supplier lead time and actual empirical dock-to-stock receipt time?
- **Primary Persona:** Procurement Manager
- **Key Metrics:** Contract Quoted Lead Time (Days), Actual Lead Time (Days), Lead Time Variance (Days).
- **Analysis Grain:** Supplier / SKU / Purchasing Route.
- **Action Triggered:** Update ERP master vendor lead-time parameters to prevent perpetual early or late replenishment orders.

### Q35: How is total procurement spend distributed across supplier risk tiers and single-sourced SKUs?
- **Primary Persona:** Procurement Manager, VP of Operations
- **Key Metrics:** Total Committed Spend ($), Single-Sourced SKU Count, Supplier Risk Score.
- **Analysis Grain:** Supplier / Risk Tier / SKU.
- **Action Triggered:** Launch dual-sourcing procurement tenders to eliminate single-point-of-failure vendor dependencies.

### Q36: What is the defect and rejection rate of inbound receipts by vendor during quality inspection?
- **Primary Persona:** Procurement Manager, Warehouse Planner
- **Key Metrics:** Rejected Quantity, Inbound Defect Rate (%), Scrapped PO Spend ($).
- **Analysis Grain:** Supplier / Product Category / Receiving Warehouse.
- **Action Triggered:** Put non-compliant suppliers on quality probation and demand vendor pre-shipment certifications.

---

## Domain 7: What-If Simulation & Scenario Sensitivity Analysis

### Q37: What is the working capital and carrying cost impact if executive management raises the target customer service level from 95% to 98%?
- **Primary Persona:** VP of Operations, Supply Chain Analyst
- **Key Metrics:** Delta Safety Stock Units (+%), Delta Inventory Valuation (+$), Incremental Annual Carrying Cost ($).
- **Analysis Grain:** Enterprise / Product Category / Simulation Model.
- **Action Triggered:** Present financial trade-off analysis to executive leadership before adopting new customer SLA commitments.

### Q38: If overseas supplier lead times increase by 7 days due to geopolitical or shipping lane disruption, how much additional buffer stock is required?
- **Primary Persona:** VP of Operations, Regional Supply Planner
- **Key Metrics:** Required Safety Stock Increase (Units), Additional Working Capital ($), New Reorder Points (ROP).
- **Analysis Grain:** Regional Sourcing Lane / Product Category / What-If Scenario.
- **Action Triggered:** Pre-order inventory ahead of anticipated logistics disruptions and secure secondary domestic backup suppliers.

### Q39: What would be the inventory valuation and stockout reduction if supplier lead-time standard deviation is cut by 50% through vendor collaboration?
- **Primary Persona:** Procurement Manager, Supply Chain Analyst
- **Key Metrics:** Safety Stock Reduction (Units), Capital Released ($), Expected Stockout Rate Reduction (%).
- **Analysis Grain:** Strategic Tier-1 Suppliers / Enterprise.
- **Action Triggered:** Justify investment in electronic data interchange (EDI) and vendor-managed inventory (VMI) partnerships.

### Q40: What is the sensitivity of annual inventory carrying costs to interest rate or holding rate fluctuations (e.g., 20% vs. 25%)?
- **Primary Persona:** VP of Operations
- **Key Metrics:** Total Inventory Holding Cost ($), Cost Delta ($), Minimum Required Turnover Rate.
- **Analysis Grain:** Enterprise / Fiscal Year.
- **Action Triggered:** Adjust economic order quantity (EOQ) batch sizes to reflect higher cost-of-capital constraints.\n