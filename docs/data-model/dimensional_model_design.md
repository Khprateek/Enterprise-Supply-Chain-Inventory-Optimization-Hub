# Kimball Dimensional Model Design: Enterprise Supply Chain & Inventory Optimization Hub

## 1. Executive Summary & Design Principles
This document establishes the formal Kimball dimensional architecture for the Enterprise Supply Chain & Inventory Optimization Hub. The model translates operational supply-chain events into a conformed, high-performance Star Schema optimized for Google BigQuery and Power BI Desktop VertiPaq execution.

Core architecture rules:
1. **Explicit Business Grain:** Every fact table models a single business process at a declared atomic grain.
2. **Conformed Dimensions:** Standardized dimensions shared across fact tables enable cross-process correlation and drill-through.
3. **Surrogate Keys:** Integer surrogate keys (`INT64`) are used for all dimensional joins, decoupling the warehouse from operational system key formats and supporting SCD Type 2 tracking.
4. **Single-Direction Filter Flow:** Pure Star Schema with 1-to-many, single-direction relationships to prevent ambiguous filter propagation and maximize compression.

---

## 2. Business-Process Fact Table Grains (STEP 1)

Each fact table corresponds to an authentic business process evaluated for analytical value:

| Fact Table | Business Process Modeled | Fact Classification | Declared Business Grain | Additivity Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **`FactSales`** | Outbound customer sales order fulfillment. | Transactional Fact | **One row per fulfilled sales order line item.** | Fully additive (`Quantity`, `NetSalesAmount`, `COGS`, `DiscountAmount`). |
| **`FactInventorySnapshot`** | Daily physical warehouse inventory balance. | Periodic Snapshot Fact | **One row per SKU ? Warehouse ? Snapshot Date.** | Semi-additive across time; fully additive across products and facilities (`OnHandQuantity`, `ReservedQuantity`, `AvailableQuantity`, `InventoryValuation`). |
| **`FactPurchaseOrder`** | Inbound supplier procurement lifecycle. | Accumulating / Transactional Fact | **One row per Purchase Order line item.** | Fully additive quantities and spend; non-additive lead-time days and cycle times. |
| **`FactDemandForecast`** | Forward-looking demand planning and consensus forecasts. | Periodic Snapshot Fact | **One row per SKU ? Warehouse/Region ? Forecast Generation Date ? Target Horizon Period.** | Additive within a target period across SKUs and locations (`ForecastQuantity`, `ForecastRevenue`); non-additive across forecast versions. |
| **`FactInventoryMovement`** | Inter-facility transfers, cycle count adjustments, and scrappage. | Transactional Event Fact | **One row per discrete physical inventory movement or adjustment event.** | Fully additive (`MovementQuantity`, `MovementValue`, `FreightCost`). |
| **`FactStockout`** | Consolidated stockout outage episodes. | Derived Event / Incident Fact | **One row per consolidated continuous stockout outage event per SKU ? Warehouse.** | Additive across events (`DurationDays`, `EstimatedLostDemandUnits`, `EstimatedLostRevenueAmount`). |
| **`FactCustomerReturns`** | Customer reverse logistics, inspection, and disposition. | Transactional Fact | **One row per returned customer order line item.** | Fully additive (`ReturnedQuantity`, `RestockedQuantity`, `ScrappedQuantity`, `RefundAmount`). |
| **`FactSupplierMonthlyPerformance`** | Monthly vendor scorecard and contract SLA compliance. | Materialized Analytical Mart | **One row per Supplier ? Month.** | Semi-additive / Non-additive ratios and statistical metrics (`OTIFRatePct`, `AverageLeadTimeDays`, `LeadTimeStdDevDays`, `LineFillRatePct`). |

---

## 3. Conformed Dimension Design (STEP 2)

### 3.1 `DimDate` (Calendar & Fiscal Dimension)
- **Business Key:** `FullDate` (DATE: `YYYY-MM-DD`).
- **Surrogate Key:** `DateKey` (INT64: `YYYYMMDD`, e.g., `20260910`).
- **Attributes:** `DayOfWeek`, `DayName`, `DayOfMonth`, `DayOfYear`, `WeekOfYear`, `MonthNumber`, `MonthName`, `QuarterNumber`, `QuarterName`, `YearNumber`, `FiscalMonthNumber`, `FiscalQuarter`, `FiscalYear`, `IsWeekday`, `IsHoliday`, `SeasonalityPeriod`.
- **Hierarchies:** 
  - Calendar: `Year` -> `Quarter` -> `Month` -> `Week` -> `Date`
  - Fiscal: `FiscalYear` -> `FiscalQuarter` -> `FiscalMonth` -> `Date`
