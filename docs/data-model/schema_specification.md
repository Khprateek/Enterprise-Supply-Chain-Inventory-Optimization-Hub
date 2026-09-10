# Schema Specification: Enterprise Supply Chain & Inventory Optimization Hub

This document defines the complete physical and logical schema specifications for all tables in the Kimball dimensional model, including table types, declared business grains, primary/foreign keys, key columns, and expected row counts.

---

## 1. Conformed Dimension Tables

### 1.1 `DimDate`
- **Table Type:** Conformed Dimension (SCD Type 0 - Static Calendar).
- **Grain:** One row per calendar day.
- **Primary Key:** `DateKey` (INT64, Format: `YYYYMMDD`).
- **Foreign Keys:** None.
- **Expected Cardinality:** ~3,653 rows (10 calendar years: 2020-01-01 to 2029-12-31).
- **Important Columns:**
  - `DateKey` (INT64, PK)
  - `FullDate` (DATE, Unique)
  - `DayOfWeek` (INT64, 1=Sunday .. 7=Saturday)
  - `DayName` (STRING, 'Monday'..'Sunday')
  - `DayOfMonth` (INT64, 1..31)
  - `DayOfYear` (INT64, 1..366)
  - `WeekOfYear` (INT64, 1..53)
  - `MonthNumber` (INT64, 1..12)
  - `MonthName` (STRING, 'January'..'December')
  - `MonthYear` (STRING, '2026-01')
  - `QuarterNumber` (INT64, 1..4)
  - `QuarterName` (STRING, 'Q1'..'Q4')
  - `YearNumber` (INT64, 2020..2029)
  - `FiscalMonthNumber` (INT64, 1..12)
  - `FiscalQuarter` (STRING, 'FQ1'..'FQ4')
  - `FiscalYear` (INT64, 2020..2029)
  - `IsWeekday` (BOOLEAN)
  - `IsHoliday` (BOOLEAN)
  - `SeasonalityPeriod` (STRING, 'Peak Holiday', 'Back-to-School', 'Summer Low', 'Normal')

---

### 1.2 `DimProduct`
- **Table Type:** Conformed Dimension (SCD Type 2).
- **Grain:** One row per distinct SKU revision version.
- **Primary Key:** `ProductKey` (INT64, Surrogate Key).
- **Foreign Keys:** `PrimarySupplierKey` (INT64 -> `DimSupplier.SupplierKey`).
- **Expected Cardinality:** 15,000 ? 25,000 rows (supporting ~10,000 unique natural SKUs with historical cost/category revisions).
- **Important Columns:**
  - `ProductKey` (INT64, PK)
  - `ProductSKU` (STRING, Natural Key, e.g., 'SKU-10492')
  - `ProductName` (STRING)
  - `BrandName` (STRING)
  - `CategoryName` (STRING, 'Beverages', 'Dry Grocery', 'Personal Care', 'Household', etc.)
  - `SubcategoryName` (STRING)
  - `DepartmentName` (STRING, 'Packaged Goods', 'Fresh/Chilled', 'Non-Food')
  - `UnitStandardCost` (NUMERIC(10, 2), Landed standard inventory cost)
  - `UnitListPrice` (NUMERIC(10, 2), Baseline selling price)
  - `HandlingProfile` (STRING, 'Standard Dry', 'Refrigerated', 'Frozen', 'Hazardous')
  - `StorageClass` (STRING, 'Fast Mover High Bay', 'Standard Rack', 'Temperature Controlled')
  - `WeightKg` (NUMERIC(8, 3))
  - `VolumeCubicMeters` (NUMERIC(8, 4))
  - `PrimarySupplierKey` (INT64)
  - `ABCClassification` (STRING, 'A', 'B', 'C')
  - `XYZClassification` (STRING, 'X', 'Y', 'Z')
  - `EffectiveFrom` (DATE, Inclusive start date of validity)
  - `EffectiveTo` (DATE, Exclusive end date of validity)
  - `IsCurrent` (BOOLEAN, TRUE if current active version)

---

