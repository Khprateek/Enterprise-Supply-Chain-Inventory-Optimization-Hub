# Business Processes Specification: Enterprise Supply Chain & Inventory Optimization Hub

This document defines the core business processes evaluated for the enterprise analytics hub. In accordance with Kimball enterprise data architecture, each business process corresponds to an operational activity within the retail/FMCG value chain. For each process, we evaluate its analytical justification, business purpose, operational grain, core dimensions, and key measures.

---

## Process Evaluation Summary

| Business Process | Analytical Value | Classification in Hub | Target Modeling Pattern |
| :--- | :--- | :--- | :--- |
| **1. Sales Fulfillment** | Critical | Primary Core Fact | Transactional Fact |
| **2. Inventory Snapshot** | Critical | Primary Core Fact | Periodic Snapshot Fact |
| **3. Procurement & Receipts**| Critical | Primary Core Fact | Accumulating / Transactional Fact |
| **4. Demand Forecasting** | High | Core Planning Fact | Periodic Snapshot Fact |
| **5. Inventory Movements** | High | Operational Detail Fact| Transactional Event Fact |
| **6. Stockout Incidents** | High | Service Risk Fact | Event / Incident Fact |
| **7. Customer Returns** | Medium-High | Reverse Logistics Fact | Transactional Fact |
| **8. Supplier Performance** | Analytical Derived | Analytical Metric Mart | Derived Analytical Views / Aggregations from Procurement |

---

## 1. Sales Fulfillment Process

### Business Purpose
Captures customer order placement, shipment, and fulfillment across wholesale, retail, and e-commerce channels. It is the primary engine of demand consumption, revenue generation, and customer service delivery. It provides the empirical baseline for demand velocity, seasonality, customer fill rates, and SKU segmentation.

### Analytical Justification
Without granular sales transactions, it is impossible to compute true demand, inventory turnover, fill rates, historical consumption rates, or ABC-XYZ classifications.

### Business Grain
**One row per fulfilled sales order line item.**

### Core Dimensions
- DimDate (Role-playing: Order Date, Ship Date, Delivery Date)
- DimProduct (SKU, Category, Brand)
- DimCustomerChannel (Customer Account, Channel: Retail, Wholesale, Direct Online)
- DimWarehouse (Fulfilling Distribution Center or Regional Facility)
- DimRegion (Destination Market Territory)

### Core Measures
- OrderedQuantity (Integer / Decimal)
- ShippedQuantity (Integer / Decimal)
- CancelledQuantity (Integer / Decimal)
- UnitPrice (Monetary Currency)
- UnitStandardCost (Monetary Currency)
- GrossSalesAmount (Extended: OrderedQuantity * UnitPrice)
- NetSalesAmount (Extended: ShippedQuantity * UnitPrice - Discounts)
- CostOfGoodsSold (COGS: ShippedQuantity * UnitStandardCost)
- OrderLineCycleTimeDays (ShipDate - OrderDate)

---

## 2. Inventory Snapshot Process

### Business Purpose
Captures periodic state-of-inventory balances at every storage location across the global network. It provides visibility into on-hand stock, reserved allocations, pipeline in-transit inventory, stock aging, and working-capital exposure.

### Analytical Justification
Inventory is fundamentally a semi-additive state over time. Daily or periodic snapshots are indispensable for tracking inventory trajectories, holding costs, working capital trends, stockout days, and stock aging curves.

### Business Grain
**One row per SKU per Warehouse Facility per Snapshot Date.**

### Core Dimensions
- DimDate (Snapshot Date)
- DimProduct (SKU, Brand, Category, Handling Profile)
- DimWarehouse (Facility Code, Region, Facility Type)
- DimRegion (Geographic Zone)