- **SCD Strategy:** **SCD Type 0** (Static calendar dimension, pre-populated for 2020?2030).

### 3.2 `DimProduct` (Master Catalog & Merchandising Dimension)
- **Business Key:** `ProductSKU` (VARCHAR, e.g., `'SKU-10492'`).
- **Surrogate Key:** `ProductKey` (INT64, deterministic sequence or hash).
- **Attributes:** `ProductName`, `BrandName`, `CategoryName`, `SubcategoryName`, `DepartmentName`, `UnitStandardCost`, `UnitListPrice`, `HandlingProfile` (Standard, Perishable, Hazardous, Fragile, Bulk), `StorageClass`, `WeightKg`, `VolumeCubicMeters`, `PrimarySupplierCode`, `ABCClassification`, `XYZClassification`.
- **Hierarchies:** `Department` -> `Category` -> `Subcategory` -> `Brand` -> `ProductSKU`.
- **SCD Strategy:** **SCD Type 2** (Tracks historical changes in unit cost, merchandising classification, and primary supplier over time).

### 3.3 `DimSupplier` (Vendor & Sourcing Dimension)
- **Business Key:** `SupplierCode` (VARCHAR, e.g., `'SUP-0042'`).
- **Surrogate Key:** `SupplierKey` (INT64).
- **Attributes:** `SupplierName`, `Country`, `City`, `RegionZone`, `SupplierTier` (Tier 1 Strategic, Tier 2 Preferred, Tier 3 Tactical), `ContractLeadTimeDays`, `PaymentTermsDays`, `MinimumOrderQuantity`, `PreferredStatusFlag`, `RiskRatingTier`.
- **Hierarchies:** `Country` -> `SupplierTier` -> `SupplierName`.
- **SCD Strategy:** **SCD Type 1** (Master attributes updated in place; historical PO delivery facts maintain historical transaction-time performance).

### 3.4 `DimWarehouse` (Facility & Distribution Center Dimension)
- **Business Key:** `WarehouseCode` (VARCHAR, e.g., `'DC-CENTRAL-01'`).
- **Surrogate Key:** `WarehouseKey` (INT64).
- **Attributes:** `WarehouseName`, `RegionKey` (Foreign Key to `DimRegion`), `FacilityType` (Central Distribution Center, Regional Distribution Center, Retail Hub, E-Commerce Fulfillment), `StorageCapacityPallets`, `TotalAreaSqM`, `RefrigeratedCapacityPallets`, `OperatingHoursPerWeek`, `ActiveFlag`.
- **Hierarchies:** `Region` -> `FacilityType` -> `WarehouseName`.
- **SCD Strategy:** **SCD Type 1**.

### 3.5 `DimRegion` (Geographic & Operating Market Dimension)
- **Business Key:** `RegionCode` (VARCHAR, e.g., `'REG-NA-EAST'`).
- **Surrogate Key:** `RegionKey` (INT64).
- **Attributes:** `RegionName`, `Theater` (Americas, EMEA, APAC), `PrimaryCountry`, `CurrencyCode`, `RegionalDirectorName`, `TimeZone`.
- **Hierarchies:** `Theater` -> `PrimaryCountry` -> `RegionName`.
- **SCD Strategy:** **SCD Type 1**.

### 3.6 `DimCustomerChannel` (Commercial Demand Channel Dimension)
- **Business Key:** `ChannelCustomerCode` (VARCHAR, e.g., `'CH-WS-00192'`).
- **Surrogate Key:** `CustomerChannelKey` (INT64).
- **Attributes:** `ChannelName` (Wholesale Distributor, Retail Big-Box, E-Commerce Direct), `CustomerAccountName`, `CustomerSegment` (Tier 1 Key Account, Regional Chain, Independent Merchant, Direct Consumer), `PaymentCreditTerms`, `DeliveryPriorityTier`.
- **Hierarchies:** `ChannelName` -> `CustomerSegment` -> `CustomerAccountName`.
- **SCD Strategy:** **SCD Type 1**.

### 3.7 `DimEmployeePlanner` (Supply Chain Planner Dimension)
- **Business Key:** `EmployeeNumber` (VARCHAR, e.g., `'EMP-5091'`).
- **Surrogate Key:** `PlannerKey` (INT64).
- **Attributes:** `PlannerName`, `EmailAddress`, `JobRole` (VP Operations, Regional Supply Planner, Warehouse Planner, Procurement Manager, Supply Chain Analyst), `Department`, `AssignedRegionCode`, `AssignedCategoryGroup`.
- **Hierarchies:** `Department` -> `JobRole` -> `PlannerName`.
- **SCD Strategy:** **SCD Type 1**.