### 1.3 `DimSupplier`
- **Table Type:** Conformed Dimension (SCD Type 1).
- **Grain:** One row per supplier vendor.
- **Primary Key:** `SupplierKey` (INT64, Surrogate Key).
- **Foreign Keys:** None.
- **Expected Cardinality:** 150 ? 250 suppliers.
- **Important Columns:**
  - `SupplierKey` (INT64, PK)
  - `SupplierCode` (STRING, Natural Key, e.g., 'SUP-0042')
  - `SupplierName` (STRING)
  - `Country` (STRING)
  - `City` (STRING)
  - `RegionZone` (STRING, 'Domestic North America', 'Europe Inbound', 'East Asia Sourcing')
  - `SupplierTier` (STRING, 'Tier 1 Strategic', 'Tier 2 Preferred', 'Tier 3 Tactical')
  - `ContractLeadTimeDays` (INT64, Quoted SLA lead time)
  - `LeadTimeToleranceDays` (INT64, Contract grace buffer)
  - `PaymentTermsDays` (INT64, e.g., 30, 60, 90)
  - `MinimumOrderQuantity` (INT64, Contract MOQ)
  - `PreferredStatusFlag` (BOOLEAN)
  - `VendorRiskScore` (NUMERIC(5, 2), Composite reliability index 0-100)

---

### 1.4 `DimWarehouse`
- **Table Type:** Conformed Dimension (SCD Type 1).
- **Grain:** One row per physical distribution center / warehouse facility.
- **Primary Key:** `WarehouseKey` (INT64, Surrogate Key).
- **Foreign Keys:** `RegionKey` (INT64 -> `DimRegion.RegionKey`).
- **Expected Cardinality:** 15 ? 30 regional facilities.
- **Important Columns:**
  - `WarehouseKey` (INT64, PK)
  - `WarehouseCode` (STRING, Natural Key, e.g., 'DC-CENTRAL-01')
  - `WarehouseName` (STRING)
  - `RegionKey` (INT64, FK)
  - `FacilityType` (STRING, 'Central DC', 'Regional DC', 'E-Commerce Hub', 'Transit Cross-Dock')
  - `StorageCapacityPallets` (INT64)
  - `TotalAreaSqMeters` (INT64)
  - `RefrigeratedCapacityPallets` (INT64)
  - `OperatingHoursPerWeek` (INT64)
  - `ActiveFlag` (BOOLEAN)

---

### 1.5 `DimRegion`
- **Table Type:** Conformed Dimension (SCD Type 1).
- **Grain:** One row per geographic operating region.
- **Primary Key:** `RegionKey` (INT64, Surrogate Key).
- **Foreign Keys:** None.
- **Expected Cardinality:** 5 ? 10 regions.
- **Important Columns:**
  - `RegionKey` (INT64, PK)
  - `RegionCode` (STRING, Natural Key, e.g., 'REG-NA-EAST')
  - `RegionName` (STRING, 'North America East', 'North America West', 'Europe Central', etc.)
  - `Theater` (STRING, 'Americas', 'EMEA', 'APAC')
  - `PrimaryCountry` (STRING)
  - `CurrencyCode` (STRING, 'USD', 'EUR', 'GBP')
  - `RegionalDirector` (STRING)

---

### 1.6 `DimCustomerChannel`
- **Table Type:** Conformed Dimension (SCD Type 1).
- **Grain:** One row per commercial sales channel or major customer account.
- **Primary Key:** `CustomerChannelKey` (INT64, Surrogate Key).
- **Foreign Keys:** None.
- **Expected Cardinality:** 1,500 ? 3,500 customer accounts.
- **Important Columns:**
  - `CustomerChannelKey` (INT64, PK)
  - `CustomerChannelCode` (STRING, Natural Key)
  - `ChannelName` (STRING, 'Wholesale B2B', 'Retail Chain Stores', 'E-Commerce Direct')
  - `CustomerAccountName` (STRING)
  - `CustomerSegment` (STRING, 'Tier 1 Key Account', 'Regional Chain', 'Independent', 'Direct Consumer')
  - `CreditTermsDays` (INT64)
  - `DeliveryPriorityTier` (STRING, 'P1 Critical', 'P2 Standard', 'P3 Economy')

---