### Core Measures
- OnHandQuantity (Semi-additive over time)
- ReservedQuantity (Stock allocated to open sales orders)
- AvailableQuantity (OnHandQuantity - ReservedQuantity)
- InTransitInboundQuantity (Stock shipped on open POs or inbound transfers)
- UnitLandedCost (Current standard or weighted average cost)
- InventoryValuation (OnHandQuantity * UnitLandedCost)
- DaysOfInventoryOnHand (Calculated or snapshot attribute)
- DailyCarryingCost (InventoryValuation * Daily Holding Cost Rate)

---

## 3. Procurement & Inbound Receipts Process

### Business Purpose
Manages the supplier ordering lifecycle from purchase order issuance through dock arrival, quality inspection, and warehouse put-away. It establishes the cost baseline for inventory replenishment, reveals supplier lead times, and identifies supplier delivery compliance.

### Analytical Justification
Essential for evaluating supplier reliability, measuring actual vs. quoted lead times, identifying procurement bottlenecks, calculating purchase commitments, and driving automated reorder workflows.

### Business Grain
**One row per Purchase Order line item.**

### Core Dimensions
- DimDate (Role-playing: PO Creation Date, Promised Delivery Date, Actual Dock Receipt Date)
- DimSupplier (Vendor, Supplier Tier, Country, SLA Terms)
- DimProduct (Purchased SKU, Packaging Specification)
- DimWarehouse (Receiving Distribution Center)
- DimEmployee (Purchasing Buyer / Procurement Specialist)

### Core Measures
- OrderedQuantity (Units ordered from vendor)
- ReceivedQuantity (Units received at dock)
- RejectedQuantity (Units failed quality inspection)
- UnitPurchasePrice (Contracted price per unit)
- ExtendedSpendAmount (OrderedQuantity * UnitPurchasePrice)
- PromisedLeadTimeDays (PromisedDeliveryDate - POCreationDate)
- ActualLeadTimeDays (ActualDockReceiptDate - POCreationDate)
- LeadTimeVarianceDays (ActualLeadTimeDays - PromisedLeadTimeDays)
- OnTimeInFullFlag (Binary indicator: 1 if On-Time and In-Full, else 0)

---

## 4. Demand Forecasting Process

### Business Purpose
Captures forward-looking baseline statistical projections and planner-adjusted consensus forecasts across forward planning horizons. It acts as the benchmark against which actual consumption is evaluated to gauge forecast accuracy, bias, and replenishment requirements.

### Analytical Justification
Supply chain optimization cannot operate reactively. Comparing demand forecasts against actual sales is required to compute forecast error metrics (WAPE, Bias, MAPE), calibrate safety stocks, and optimize replenishment schedules.

### Business Grain
**One row per SKU per Warehouse (or Regional Market) per Forecast Generation Date per Target Horizon Date (Weekly/Monthly bucket).**

### Core Dimensions
- DimDate (Role-playing: Forecast Generated Date, Forecast Target Date/Week)
- DimProduct (SKU, Category, Product Line)
- DimWarehouse or DimRegion (Planning Territory / Distribution Hub)
- DimCustomerChannel (Sales Channel or Global Total)
- DimScenario (Forecast Version: Statistical Baseline, Consensus Plan, Budget)

### Core Measures
- ForecastedQuantity (Projected unit demand)
- BaselineStatisticalQuantity (Unconstrained algorithmic baseline)
- PlannerAdjustmentQuantity (Manual override delta)
- ForecastValue (ForecastedQuantity * Planned Unit Price)

---

## 5. Inventory Movement Process

### Business Purpose
Records discrete physical movements and stock adjustments inside and between warehouse nodes. This encompasses inter-warehouse balancing transfers, dock-to-shelf put-aways, scrap/spoilage write-offs, cycle count adjustments, and inventory reclassifications.

### Analytical Justification
While snapshots record the *state* of inventory, movements explain *why* inventory changed. Critical for tracking transfer logistics costs, shrinkage/loss rates, damaged goods, and warehouse operational efficiency.

### Business Grain
**One row per physical inventory transfer or adjustment transaction.**