### 3.8 `DimScenario` (Simulation & What-If Parameter Dimension)
- **Business Key:** `ScenarioCode` (VARCHAR, e.g., `'SCN-BASE'`).
- **Surrogate Key:** `ScenarioKey` (INT64).
- **Attributes:** `ScenarioName` (Baseline Actuals, Stretch Growth +10%, Port Disruption +7d Lead Time, High Service Target 98%), `Description`, `DemandMultiplier`, `LeadTimeShockDays`, `ServiceLevelTargetPct`, `AnnualCarryingCostRatePct`.
- **SCD Strategy:** **SCD Type 0** (Static parameter reference model).

---

## 4. Role-Playing Date Dimensions Strategy (STEP 3)

### The Architectural Problem
In supply chain data warehousing, single fact records frequently reference multiple milestone dates. For example:
- `FactSales`: `OrderDate`, `ShipDate`, `DeliveryDate`.
- `FactPurchaseOrder`: `POCreationDate`, `PromisedDeliveryDate`, `ActualDockReceiptDate`.
- `FactStockout`: `StartDate`, `EndDate`.
- `FactCustomerReturns`: `ReturnDate`, `OriginalOrderDate`.

If a physical model creates multiple active relationships between a single fact table and `DimDate`, Power BI and relational query engines encounter **ambiguous join paths**, causing queries to fail or produce cartesian products.

### The Approved Kimball Solution
We implement an enterprise role-playing date architecture:

```
                  ????????????????????????
                  ?       DimDate        ?
                  ? (Single Conformed)   ?
                  ????????????????????????
                             ?
     ?????????????????????????????????????????????????
     ? Active Relationship   ? Inactive (USEREL)     ? Inactive (USEREL)
     ?                       ?                       ?
[OrderDateKey]         [ShipDateKey]          [DeliveryDateKey]
  (Primary)            (Secondary)             (Tertiary)
     ?                       ?                       ?
     ?????????????????????????????????????????????????
                             ?
                  ????????????????????????
                  ?      FactSales       ?
                  ????????????????????????
```

1. **Primary Active Relationship:** Exactly one primary milestone date per fact table is wired as an **Active** relationship to `DimDate`:
   - `FactSales`: `OrderDateKey` -> `DimDate.DateKey` (Active)
   - `FactInventorySnapshot`: `SnapshotDateKey` -> `DimDate.DateKey` (Active)
   - `FactPurchaseOrder`: `POCreationDateKey` -> `DimDate.DateKey` (Active)
   - `FactDemandForecast`: `TargetPeriodDateKey` -> `DimDate.DateKey` (Active)
   - `FactInventoryMovement`: `MovementDateKey` -> `DimDate.DateKey` (Active)
   - `FactStockout`: `StartDateKey` -> `DimDate.DateKey` (Active)
   - `FactCustomerReturns`: `ReturnDateKey` -> `DimDate.DateKey` (Active)
   - `FactSupplierMonthlyPerformance`: `YearMonthDateKey` -> `DimDate.DateKey` (Active)

2. **Secondary Inactive Relationships:** Secondary dates are linked to `DimDate.DateKey` via **Inactive** relationships and activated explicitly in DAX business measures using `USERELATIONSHIP()`:
   ```dax
   // Example: Sales fulfilled based on physical Ship Date
   Sales Shipped Amount = 
   CALCULATE(
       [Net Sales Amount],
       USERELATIONSHIP(FactSales[ShipDateKey], DimDate[DateKey])
   )

   // Example: Inbound PO receipts evaluated by Dock Receipt Date
   Inbound Received Spend = 
   CALCULATE(
       [Total PO Received Spend],
       USERELATIONSHIP(FactPurchaseOrder[ActualDockReceiptDateKey], DimDate[DateKey])
   )
   ```

3. **Explicit Date Role Views (When Parallel Slicing is Mandated):**
   If report users require simultaneous slicing by Order Year and Delivery Year in the same visual matrix, dedicated role-playing views (`DimPromisedDeliveryDate`, `DimShipDate`) are materialized as thin SQL views referencing `DimDate`.

---

## 5. Slowly Changing Dimension (SCD) Type 2 Strategy (STEP 4)

### Target Dimension: `DimProduct`
`DimProduct` is designated as the primary SCD Type 2 dimension in accordance with [ADR-008](../decisions/ADR-008-scd-type-2-dimension-strategy.md).