### 1.7 `DimEmployeePlanner`
- **Table Type:** Conformed Dimension (SCD Type 1).
- **Grain:** One row per supply chain planner / operations employee.
- **Primary Key:** `PlannerKey` (INT64, Surrogate Key).
- **Foreign Keys:** `AssignedRegionKey` (INT64 -> `DimRegion.RegionKey`).
- **Expected Cardinality:** 30 ? 60 employees.
- **Important Columns:**
  - `PlannerKey` (INT64, PK)
  - `EmployeeNumber` (STRING, Natural Key, e.g., 'EMP-5091')
  - `PlannerName` (STRING)
  - `EmailAddress` (STRING, Corporate email used for RLS matching)
  - `JobRole` (STRING, 'VP Operations', 'Regional Supply Planner', 'Warehouse Planner', 'Procurement Manager', 'Supply Chain Analyst')
  - `Department` (STRING, 'Executive Operations', 'Regional Demand Planning', 'Warehouse Operations', 'Sourcing')
  - `AssignedRegionKey` (INT64)
  - `AssignedCategoryGroup` (STRING)

---

### 1.8 `DimScenario`
- **Table Type:** Conformed Dimension (SCD Type 0 - Parameter Reference).
- **Grain:** One row per what-if simulation parameter set.
- **Primary Key:** `ScenarioKey` (INT64, Surrogate Key).
- **Foreign Keys:** None.
- **Expected Cardinality:** 5 ? 10 simulation baselines.
- **Important Columns:**
  - `ScenarioKey` (INT64, PK)
  - `ScenarioCode` (STRING, 'SCN-BASE', 'SCN-SURGE10', 'SCN-PORT7D', 'SCN-SLA98')
  - `ScenarioName` (STRING)
  - `Description` (STRING)
  - `DemandMultiplier` (NUMERIC(4, 2), e.g., 1.00, 1.10, 1.25)
  - `LeadTimeShockDays` (INT64, e.g., 0, +5, +7, +14)
  - `ServiceLevelTargetPct` (NUMERIC(5, 2), e.g., 95.00, 98.00, 99.00)
  - `AnnualCarryingCostRatePct` (NUMERIC(5, 2), e.g., 20.00, 22.00, 25.00)

---

### 1.9 `BridgeProductSupplier`
- **Table Type:** Reference Bridge Table.
- **Grain:** One row per approved sourcing authorization pair (SKU ? Supplier).
- **Primary Key:** Composite (`ProductSKU`, `SupplierKey`).
- **Foreign Keys:**
  - `SupplierKey` (INT64 -> `DimSupplier.SupplierKey`)
- **Expected Cardinality:** 25,000 ? 45,000 rows.
- **Important Columns:**
  - `ProductSKU` (STRING)
  - `SupplierKey` (INT64)
  - `IsPrimarySupplier` (BOOLEAN)
  - `ContractAllocationSharePct` (NUMERIC(5, 2), Target volume allocation e.g., 70.00 / 30.00)
  - `ContractUnitCost` (NUMERIC(10, 2))

---

## 2. Core Fact Tables & Materialized Marts

### 2.1 `FactSales`
- **Table Type:** Transactional Fact Table.
- **Grain:** **One row per fulfilled customer sales order line item.**
- **Primary Key:** `SalesLineKey` (INT64).
- **Foreign Keys:**
  - `OrderDateKey` (INT64 -> `DimDate.DateKey`, Active)
  - `ShipDateKey` (INT64 -> `DimDate.DateKey`, Inactive)
  - `DeliveryDateKey` (INT64 -> `DimDate.DateKey`, Inactive)
  - `ProductKey` (INT64 -> `DimProduct.ProductKey`)
  - `CustomerChannelKey` (INT64 -> `DimCustomerChannel.CustomerChannelKey`)
  - `WarehouseKey` (INT64 -> `DimWarehouse.WarehouseKey`)
