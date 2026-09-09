# Enterprise KPI Catalog: Supply Chain & Inventory Optimization Hub

This document defines the formal analytical catalog for all key performance indicators (KPIs) in the Supply Chain & Inventory Optimization Hub. Every KPI includes its business definition, mathematical formulation, unit of measure, analytical grain, additivity behavior, required source data, interpretation guidance, and technical caveats.

---

## Catalog Index

1. [Inventory Value](#1-inventory-value)
2. [Average Inventory](#2-average-inventory)
3. [Inventory Turns (Turnover Ratio)](#3-inventory-turns-turnover-ratio)
4. [Days of Inventory (DOI) / Days of Supply](#4-days-of-inventory-doi--days-of-supply)
5. [Stockout Rate](#5-stockout-rate)
6. [Fill Rate (Order Line Fill Rate)](#6-fill-rate-order-line-fill-rate)
7. [Customer Service Level (Order Complete & On-Time)](#7-customer-service-level-order-complete--on-time)
8. [On-Time In-Full (OTIF) — Supplier & Customer](#8-on-time-in-full-otif--supplier--customer)
9. [Forecast Accuracy](#9-forecast-accuracy)
10. [Forecast Bias](#10-forecast-bias)
11. [Weighted Absolute Percentage Error (WAPE)](#11-weighted-absolute-percentage-error-wape)
12. [Supplier Lead Time](#12-supplier-lead-time)
13. [Lead-Time Variability (Standard Deviation)](#13-lead-time-variability-standard-deviation)
14. [Excess Inventory](#14-excess-inventory)
15. [Dead Stock (Obsolete Inventory)](#15-dead-stock-obsolete-inventory)
16. [Working-Capital Exposure](#16-working-capital-exposure)
17. [Dynamic Safety Stock (SS)](#17-dynamic-safety-stock-ss)
18. [Reorder Point (ROP)](#18-reorder-point-rop)
19. [Inventory Carrying Cost](#19-inventory-carrying-cost)
20. [Backorder Rate](#20-backorder-rate)

---

## 1. Inventory Value

- **Business Definition:** The total monetary worth of on-hand inventory physically present in network warehouses at standard landed cost.
- **Formula:**
  $$\text{Inventory Value} = \sum_{i \in \text{SKUs}} (\text{OnHandQuantity}_i \times \text{UnitLandedCost}_i)$$
- **Unit:** Currency ($ USD).
- **Grain:** SKU / Warehouse / Snapshot Date.
- **Additivity Classification:** **Semi-additive**. Additive across SKUs, categories, warehouses, and regions; non-additive across time (cannot sum Monday through Sunday; must use end-of-period snapshot or average).
- **Required Source Data:**
  - FactInventorySnapshot.OnHandQuantity
  - DimProduct.UnitLandedCost (or snapshot-specific landed cost)
- **Example Interpretation:** An Inventory Value of $12,450,000 for Central DC on June 30 indicates the asset value of physical stock held on the books at month-end.
- **Known Caveats:** Excludes stock in transit unless explicitly marked as FOB shipping point. Distortions occur if standard cost changes without inventory revaluation adjustments.

---

## 2. Average Inventory

- **Business Definition:** The average monetary valuation (or physical unit volume) of inventory held over a defined time interval (month, quarter, or year).
- **Formula:**
  $$\text{Average Inventory Value} = \frac{1}{N} \sum_{t=1}^{N} \text{InventoryValue}_t$$
  *(Where N is the number of daily snapshots in the reporting period).*
- **Unit:** Currency ($ USD) or Physical Units.
- **Grain:** SKU / Warehouse / Reporting Period (Monthly, Quarterly, Annual).
- **Additivity Classification:** **Non-additive across time**; semi-additive across product and location dimensions.
- **Required Source Data:** Daily FactInventorySnapshot records over the evaluation period.
- **Example Interpretation:** An average inventory of $5,000,000 over Q2 vs. an ending inventory of $6,200,000 reveals that stock accumulated toward the end of the quarter.
- **Known Caveats:** Using simple beginning-plus-ending inventory divided by 2 creates severe distortion for seasonal FMCG goods; daily snapshot averaging is mandatory for accuracy.

---

## 3. Inventory Turns (Turnover Ratio)

- **Business Definition:** The number of times the average inventory investment is sold and replaced over an annualized period, indicating inventory velocity and capital productivity.
- **Formula:**
  $$\text{Inventory Turns} = \frac{\text{Cost of Goods Sold (COGS) in Period}}{\text{Average Inventory Value in Period}} \times \left( \frac{365}{\text{Days in Period}} \right)$$
- **Unit:** Ratio (Turns / Year).
- **Grain:** SKU / Category / Warehouse / Region / Period.
- **Additivity Classification:** **Non-additive**. A ratio derived from an additive numerator (COGS) and a non-additive denominator (Average Inventory).
- **Required Source Data:**
  - FactSales.ShippedQuantity * DimProduct.UnitStandardCost (COGS)
  - Daily FactInventorySnapshot.InventoryValue
  - DimDate.DaysInPeriod
- **Example Interpretation:** An annualized turn rate of 8.5 means the inventory cycles 8.5 times per year (~every 43 days). A turn rate < 2 indicates high risk of stagnant stock.
- **Known Caveats:** Never divide Sales Revenue by Inventory Value, as this mixes retail selling price with cost-basis inventory, artificially inflating turns.

---

## 4. Days of Inventory (DOI) / Days of Supply

- **Business Definition:** The estimated number of days the current on-hand inventory will last based on historical or projected daily consumption.
- **Formula (Historical COGS method):**
  $$\text{DOI} = \frac{\text{Current Inventory Value}}{\text{Annualized COGS} / 365} = \frac{\text{Current Inventory Value}}{\text{Average Daily COGS (Trailing 90 Days)}}$$
  *Alternative (Forward Demand method):* Units on Hand / Average Forecasted Daily Demand.
- **Unit:** Days.
- **Grain:** SKU / Warehouse / Snapshot Date.
- **Additivity Classification:** **Non-additive**.
- **Required Source Data:**
  - FactInventorySnapshot.OnHandQuantity / InventoryValue
  - FactSales.CostOfGoodsSold (trailing 30/60/90 days) or FactForecast.ForecastedQuantity
- **Example Interpretation:** A DOI of 120 days for a consumer electronics SKU with a 30-day supplier lead time indicates substantial overstocking.
- **Known Caveats:** If a product had zero sales in the trailing period, daily COGS is zero, leading to division-by-zero errors. System must cap or handle zero demand explicitly (e.g., flag as Infinite/Inactive).

---

## 5. Stockout Rate

- **Business Definition:** The proportion of time (or active SKU catalog) where inventory is depleted to zero, preventing customer order fulfillment.
- **Formula (Time-based across days):**
  $$\text{Stockout Rate (Time)} = \frac{\sum \text{Stockout Days in Period}}{\text{Total Active SKU-Warehouse Days in Period}} \times 100\%$$
  *Catalog-based on a single day:*
  $$\text{Stockout Rate (Catalog)} = \frac{\text{Count of Active SKUs with AvailableQuantity} = 0}{\text{Total Active Catalog SKUs}} \times 100\%$$
- **Unit:** Percentage (%).
- **Grain:** SKU / Category / Warehouse / Period.
- **Additivity Classification:** **Non-additive**.
- **Required Source Data:**
  - FactInventorySnapshot.AvailableQuantity
  - FactStockout.StockoutDurationDays
- **Example Interpretation:** A stockout rate of 4.2% across beverage SKUs means that on average, 4.2% of catalog items were unavailable for dispatch on any given day.
- **Known Caveats:** Must be restricted to active commercial SKUs; discontinued or phased-out products with zero stock must be filtered out to prevent artificial inflation.

---

## 6. Fill Rate (Order Line Fill Rate)

- **Business Definition:** The percentage of customer-ordered unit volume that is immediately fulfilled from available inventory without delay or backorders.
- **Formula:**
  $$\text{Fill Rate} = \frac{\sum \text{ShippedQuantity}}{\sum \text{OrderedQuantity}} \times 100\%$$
- **Unit:** Percentage (%).
- **Grain:** Order Line; aggregated by SKU, Customer Channel, Warehouse, Period.
- **Additivity Classification:** **Non-additive ratio** (calculated as SUM(ShippedQuantity) / SUM(OrderedQuantity)).
- **Required Source Data:**
  - FactSales.ShippedQuantity
  - FactSales.OrderedQuantity
- **Example Interpretation:** A fill rate of 97.5% indicates that out of 10,000 units ordered by retail accounts, 9,750 units were shipped on schedule.
- **Known Caveats:** Fill rate measures unit volume; a company could have a 99% unit fill rate while still failing 20% of customer purchase orders if single low-volume lines are missed.

---

## 7. Customer Service Level (Order Complete & On-Time)

- **Business Definition:** The percentage of complete customer orders delivered without stockouts, shortages, or delivery delays.
- **Formula:**
  $$\text{Customer Service Level} = \frac{\text{Count of Orders Fulfilled 100\% In-Full and Delivered On-Time}}{\text{Total Customer Orders Placed}} \times 100\%$$
- **Unit:** Percentage (%).
- **Grain:** Sales Order Header / Aggregated by Customer Channel, Region, Period.
- **Additivity Classification:** **Non-additive**.
- **Required Source Data:** FactSales (Order Status, Promised Date, Actual Delivery Date, Line fulfillment status).
- **Example Interpretation:** A 94.0% service level against a contractual SLA target of 96.0% highlights customer relationship vulnerability and potential contractual penalties.
- **Known Caveats:** An order is deemed failed if even 1 unit of a 50-line order is omitted or arrives 1 day late (Order OTIF).

---

## 8. On-Time In-Full (OTIF) — Supplier & Customer

- **Business Definition:**
  - **Supplier Inbound OTIF:** Percentage of inbound purchase order deliveries received on or before the contract promised date with 100% of ordered quantities intact.
  - **Customer Outbound OTIF:** Percentage of customer shipments delivered to customer dock on time and in full.
- **Formula (Supplier OTIF):**
  $$\text{Supplier OTIF} = \frac{\sum \text{PO Lines Delivered On-Time AND In-Full}}{\text{Total Scheduled PO Lines}} \times 100\%$$
  *Where:* On-Time = ActualDockReceiptDate <= PromisedDeliveryDate; In-Full = ReceivedQuantity >= OrderedQuantity * (1 - Tolerance).
- **Unit:** Percentage (%).
- **Grain:** PO Line / Aggregated by Supplier, Product Category, Receiving DC, Period.
- **Additivity Classification:** **Non-additive**.
- **Required Source Data:**
  - FactPurchaseOrder.PromisedDeliveryDate, ActualDockReceiptDate, OrderedQuantity, ReceivedQuantity.
- **Example Interpretation:** A supplier with 82% OTIF generates stockout risk and forces the warehouse to carry excessive buffer stock.
- **Known Caveats:** Early delivery should not automatically be rewarded if it congests warehouse dock capacity; strict enterprise OTIF rules specify an acceptable window (e.g., -2 days to 0 days).

---

## 9. Forecast Accuracy

- **Business Definition:** The degree of agreement between forecasted demand and actual customer demand over an evaluated planning period.
- **Formula (WAPE-derived):**
  $$\text{Forecast Accuracy} = \max\left(0, 1 - \frac{\sum_{i} |\text{ActualDemand}_i - \text{ForecastDemand}_i|}{\sum_{i} \text{ActualDemand}_i}\right) \times 100\%$$
- **Unit:** Percentage (%).
- **Grain:** SKU / Category / Warehouse / Region / Forecast Period.
- **Additivity Classification:** **Non-additive**.
- **Required Source Data:**
  - FactForecast.ForecastedQuantity
  - FactSales.ShippedQuantity (or unconstrained demand: Shipped + Lost Sales)
- **Example Interpretation:** 84% forecast accuracy indicates that aggregate error across products accounted for 16% of demand volume.
- **Known Caveats:** Using standard MAPE (Mean Absolute Percentage Error) creates mathematical division-by-zero on slow-moving items with zero sales; WAPE-derived accuracy avoids this flaw.

---

## 10. Forecast Bias

- **Business Definition:** The persistent directional tendency of a forecast to systematically over-predict or under-predict actual demand.
- **Formula:**
  $$\text{Forecast Bias (%)} = \frac{\sum_{i} (\text{ForecastDemand}_i - \text{ActualDemand}_i)}{\sum_{i} \text{ActualDemand}_i} \times 100\%$$
- **Unit:** Percentage (%) with algebraic sign (+ / -).
- **Grain:** SKU / Product Category / Region / Planning Period.
- **Additivity Classification:** **Non-additive**.
- **Required Source Data:** FactForecast.ForecastedQuantity, FactSales.ShippedQuantity.
- **Example Interpretation:** A bias of +14% indicates systematic over-forecasting (leading to overstock and cash lockup); a bias of -18% indicates chronic under-forecasting (driving stockouts).
- **Known Caveats:** Positive and negative errors across individual SKUs can cancel out at high aggregation levels, making a portfolio appear unbiased when individual SKUs are erratic. Bias must be monitored at subcategory and SKU grain.

---

## 11. Weighted Absolute Percentage Error (WAPE)

- **Business Definition:** Volume-weighted absolute forecast error, expressing the magnitude of error as a percentage of total actual volume.
- **Formula:**
  $$\text{WAPE} = \frac{\sum_{i} |\text{ActualDemand}_i - \text{ForecastDemand}_i|}{\sum_{i} \text{ActualDemand}_i} \times 100\%$$
- **Unit:** Percentage (%).
- **Grain:** SKU / Category / Region / Planning Cycle.
- **Additivity Classification:** **Non-additive**.
- **Required Source Data:** Paired records of FactForecast and FactSales by SKU-Warehouse-Period.
- **Example Interpretation:** A WAPE of 15.4% across the Dairy category indicates tight alignment, whereas a 42% WAPE in Personal Care signals erratic demand or promotional planning failure.
- **Known Caveats:** Highly sensitive to outlier promotion periods if promotional lift was not recorded in the baseline forecast.

---

## 12. Supplier Lead Time

- **Business Definition:** The elapsed calendar duration from purchase order placement until the physical goods arrive at the distribution center dock and pass receiving inspection.
- **Formula:**
  $$\text{Lead Time (Days)} = \text{ActualDockReceiptDate} - \text{POCreationDate}$$
  *Average Lead Time over Period:*
  $$\overline{\text{Lead Time}} = \frac{1}{M} \sum_{j=1}^{M} \text{Lead Time}_j$$
- **Unit:** Days.
- **Grain:** PO Line Item; aggregated by Supplier, Warehouse, Month.
- **Additivity Classification:** **Non-additive**.
- **Required Source Data:**
  - FactPurchaseOrder.POCreationDate
  - FactPurchaseOrder.ActualDockReceiptDate
- **Example Interpretation:** An average lead time of 42 days from an overseas supplier compared to a 14-day lead time from a domestic vendor informs replenishment frequency and pipeline commitment.
- **Known Caveats:** Excludes internal dock-to-stock putaway time unless dock receipt timestamps are formally separated from ERP release timestamps.

---

## 13. Lead-Time Variability (Standard Deviation)

- **Business Definition:** The statistical dispersion and unpredictability of supplier lead times around their historical average.
- **Formula:**
  $$\sigma_{LT} = \sqrt{\frac{1}{M - 1} \sum_{j=1}^{M} (\text{Lead Time}_j - \overline{\text{Lead Time}})^2}$$
- **Unit:** Days.
- **Grain:** Supplier / SKU / Purchasing Route over trailing 90–180 days.
- **Additivity Classification:** **Non-additive**.
- **Required Source Data:** Historical FactPurchaseOrder lead-time observations.
- **Example Interpretation:** A supplier with a 20-day mean lead time and standard deviation of 8 days requires dramatically higher safety stock than a supplier with a 22-day mean lead time and standard deviation of 1 day.
- **Known Caveats:** Requires a minimum sample size (M >= 10 receipts) to be statistically valid; new vendors must use contractual proxy assumptions.

---

## 14. Excess Inventory

- **Business Definition:** The portion of physical stock currently on hand that exceeds the upper control boundary defined by planned cycle stock, safety stock, and demand over lead time.
- **Formula:**
  $$\text{Excess Units}_i = \max\left(0, \text{OnHandQuantity}_i - (\text{SafetyStock}_i + \text{CycleStock}_i + \text{LeadTimeDemand}_i)\right)$$
  $$\text{Excess Inventory Value} = \sum_{i} (\text{Excess Units}_i \times \text{UnitLandedCost}_i)$$
- **Unit:** Units and Currency ($ USD).
- **Grain:** SKU / Warehouse / Snapshot Date.
- **Additivity Classification:** **Semi-additive**.
- **Required Source Data:**
  - FactInventorySnapshot.OnHandQuantity
  - Replenishment parameters (SafetyStock, LeadTimeDemand)
  - DimProduct.UnitLandedCost
- **Example Interpretation:** $1,800,000 in excess inventory across Frozen Goods flags an urgent need to throttle incoming POs or launch promotional markdown campaigns.
- **Known Caveats:** Parameter-sensitive: if safety stock is set artificially high, excess inventory will be masked.

---

## 15. Dead Stock (Obsolete Inventory)

- **Business Definition:** Unsaleable or stagnant inventory sitting in warehouse storage that has had zero customer sales, outward shipments, or movement over a predefined aging horizon (e.g., 90, 180, or 360 days).
- **Formula:**
  $$\text{Dead Stock Value} = \sum_{i \in \text{Stagnant SKUs}} (\text{OnHandQuantity}_i \times \text{UnitLandedCost}_i)$$
  *Condition for Stagnant SKU:* Days Since Last Sale / Movement >= 180 Days.
- **Unit:** Currency ($ USD).
- **Grain:** SKU / Warehouse / Snapshot Date.
- **Additivity Classification:** **Semi-additive**.
- **Required Source Data:**
  - FactInventorySnapshot.OnHandQuantity
  - FactSales.ShipDate (most recent occurrence)
  - DimProduct.UnitLandedCost
- **Example Interpretation:** $450,000 of inventory with zero movement in 180+ days represents capital write-off exposure and consumes valuable rack space.
- **Known Caveats:** Seasonal goods (e.g., winter apparel held during summer) will appear dead unless filtered by seasonal catalog flags.

---

## 16. Working-Capital Exposure

- **Business Definition:** Total financial capital locked into unproductive or high-risk inventory assets across the enterprise, representing the sum of excess stock, dead stock, and committed inbound orders for overstocked SKUs.
- **Formula:**
  $$\text{Working-Capital Exposure} = \text{Excess Inventory Value} + \text{Dead Stock Value} + \text{Committed Inbound PO Spend on Excess SKUs}$$
- **Unit:** Currency ($ USD).
- **Grain:** SKU / Category / Warehouse / Region / Snapshot Date.
- **Additivity Classification:** **Semi-additive**.
- **Required Source Data:**
  - FactInventorySnapshot
  - FactPurchaseOrder (Open/in-transit quantities on overstocked SKUs)
  - DimProduct.UnitLandedCost
- **Example Interpretation:** A working-capital exposure of $3,800,000 alerts the VP of Operations that near-term cash flow can be liberated by canceling/delaying open POs and liquidating stagnant inventory.
- **Known Caveats:** Avoid double-counting SKUs that are simultaneously categorized as dead and excess.

---

## 17. Dynamic Safety Stock (SS)

- **Business Definition:** Scientifically calculated buffer stock maintained to mitigate the combined statistical uncertainty of customer demand surges and supplier lead-time fluctuations during replenishment.
- **Formula (King\'s Combined Uncertainty Model):**
  $$SS = Z \times \sqrt{\left(\overline{LT} \times \sigma_D^2\right) + \left(\overline{D}^2 \times \sigma_{LT}^2\right)}$$
  *Where:*
  - Z = Service-level Z-factor (e.g., 1.645 for 95%, 2.054 for 98%, 2.326 for 99%)
  - Average LT = Average supplier lead time (in days)
  - Sigma D = Standard deviation of daily demand
  - Average D = Average daily demand
  - Sigma LT = Standard deviation of supplier lead time (in days)
- **Unit:** Units.
- **Grain:** SKU / Warehouse Facility.
- **Additivity Classification:** **Non-additive**.
- **Required Source Data:** Daily sales history (FactSales), PO delivery history (FactPurchaseOrder).
- **Example Interpretation:** For a high-velocity SKU with Z=2.054 (98% SLA), Average LT=14, Sigma D=25, Average D=100, and Sigma LT=3, SS = 2.054 * sqrt((14 * 625) + (10000 * 9)) = 645 units.
- **Known Caveats:** Assumes independent demand and lead-time distributions. If lead time is fixed (Sigma LT=0), simplifies to Z * Sigma D * sqrt(LT).

---

## 18. Reorder Point (ROP)

- **Business Definition:** The inventory threshold that triggers a replenishment purchase order to prevent stockout before inbound goods arrive.
- **Formula:**
  $$\text{ROP} = (\overline{D} \times \overline{LT}) + SS$$
  *Trigger Rule:* If Net Inventory (OnHand + OnOrder - Reserved) <= ROP, generate replenishment purchase requisition.
- **Unit:** Units.
- **Grain:** SKU / Warehouse Facility.
- **Additivity Classification:** **Non-additive**.
- **Required Source Data:** Average daily demand, average lead time, dynamic safety stock.
- **Example Interpretation:** An ROP of 2,045 units means that as soon as net effective inventory drops to 2,045, a purchase order must be placed immediately.
- **Known Caveats:** Must evaluate net available stock (including stock on open POs) to prevent duplicate daily reorder triggers.

---

## 19. Inventory Carrying Cost

- **Business Definition:** The total annual cost incurred to maintain and hold inventory in storage, encompassing opportunity cost of capital, physical warehousing, insurance, handling, taxation, shrinkage, and obsolescence.
- **Formula:**
  $$\text{Carrying Cost} = \text{Average Inventory Value} \times \text{Annual Carrying Cost Rate (%)}$$
  *Typical FMCG Carrying Cost Rate:* 20% - 25% per annum.
- **Unit:** Currency ($ USD / Year).
- **Grain:** Warehouse / Category / Region / Fiscal Period.
- **Additivity Classification:** **Semi-additive** across entities; non-additive over time.
- **Required Source Data:** Daily FactInventorySnapshot.InventoryValue, Corporate Holding Cost Policy Parameter (e.g., 22%).
- **Example Interpretation:** Carrying $10,000,000 in average inventory at a 22% holding rate costs the enterprise $2,200,000 annually in pure carrying overhead.
- **Known Caveats:** Carrying cost rate must be treated as a scenario-parameterized assumption rather than a static hardcoded number.

---

## 20. Backorder Rate

- **Business Definition:** The percentage of total customer demand units that cannot be immediately fulfilled from stock and must be placed on backorder for future delivery.
- **Formula:**
  $$\text{Backorder Rate} = \frac{\sum \text{Backordered Units}}{\sum \text{Total Ordered Units}} \times 100\%$$
- **Unit:** Percentage (%).
- **Grain:** SKU / Customer Channel / Warehouse / Period.
- **Additivity Classification:** **Non-additive**.
- **Required Source Data:** FactSales.OrderedQuantity, FactSales.ShippedQuantity.
- **Example Interpretation:** A backorder rate of 3.8% indicates demand deferred into future delivery cycles, jeopardizing customer retention and causing split-shipment costs.
- **Known Caveats:** In wholesale channels, backorders are often accepted; in retail e-commerce, unfulfilled orders often result in instant cancellation rather than backorder.\n