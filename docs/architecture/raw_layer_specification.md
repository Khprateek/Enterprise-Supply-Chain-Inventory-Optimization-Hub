# Raw Layer Specification: Physical Schema, Partitioning & Clustering

This document defines the physical DDL specifications for ingesting the validated raw Parquet files into Google BigQuery dataset aw_supply_chain.

---

## 1. Design Principles for the Raw Layer
1. **Columnar Ingestion:** Ingested directly from compressed Parquet files to preserve explicit schema data types without loose string conversions.
2. **Partitioning:** Applied on high-volume fact tables using event dates (DATE) to prune query scan overheads.
3. **Clustering:** Applied up to 4 high-cardinality foreign keys (ProductKey, WarehouseKey, SupplierKey, CustomerChannelKey) to accelerate joins.
4. **Immutability:** Raw tables are read-only append-only audit sources.

---

## 2. DDL Specifications

### 2.1 Dimensions & Bridge Tables

`sql
-- DimDate
CREATE OR REPLACE TABLE aw_supply_chain.raw_dim_date (
    DateKey INT64,
    FullDate DATE,
    DayOfWeek INT64,
    DayName STRING,
    DayOfMonth INT64,
    DayOfYear INT64,
    WeekOfYear INT64,
    MonthNumber INT64,
    MonthName STRING,
    MonthYear STRING,
    QuarterNumber INT64,
    QuarterName STRING,
    YearNumber INT64,
    FiscalMonthNumber INT64,
    FiscalQuarter STRING,
    FiscalYear INT64,
    IsWeekday BOOLEAN,
    IsHoliday BOOLEAN,
    SeasonalityPeriod STRING
);

-- DimRegion
CREATE OR REPLACE TABLE aw_supply_chain.raw_dim_region (
    RegionKey INT64,
    RegionCode STRING,
    RegionName STRING,
    Theater STRING,
    PrimaryCountry STRING,
    CurrencyCode STRING,
    RegionalDirector STRING
);

-- DimWarehouse
CREATE OR REPLACE TABLE aw_supply_chain.raw_dim_warehouse (
    WarehouseKey INT64,
    WarehouseCode STRING,
    WarehouseName STRING,
    RegionKey INT64,
    FacilityType STRING,
    StorageCapacityPallets INT64,
    TotalAreaSqMeters INT64,
    RefrigeratedCapacityPallets INT64,
    OperatingHoursPerWeek INT64,
    ActiveFlag BOOLEAN
)
CLUSTER BY RegionKey;

-- DimSupplier
CREATE OR REPLACE TABLE aw_supply_chain.raw_dim_supplier (
    SupplierKey INT64,
    SupplierCode STRING,
    SupplierName STRING,
    Country STRING,
    City STRING,
    RegionZone STRING,
    SupplierTier STRING,
    ContractLeadTimeDays INT64,
    LeadTimeToleranceDays INT64,
    PaymentTermsDays INT64,
    MinimumOrderQuantity INT64,
    PreferredStatusFlag BOOLEAN,
    VendorRiskScore NUMERIC(5, 2)
);

-- DimProduct (SCD2 Seed/Staging Source)
CREATE OR REPLACE TABLE aw_supply_chain.raw_dim_product (
    ProductKey INT64,
    ProductSKU STRING,
    ProductName STRING,
    BrandName STRING,
    CategoryName STRING,
    SubcategoryName STRING,
    DepartmentName STRING,
    UnitStandardCost NUMERIC(10, 2),
    UnitListPrice NUMERIC(10, 2),
    HandlingProfile STRING,
    StorageClass STRING,
    WeightKg NUMERIC(8, 3),
    VolumeCubicMeters NUMERIC(8, 4),
    PrimarySupplierKey INT64,
    ABCClassification STRING,
    XYZClassification STRING,
    EffectiveFrom DATE,
    EffectiveTo DATE,
    IsCurrent BOOLEAN
)
CLUSTER BY PrimarySupplierKey, CategoryName;

-- DimCustomerChannel
CREATE OR REPLACE TABLE aw_supply_chain.raw_dim_customer_channel (
    CustomerChannelKey INT64,
    CustomerChannelCode STRING,
    ChannelName STRING,
    CustomerAccountName STRING,
    CustomerSegment STRING,
    CreditTermsDays INT64,
    DeliveryPriorityTier STRING
);

-- DimEmployeePlanner
CREATE OR REPLACE TABLE aw_supply_chain.raw_dim_employee_planner (
    PlannerKey INT64,
    EmployeeNumber STRING,
    PlannerName STRING,
    EmailAddress STRING,
    JobRole STRING,
    Department STRING,
    AssignedRegionKey INT64,
    AssignedCategoryGroup STRING
);

-- DimScenario
CREATE OR REPLACE TABLE aw_supply_chain.raw_dim_scenario (
    ScenarioKey INT64,
    ScenarioCode STRING,
    ScenarioName STRING,
    Description STRING,
    DemandMultiplier NUMERIC(4, 2),
    LeadTimeShockDays INT64,
    ServiceLevelTargetPct NUMERIC(5, 2),
    AnnualCarryingCostRatePct NUMERIC(5, 2)
);

-- BridgeProductSupplier
CREATE OR REPLACE TABLE aw_supply_chain.raw_bridge_product_supplier (
    BridgeKey INT64,
    ProductSKU STRING,
    SupplierKey INT64,
    IsPrimarySupplier BOOLEAN,
    ContractAllocationSharePct NUMERIC(5, 2)
)
CLUSTER BY SupplierKey, ProductSKU;
`