- **Partitioning:** BigQuery Day Partition on `OrderDateKey` (or `OrderDate`).
- **Clustering:** `ProductKey`, `CustomerChannelKey`, `WarehouseKey`.
- **Expected Cardinality:** **3,500,000 ? 5,500,000 rows** (2+ years of order lines).
- **Important Columns:**
  - `SalesLineKey` (INT64, PK)
  - `SalesOrderID` (STRING, Degenerate Key)
  - `SalesOrderLineNumber` (INT64)
  - `OrderedQuantity` (INT64)
  - `ShippedQuantity` (INT64)
  - `CancelledQuantity` (INT64)
  - `UnitPrice` (NUMERIC(10, 2))
  - `UnitStandardCost` (NUMERIC(10, 2))
  - `GrossSalesAmount` (NUMERIC(12, 2))
  - `DiscountAmount` (NUMERIC(12, 2))
  - `NetSalesAmount` (NUMERIC(12, 2))
  - `CostOfGoodsSold` (NUMERIC(12, 2))
  - `OrderLineCycleTimeDays` (INT64)
  - `OnTimeInFullFlag` (INT64, 1 if On-Time and In-Full, else 0)

---

### 2.2 `FactInventorySnapshot`
- **Table Type:** Periodic Daily Snapshot Fact Table.
- **Grain:** **One row per SKU ? Warehouse ? Snapshot Date.**
- **Primary Key:** `SnapshotKey` (INT64).
- **Foreign Keys:**
  - `SnapshotDateKey` (INT64 -> `DimDate.DateKey`, Active)
  - `ProductKey` (INT64 -> `DimProduct.ProductKey`)
  - `WarehouseKey` (INT64 -> `DimWarehouse.WarehouseKey`)
- **Partitioning:** BigQuery Day Partition on `SnapshotDateKey` (or `SnapshotDate`).
- **Clustering:** `ProductKey`, `WarehouseKey`.
- **Expected Cardinality:** **4,500,000 ? 7,500,000 rows** (Active catalog across facilities over 2-3 years).
- **Important Columns:**
  - `SnapshotKey` (INT64, PK)
  - `SnapshotDate` (DATE)
  - `OnHandQuantity` (INT64, Semi-additive)
  - `ReservedQuantity` (INT64, Stock committed to open sales orders)
  - `AvailableQuantity` (INT64, OnHand - Reserved)
  - `InTransitInboundQuantity` (INT64, Pipeline inbound stock on open POs)
  - `UnitLandedCost` (NUMERIC(10, 2))
  - `InventoryValuation` (NUMERIC(14, 2), OnHand * UnitLandedCost)
  - `DaysSinceLastMovement` (INT64, Aging metric)
  - `IsStockoutFlag` (INT64, 1 if AvailableQuantity <= 0, else 0)
  - `IsDeadStockFlag` (INT64, 1 if DaysSinceLastMovement >= 180, else 0)

---

### 2.3 `FactPurchaseOrder`
- **Table Type:** Accumulating / Transactional Fact Table.
- **Grain:** **One row per purchase order line item.**
- **Primary Key:** `POLineKey` (INT64).
- **Foreign Keys:**
  - `POCreationDateKey` (INT64 -> `DimDate.DateKey`, Active)
  - `PromisedDeliveryDateKey` (INT64 -> `DimDate.DateKey`, Inactive)
  - `ActualDockReceiptDateKey` (INT64 -> `DimDate.DateKey`, Inactive)
  - `SupplierKey` (INT64 -> `DimSupplier.SupplierKey`)
  - `ProductKey` (INT64 -> `DimProduct.ProductKey`)
  - `ReceivingWarehouseKey` (INT64 -> `DimWarehouse.WarehouseKey`)
  - `BuyerEmployeeKey` (INT64 -> `DimEmployeePlanner.PlannerKey`)
- **Partitioning:** BigQuery Day Partition on `POCreationDateKey`.
- **Clustering:** `SupplierKey`, `ProductKey`, `ReceivingWarehouseKey`.
- **Expected Cardinality:** **600,000 ? 1,200,000 rows**.
- **Important Columns:**
  - `POLineKey` (INT64, PK)
  - `PurchaseOrderID` (STRING, Degenerate Key)
  - `POLineNumber` (INT64)
  - `OrderedQuantity` (INT64)
  - `ReceivedQuantity` (INT64)
  - `RejectedQuantity` (INT64)
  - `UnitPurchasePrice` (NUMERIC(10, 2))
  - `ExtendedPOAmount` (NUMERIC(12, 2))
  - `PromisedLeadTimeDays` (INT64)
  - `ActualLeadTimeDays` (INT64)
  - `LeadTimeVarianceDays` (INT64, Actual - Promised)
  - `IsDeliveredOnTimeFlag` (INT64, 1 if ActualDockDate <= PromisedDate, else 0)
  - `IsDeliveredInFullFlag` (INT64, 1 if ReceivedQty >= OrderedQty, else 0)
  - `IsSupplierOTIFFlag` (INT64, 1 if On-Time AND In-Full, else 0)
  - `POStatus` (STRING, 'Completed', 'Open In-Transit', 'Overdue', 'Cancelled')