### Core Dimensions
- DimDate (Transaction Timestamp / Date)
- DimProduct (SKU)
- DimWarehouse (Origin Facility for transfers or Adjusting Facility)
- DimWarehouse (Destination Facility for inter-DC transfers)
- DimEmployee (Warehouse Operator / Supervisor)
- DimMovementReason (Transfer, Spoilage, Damage, Cycle Count Correction, Obsolete Write-off)

### Core Measures
- MovementQuantity (Positive for stock increases, negative for decreases)
- MovementValue (MovementQuantity * UnitLandedCost)
- TransferTransitTimeDays (For inter-facility transfers)
- TransferFreightCost (Cost incurred to rebalance stock)

---

## 6. Stockout Incidents Process

### Business Purpose
Tracks explicit stockout occurrences where inventory is exhausted at a facility while active demand exists. Records the inception, duration, and resolution of stockouts, enabling exact tracking of unfulfilled demand, lost revenue, and planner response times.

### Analytical Justification
Deriving stockout metrics solely from snapshots can obscure intra-day outages and misses estimated lost sales volume. Explicit incident tracking allows root-cause attribution (e.g., supplier late delivery, demand surge, warehouse misplacement).

### Business Grain
**One row per stockout event per SKU per Warehouse Facility.**

### Core Dimensions
- DimDate (Stockout Start Date, Stockout Resolved Date)
- DimProduct (SKU, Brand, Category)
- DimWarehouse (Depleted Facility)
- DimCustomerChannel (Impacted customer channel)
- DimStockoutReason (Supplier Delay, Unexpected Demand Surge, Quality Hold, Inaccurate Inventory Record)

### Core Measures
- StockoutDurationDays (Resolved Date - Start Date)
- EstimatedLostUnits (Lost demand during outage window)
- EstimatedLostRevenue (EstimatedLostUnits * UnitPrice)
- ImpactedCustomerOrdersCount (Number of orders stalled or cancelled)

---

## 7. Customer Returns Process

### Business Purpose
Manages reverse logistics when customers return products across retail, wholesale, and e-commerce channels. Tracks receipt, inspection condition, and subsequent disposition (restock to active inventory, scrap, refurbish, or vendor return).

### Analytical Justification
High return rates distort sales velocity, inflate inventory carrying costs, and generate operational overhead. Distinguishing between restockable returns and scrapped returns is essential for accurate net-demand and inventory valuation calculations.

### Business Grain
**One row per returned order line item.**

### Core Dimensions
- DimDate (Return Receipt Date, Original Sale Date)
- DimProduct (Returned SKU)
- DimCustomerChannel (Original Purchasing Channel)
- DimWarehouse (Return Processing Facility)
- DimReturnReason (Defective, Damaged in Transit, Incorrect Item, Customer Remorse)

### Core Measures
- ReturnedQuantity (Total units returned)
- RestockedQuantity (Units returned to active saleable inventory)
- ScrappedQuantity (Units deemed unsaleable and written off)
- RefundAmount (Customer reimbursement)
- ReverseLogisticsCost (Handling, freight, and inspection cost)

---

## 8. Supplier Performance (Evaluated Analytical Process)

### Business Purpose & Analytical Architecture Decision
Tracks vendor compliance over time against contractual SLAs, including delivery timeliness, quantity accuracy, quality defect rates, and lead-time stability.

### Analytical Evaluation & Modeling Decision
- **Evaluation:** Does this require a raw transactional event table? **No.**
- **Architectural Rationale:** Supplier performance is an **analytical consolidation** calculated directly from the Procurement & Inbound Receipts process (FactPurchaseOrder) combined with receiving inspection results.
- **Implementation Approach:** In dbt and BigQuery, supplier performance will be modeled as a conformed analytical aggregate mart (e.g., Monthly Supplier Scorecard) rather than inventing an artificial transactional source. This ensures 100% mathematical reconciliation between operational purchase orders and supplier scorecards.