---

### 2.2 Core Fact Tables

`sql
-- FactSales (2.47M rows)
CREATE OR REPLACE TABLE aw_supply_chain.raw_fact_sales (
    SalesLineKey INT64,
    SalesOrderID STRING,
    SalesOrderLineNumber INT64,
    OrderDate DATE,
    ShipDate DATE,
    DeliveryDate DATE,
    OrderDateKey INT64,
    ShipDateKey INT64,
    DeliveryDateKey INT64,
    ProductKey INT64,
    ProductSKU STRING,
    CustomerChannelKey INT64,
    CustomerChannelCode STRING,
    WarehouseKey INT64,
    WarehouseCode STRING,
    OrderedQuantity INT64,
    ShippedQuantity INT64,
    CancelledQuantity INT64,
    UnitPrice NUMERIC(10, 2),
    UnitStandardCost NUMERIC(10, 2),
    GrossSalesAmount NUMERIC(12, 2),
    DiscountAmount NUMERIC(12, 2),
    NetSalesAmount NUMERIC(12, 2),
    CostOfGoodsSold NUMERIC(12, 2),
    OrderLineCycleTimeDays INT64,
    OnTimeInFullFlag INT64
)
PARTITION BY OrderDate
CLUSTER BY ProductKey, WarehouseKey, CustomerChannelKey;

-- FactInventorySnapshot (5.46M rows)
CREATE OR REPLACE TABLE aw_supply_chain.raw_fact_inventory_snapshot (
    SnapshotKey INT64,
    SnapshotDate DATE,
    SnapshotDateKey INT64,
    ProductKey INT64,
    ProductSKU STRING,
    WarehouseKey INT64,
    WarehouseCode STRING,
    OnHandQuantity INT64,
    ReservedQuantity INT64,
    AvailableQuantity INT64,
    InTransitInboundQuantity INT64,
    UnitLandedCost NUMERIC(10, 2),
    InventoryValuation NUMERIC(14, 2),
    DaysSinceLastMovement INT64,
    IsStockoutFlag INT64,
    IsDeadStockFlag INT64
)
PARTITION BY SnapshotDate
CLUSTER BY ProductKey, WarehouseKey;

-- FactPurchaseOrder (1.11M rows)
CREATE OR REPLACE TABLE aw_supply_chain.raw_fact_purchase_order (
    POLineKey INT64,
    PurchaseOrderID STRING,
    POLineNumber INT64,
    POCreationDate DATE,
    PromisedDeliveryDate DATE,
    ActualDockReceiptDate DATE,
    POCreationDateKey INT64,
    PromisedDeliveryDateKey INT64,
    ActualDockReceiptDateKey INT64,
    SupplierKey INT64,
    SupplierCode STRING,
    ProductKey INT64,
    ProductSKU STRING,
    ReceivingWarehouseKey INT64,
    WarehouseCode STRING,
    BuyerEmployeeKey INT64,
    OrderedQuantity INT64,
    ReceivedQuantity INT64,
    RejectedQuantity INT64,
    UnitPurchasePrice NUMERIC(10, 2),
    ExtendedPOAmount NUMERIC(12, 2),
    PromisedLeadTimeDays INT64,
    ActualLeadTimeDays INT64,
    LeadTimeVarianceDays INT64,
    IsDeliveredOnTimeFlag INT64,
    IsDeliveredInFullFlag INT64,
    IsSupplierOTIFFlag INT64,
    POStatus STRING
)
PARTITION BY POCreationDate
CLUSTER BY SupplierKey, ProductKey, ReceivingWarehouseKey;

-- FactDemandForecast (179K rows)
CREATE OR REPLACE TABLE aw_supply_chain.raw_fact_demand_forecast (
    ForecastKey INT64,
    TargetPeriodDate DATE,
    ForecastGeneratedDate DATE,
    TargetPeriodDateKey INT64,
    ForecastGeneratedDateKey INT64,
    ProductKey INT64,
    ProductSKU STRING,
    WarehouseKey INT64,
    WarehouseCode STRING,
    ScenarioKey INT64,
    ForecastedQuantity INT64,
    BaselineStatisticalQuantity INT64,
    PlannerAdjustmentQuantity INT64,
    ForecastValue NUMERIC(12, 2)
)
PARTITION BY TargetPeriodDate
CLUSTER BY ProductKey, WarehouseKey;

-- FactInventoryMovement (175K rows)
CREATE OR REPLACE TABLE aw_supply_chain.raw_fact_inventory_movement (
    MovementKey INT64,
    MovementTransactionID STRING,
    MovementDate DATE,
    MovementDateKey INT64,
    ProductKey INT64,
    ProductSKU STRING,
    OriginWarehouseKey INT64,
    DestinationWarehouseKey INT64,
    ResponsibleEmployeeKey INT64,
    MovementType STRING,
    MovementQuantity INT64,
    MovementValue NUMERIC(12, 2),
    TransferFreightCost NUMERIC(10, 2),
    TransferTransitDays INT64
)
PARTITION BY MovementDate
CLUSTER BY ProductKey, OriginWarehouseKey;

-- FactStockout (913 rows)
CREATE OR REPLACE TABLE aw_supply_chain.raw_fact_stockout (
    StockoutEventKey INT64,
    StartDateKey INT64,
    EndDateKey INT64,
    StartDate DATE,
    EndDate DATE,
    ProductKey INT64,
    ProductSKU STRING,
    WarehouseKey INT64,
    StockoutDurationDays INT64,
    EstimatedLostDemandUnits INT64,
    EstimatedLostRevenueAmount NUMERIC(12, 2),
    StockoutAttributedReason STRING,
    SeverityTier STRING
)
CLUSTER BY ProductKey, WarehouseKey;

-- FactCustomerReturns (103K rows)
CREATE OR REPLACE TABLE aw_supply_chain.raw_fact_customer_returns (
    ReturnLineKey INT64,
    ReturnID STRING,
    ReturnDate DATE,
    OriginalOrderDate DATE,
    ReturnDateKey INT64,
    OriginalOrderDateKey INT64,
    ProductKey INT64,
    ProductSKU STRING,
    ReceivingWarehouseKey INT64,
    WarehouseCode STRING,
    CustomerChannelKey INT64,
    ReturnedQuantity INT64,
    RestockedQuantity INT64,
    ScrappedQuantity INT64,
    RefundAmount NUMERIC(10, 2),
    ReturnReasonCategory STRING,
    DispositionStatus STRING
)
PARTITION BY ReturnDate
CLUSTER BY ProductKey, CustomerChannelKey;
`