---

### 2.4 `FactDemandForecast`
- **Table Type:** Periodic Planning Snapshot Fact Table.
- **Grain:** **One row per SKU ? Warehouse ? Forecast Generation Date ? Target Horizon Period.**
- **Primary Key:** `ForecastKey` (INT64).
- **Foreign Keys:**
  - `TargetPeriodDateKey` (INT64 -> `DimDate.DateKey`, Active)
  - `ForecastGeneratedDateKey` (INT64 -> `DimDate.DateKey`, Inactive)
  - `ProductKey` (INT64 -> `DimProduct.ProductKey`)
  - `WarehouseKey` (INT64 -> `DimWarehouse.WarehouseKey`)
  - `ScenarioKey` (INT64 -> `DimScenario.ScenarioKey`)
- **Partitioning:** BigQuery Month Partition on `TargetPeriodDateKey`.
- **Clustering:** `ProductKey`, `WarehouseKey`.
- **Expected Cardinality:** **600,000 ? 1,200,000 rows**.
- **Important Columns:**
  - `ForecastKey` (INT64, PK)
  - `ForecastedQuantity` (INT64, Final consensus forecast)
  - `BaselineStatisticalQuantity` (INT64, Algorithmic projection)
  - `PlannerAdjustmentQuantity` (INT64, Manual override delta)
  - `ForecastValue` (NUMERIC(12, 2), ForecastedQuantity * UnitListPrice)
  - `ForecastModelVersion` (STRING, 'HoltWinters-V2', 'ARIMA-Promo', 'Consensus')

---

### 2.5 `FactInventoryMovement`
- **Table Type:** Transactional Event Fact Table.
- **Grain:** **One row per physical inventory transfer or adjustment transaction.**
- **Primary Key:** `MovementKey` (INT64).
- **Foreign Keys:**
  - `MovementDateKey` (INT64 -> `DimDate.DateKey`, Active)
  - `ProductKey` (INT64 -> `DimProduct.ProductKey`)
  - `OriginWarehouseKey` (INT64 -> `DimWarehouse.WarehouseKey`)
  - `DestinationWarehouseKey` (INT64 -> `DimWarehouse.WarehouseKey`, NULL for adjustments)
  - `ResponsibleEmployeeKey` (INT64 -> `DimEmployeePlanner.PlannerKey`)
- **Partitioning:** BigQuery Day Partition on `MovementDateKey`.
- **Clustering:** `ProductKey`, `OriginWarehouseKey`.
- **Expected Cardinality:** **500,000 ? 1,000,000 rows**.
- **Important Columns:**
  - `MovementKey` (INT64, PK)
  - `MovementTransactionID` (STRING, Degenerate Key)
  - `MovementType` (STRING, 'Inter-DC Transfer', 'Cycle Count Adjustment', 'Spoilage Scrap', 'Damage Write-off')
  - `MovementQuantity` (INT64, Positive for stock increments, negative for decrements)
  - `MovementValue` (NUMERIC(12, 2))
  - `TransferFreightCost` (NUMERIC(10, 2))
  - `TransferTransitDays` (INT64)

---

### 2.6 `FactStockout`
- **Table Type:** Derived Event Fact Table (Consolidated Outage Incidents).
- **Grain:** **One row per consolidated continuous stockout episode per SKU ? Warehouse.**
- **Primary Key:** `StockoutEventKey` (INT64).
- **Foreign Keys:**
  - `StartDateKey` (INT64 -> `DimDate.DateKey`, Active)
  - `EndDateKey` (INT64 -> `DimDate.DateKey`, Inactive)
  - `ProductKey` (INT64 -> `DimProduct.ProductKey`)
  - `WarehouseKey` (INT64 -> `DimWarehouse.WarehouseKey`)