### Business Justification
In retail and FMCG:
1. **Landed Standard Cost Revisions:** Standard unit costs change periodically due to freight rate fluctuations and supplier renegotiations. Overwriting standard costs (SCD 1) retroactively recalculates historical inventory asset values and historical COGS, corrupting financial reporting.
2. **Merchandising Realignments:** Products are frequently reclassified into new subcategories or brand portfolios. SCD 2 enables "As-Was" historical category analysis alongside "As-Is" current brand management.
3. **Primary Sourcing Reassignments:** Reallocating an SKU to a new primary vendor must preserve the historical vendor relationship for past performance scorecards.

### SCD Type 2 Schema Design for `DimProduct`
```sql
CREATE TABLE DimProduct (
    ProductKey          INT64 NOT NULL,         -- Surrogate Key (Primary Key)
    ProductSKU          STRING NOT NULL,        -- Natural / Business Key
    ProductName         STRING NOT NULL,
    BrandName           STRING NOT NULL,
    CategoryName        STRING NOT NULL,
    SubcategoryName     STRING NOT NULL,
    DepartmentName      STRING NOT NULL,
    UnitStandardCost    NUMERIC(10, 2) NOT NULL,-- Tracked SCD2 attribute
    UnitListPrice       NUMERIC(10, 2) NOT NULL,
    HandlingProfile     STRING NOT NULL,
    PrimarySupplierCode STRING NOT NULL,        -- Tracked SCD2 attribute
    
    -- Temporal Tracking Metadata
    EffectiveFrom       DATE NOT NULL,          -- Inclusive start date of validity
    EffectiveTo         DATE NOT NULL,          -- Exclusive expiry date (or '9999-12-31')
    IsCurrent           BOOLEAN NOT NULL        -- TRUE for current active record; FALSE for historical
);
```

### Fact Table Binding Rule
During ETL / dbt execution, fact tables join to `DimProduct` on `ProductSKU` where the transaction date falls within the temporal validity window:
```sql
SELECT
    f.TransactionID,
    f.OrderDate,
    p.ProductKey,      -- Specific version surrogate key
    f.Quantity,
    f.Quantity * p.UnitStandardCost AS HistoricalCOGS
FROM staging_sales f
JOIN DimProduct p
  ON f.ProductSKU = p.ProductSKU
 AND f.OrderDate >= p.EffectiveFrom
 AND f.OrderDate <  p.EffectiveTo;
```

---

## 6. Many-to-Many Relationships Evaluation (STEP 5)

We evaluate three potential many-to-many relationships in the supply chain domain to determine if a bridge table is genuinely justified:

### 6.1 Evaluation 1: Product ? Supplier
- **Business Reality:** In a multi-regional supply chain, a product can be supplied by multiple qualified vendors (dual-sourcing / multi-sourcing), and a single vendor supplies thousands of products.
- **Transactional Fact Handling:** In actual procurement execution (`FactPurchaseOrder`), every individual PO line item has **exactly one supplier** and **exactly one product**. The transactional fact is a pure 1-to-many relationship (`DimSupplier` 1:N `FactPurchaseOrder` N:1 `DimProduct`).
- **Sourcing Authorization Catalog:** Does the business need to analyze authorized sourcing availability independent of purchase orders?
  - *Decision:* We introduce an optional reference bridge table: **`BridgeProductSupplier`** (`ProductSKU`, `SupplierKey`, `IsPrimaryVendor`, `ContractAllocationSharePct`).
  - *Constraint:* This bridge table is strictly for procurement risk analysis (identifying single-sourced vs. dual-sourced SKUs). It is **not** placed in the query path between core fact tables and dimensions, preserving pure star-schema performance.

### 6.2 Evaluation 2: Product ? Planner
- **Business Reality:** Planners are assigned to product categories, brands, or regional warehouse groups.
- **Evaluation:** In enterprise retail/FMCG, replenishment planning responsibilities follow a clean hierarchical delegation: each product category or brand is assigned to exactly one primary category planner.
- **Decision:** **Bridge Table Rejected.** Modeled as a direct 1-to-many hierarchy in `DimProduct` (`CategoryPlannerKey`) or via `DimEmployeePlanner` assigned to category groups.

### 6.3 Evaluation 3: Warehouse ? Region
- **Business Reality:** Every physical warehouse is geographically situated in exactly one operating region.
- **Decision:** **Bridge Table Rejected.** A warehouse facility cannot exist in multiple regions simultaneously. Modeled as a strict 1-to-many physical hierarchy (`DimRegion.RegionKey` as a parent attribute in `DimWarehouse`).