- **Partitioning:** BigQuery Month Partition on `StartDateKey`.
- **Clustering:** `ProductKey`, `WarehouseKey`.
- **Expected Cardinality:** **75,000 ? 150,000 outage events**.
- **Important Columns:**
  - `StockoutEventKey` (INT64, PK)
  - `StartDate` (DATE)
  - `EndDate` (DATE)
  - `StockoutDurationDays` (INT64, EndDate - StartDate + 1)
  - `EstimatedLostDemandUnits` (INT64)
  - `EstimatedLostRevenueAmount` (NUMERIC(12, 2))
  - `StockoutAttributedReason` (STRING, 'Supplier Delayed Inbound', 'Demand Spike', 'Record Inaccuracy')
  - `SeverityTier` (STRING, 'Critical Tier A', 'Moderate Tier B', 'Low Tier C')

---

### 2.7 `FactCustomerReturns`
- **Table Type:** Transactional Fact Table.
- **Grain:** **One row per returned customer order line item.**
- **Primary Key:** `ReturnLineKey` (INT64).
- **Foreign Keys:**
  - `ReturnDateKey` (INT64 -> `DimDate.DateKey`, Active)
  - `OriginalOrderDateKey` (INT64 -> `DimDate.DateKey`, Inactive)
  - `ProductKey` (INT64 -> `DimProduct.ProductKey`)
  - `ReceivingWarehouseKey` (INT64 -> `DimWarehouse.WarehouseKey`)
  - `CustomerChannelKey` (INT64 -> `DimCustomerChannel.CustomerChannelKey`)
- **Partitioning:** BigQuery Month Partition on `ReturnDateKey`.
- **Clustering:** `ProductKey`, `CustomerChannelKey`.
- **Expected Cardinality:** **200,000 ? 400,000 rows**.
- **Important Columns:**
  - `ReturnLineKey` (INT64, PK)
  - `ReturnID` (STRING, Degenerate Key)
  - `ReturnedQuantity` (INT64)
  - `RestockedQuantity` (INT64, Returned to active saleable stock)
  - `ScrappedQuantity` (INT64, Damaged beyond repair)
  - `RefundAmount` (NUMERIC(10, 2))
  - `ReturnReasonCategory` (STRING, 'Defective Item', 'Shipping Damage', 'Wrong Item Shipped', 'Customer Remorse')
  - `DispositionStatus` (STRING, 'Restocked', 'Scrapped', 'Return to Vendor')

---

### 2.8 `FactSupplierMonthlyPerformance` (Materialized Analytical Mart)
- **Table Type:** Materialized Analytical Mart (Built via dbt).
- **Grain:** **One row per Supplier ? Month.**
- **Primary Key:** `SupplierMonthlyKey` (INT64).
- **Foreign Keys:**
  - `YearMonthDateKey` (INT64 -> `DimDate.DateKey`, Active - month start date)
  - `SupplierKey` (INT64 -> `DimSupplier.SupplierKey`)
- **Expected Cardinality:** **3,500 ? 7,500 rows** (~200 suppliers ? 36 months).
- **Important Columns:**
  - `SupplierMonthlyKey` (INT64, PK)
  - `YearMonth` (STRING, '2025-06')
  - `TotalPOCount` (INT64)
  - `TotalPOLines` (INT64)
  - `TotalOrderedQuantity` (INT64)
  - `TotalReceivedQuantity` (INT64)
  - `TotalRejectedQuantity` (INT64)
  - `TotalSpendAmount` (NUMERIC(14, 2))
  - `OnTimePOCount` (INT64)
  - `InFullPOCount` (INT64)
  - `OTIFLineCount` (INT64)
  - `OTIFRatePct` (NUMERIC(5, 2))
  - `AverageLeadTimeDays` (NUMERIC(6, 2))
  - `LeadTimeStdDevDays` (NUMERIC(6, 2))
  - `LateDeliveryCount` (INT64)
  - `LineFillRatePct` (NUMERIC(5, 2))
  - `SupplierMonthlyRiskRating` (STRING, 'Low Risk', 'Moderate Risk', 'Critical SLA Breach')
