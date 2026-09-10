# Enterprise Data Dictionary: Supply Chain & Inventory Optimization Hub

This document defines the complete physical data dictionary for all dimension, fact, bridge, and analytical mart tables in the Enterprise Supply Chain & Inventory Optimization Hub.

---

## Table of Contents
1. [Conformed Dimensions](#1-conformed-dimensions)
   - [DimDate](#11-dimdate)
   - [DimProduct (SCD2)](#12-dimproduct-scd-type-2)
   - [DimSupplier](#13-dimsupplier)
   - [DimWarehouse](#14-dimwarehouse)
   - [DimRegion](#15-dimregion)
   - [DimCustomerChannel](#16-dimcustomerchannel)
   - [DimEmployeePlanner](#17-dimemployeeplanner)
   - [DimScenario](#18-dimscenario)
   - [BridgeProductSupplier](#19-bridgeproductsupplier)
2. [Fact Tables & Marts](#2-fact-tables--marts)
   - [FactSales](#21-factsales)
   - [FactInventorySnapshot](#22-factinventorysnapshot)
   - [FactPurchaseOrder](#23-factpurchaseorder)
   - [FactDemandForecast](#24-factdemandforecast)
   - [FactInventoryMovement](#25-factinventorymovement)
   - [FactStockout](#26-factstockout)
   - [FactCustomerReturns](#27-factcustomerreturns)
   - [FactSupplierMonthlyPerformance](#28-factsuppliermonthlyperformance)

---

## 1. Conformed Dimensions

### 1.1 `DimDate`
| Column Name | Data Type | Nullable | Key Type | Business Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DateKey` | INT64 | No | PK | Integer surrogate key in YYYYMMDD format. | `20260910` |
| `FullDate` | DATE | No | Natural Key | Calendar date in standard ISO format. | `2026-09-10` |
| `DayOfWeek` | INT64 | No | Attribute | Day of week integer (1=Sunday through 7=Saturday). | `5` |
| `DayName` | STRING | No | Attribute | Full English name of the day. | `'Thursday'` |
| `DayOfMonth` | INT64 | No | Attribute | Day of the month integer (1?31). | `10` |
| `DayOfYear` | INT64 | No | Attribute | Sequential day count within the year (1?366). | `253` |
| `WeekOfYear` | INT64 | No | Attribute | ISO calendar week number (1?53). | `37` |
| `MonthNumber` | INT64 | No | Attribute | Calendar month number (1?12). | `9` |
| `MonthName` | STRING | No | Attribute | Full English name of the month. | `'September'` |
| `MonthYear` | STRING | No | Attribute | Year and month label for reporting slicers. | `'2026-09'` |
| `QuarterNumber` | INT64 | No | Attribute | Calendar quarter integer (1?4). | `3` |
| `QuarterName` | STRING | No | Attribute | Calendar quarter label. | `'Q3'` |
| `YearNumber` | INT64 | No | Attribute | Four-digit calendar year. | `2026` |
| `FiscalMonthNumber` | INT64 | No | Attribute | Fiscal period month (1?12). | `12` |
| `FiscalQuarter` | STRING | No | Attribute | Fiscal quarter label. | `'FQ4'` |
| `FiscalYear` | INT64 | No | Attribute | Fiscal reporting year. | `2026` |
| `IsWeekday` | BOOLEAN | No | Attribute | TRUE if Monday?Friday, else FALSE. | `TRUE` |
| `IsHoliday` | BOOLEAN | No | Attribute | TRUE if national public operating holiday. | `FALSE` |
| `SeasonalityPeriod` | STRING | No | Attribute | Operational seasonal demand classification. | `'Back-to-School'` |

---

### 1.2 `DimProduct` (SCD Type 2)
| Column Name | Data Type | Nullable | Key Type | Business Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ProductKey` | INT64 | No | PK | Surrogate key identifying distinct product revision. | `10042` |
| `ProductSKU` | STRING | No | Natural Key | Stable business SKU identifier from ERP/PLM. | `'SKU-BEV-001'` |
| `ProductName` | STRING | No | Attribute | Commercial product name description. | `'Sparkling Citrus 500ml'` |
| `BrandName` | STRING | No | Attribute | Product brand portfolio name. | `'AuraPure'` |
| `CategoryName` | STRING | No | Attribute | Primary product merchandising category. | `'Beverages'` |
| `SubcategoryName` | STRING | No | Attribute | Merchandising subcategory. | `'Carbonated Soft Drinks'` |
| `DepartmentName` | STRING | No | Attribute | High-level organizational department. | `'Packaged Goods'` |
| `UnitStandardCost` | NUMERIC(10, 2) | No | Tracked SCD2 | Landed inventory standard valuation cost. | `1.45` |
| `UnitListPrice` | NUMERIC(10, 2) | No | Attribute | Recommended baseline selling price. | `2.99` |
| `HandlingProfile` | STRING | No | Attribute | Storage & safety profile. | `'Standard Dry'` |
| `StorageClass` | STRING | No | Attribute | Warehouse slotting velocity tier. | `'Fast Mover High Bay'` |
| `WeightKg` | NUMERIC(8, 3) | No | Attribute | Net weight per packaged unit in kilograms. | `0.520` |
| `VolumeCubicMeters` | NUMERIC(8, 4) | No | Attribute | Cubic volume per packaged unit. | `0.0012` |
| `PrimarySupplierKey`| INT64 | No | FK / Tracked | FK to primary sourcing vendor in `DimSupplier`. | `12` |
| `ABCClassification` | STRING | No | Attribute | Annual consumption value tier (A/B/C). | `'A'` |
| `XYZClassification` | STRING | No | Attribute | Demand volatility coefficient of variation tier (X/Y/Z). | `'X'` |
| `EffectiveFrom` | DATE | No | Temporal | Inclusive start date of this product version. | `2025-01-01` |
| `EffectiveTo` | DATE | No | Temporal | Exclusive expiry date of this version. | `9999-12-31` |
| `IsCurrent` | BOOLEAN | No | Temporal | TRUE if current active record, else FALSE. | `TRUE` |

---

### 1.3 `DimSupplier`
| Column Name | Data Type | Nullable | Key Type | Business Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SupplierKey` | INT64 | No | PK | Surrogate key identifying unique vendor. | `12` |
| `SupplierCode` | STRING | No | Natural Key | Operational ERP supplier account code. | `'SUP-0042'` |
| `SupplierName` | STRING | No | Attribute | Full legal vendor business name. | `'Apex Packaging Solutions'` |
| `Country` | STRING | No | Attribute | Supplier headquarters country of dispatch. | `'United States'` |
| `City` | STRING | No | Attribute | Supplier dispatch origin city. | `'Chicago'` |
| `RegionZone` | STRING | No | Attribute | Logistics geographic sourcing zone. | `'Domestic North America'` |
| `SupplierTier` | STRING | No | Attribute | Strategic vendor tier classification. | `'Tier 1 Strategic'` |
| `ContractLeadTimeDays` | INT64 | No | Attribute | Baseline SLA lead time in calendar days. | `14` |
| `LeadTimeToleranceDays`| INT64 | No | Attribute | Contractual grace window for on-time arrivals. | `2` |
| `PaymentTermsDays` | INT64 | No | Attribute | Standard supplier credit payment terms. | `45` |
| `MinimumOrderQuantity`| INT64 | No | Attribute | Minimum allowable purchasing batch (MOQ). | `500` |
| `PreferredStatusFlag` | BOOLEAN | No | Attribute | TRUE if vendor is preferred contract partner. | `TRUE` |
| `VendorRiskScore` | NUMERIC(5, 2) | No | Attribute | Vendor risk index score (0.00 to 100.00). | `88.50` |

---

### 1.4 `DimWarehouse`
| Column Name | Data Type | Nullable | Key Type | Business Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `WarehouseKey` | INT64 | No | PK | Surrogate key identifying warehouse facility. | `4` |
| `WarehouseCode` | STRING | No | Natural Key | Operational warehouse/DC facility code. | `'DC-CENTRAL-01'` |
| `WarehouseName` | STRING | No | Attribute | Official facility name. | `'Midwest Distribution Hub'` |
| `RegionKey` | INT64 | No | FK | Foreign key to operating `DimRegion`. | `2` |
| `FacilityType` | STRING | No | Attribute | Operational distribution facility classification. | `'Central DC'` |
| `StorageCapacityPallets`| INT64 | No | Attribute | Maximum rated pallet storage capacity. | `25000` |
| `TotalAreaSqMeters`| INT64 | No | Attribute | Total facility floor footprint in square meters. | `45000` |
| `RefrigeratedCapacityPallets`| INT64 | No | Attribute | Climate-controlled cold storage pallet slots. | `4000` |
| `OperatingHoursPerWeek`| INT64 | No | Attribute | Weekly dock operating schedule hours. | `120` |
| `ActiveFlag` | BOOLEAN | No | Attribute | TRUE if facility is currently operational. | `TRUE` |

---

### 1.5 `DimRegion`
| Column Name | Data Type | Nullable | Key Type | Business Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `RegionKey` | INT64 | No | PK | Surrogate key identifying operating region. | `2` |
| `RegionCode` | STRING | No | Natural Key | Geographic region business code. | `'REG-NA-MIDWEST'` |
| `RegionName` | STRING | No | Attribute | Name of the geographic operating market. | `'North America Midwest'` |
| `Theater` | STRING | No | Attribute | Global macro operating theater. | `'Americas'` |
| `PrimaryCountry` | STRING | No | Attribute | Primary nation governing operational territory. | `'United States'` |
| `CurrencyCode` | STRING | No | Attribute | Base transactional currency of the region. | `'USD'` |
| `RegionalDirector` | STRING | No | Attribute | Operations director responsible for the zone. | `'Marcus Vance'` |

---

### 1.6 `DimCustomerChannel`
| Column Name | Data Type | Nullable | Key Type | Business Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CustomerChannelKey` | INT64 | No | PK | Surrogate key identifying customer account/channel. | `145` |
| `CustomerChannelCode`| STRING | No | Natural Key | Commercial account number or channel code. | `'CH-RET-0089'` |
| `ChannelName` | STRING | No | Attribute | Broad commercial distribution channel. | `'Retail Chain Stores'` |
| `CustomerAccountName`| STRING | No | Attribute | Customer legal entity or account name. | `'MegaMart Corp'` |
| `CustomerSegment` | STRING | No | Attribute | Account priority tier. | `'Tier 1 Key Account'` |
| `CreditTermsDays` | INT64 | No | Attribute | Standard commercial payment terms. | `30` |
| `DeliveryPriorityTier`| STRING | No | Attribute | Order allocation priority tier during stockouts. | `'P1 Critical'` |

---

### 1.7 `DimEmployeePlanner`
| Column Name | Data Type | Nullable | Key Type | Business Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `PlannerKey` | INT64 | No | PK | Surrogate key identifying supply chain employee. | `8` |
| `EmployeeNumber` | STRING | No | Natural Key | Corporate HR employee ID. | `'EMP-5091'` |
| `PlannerName` | STRING | No | Attribute | Employee full name. | `'Elena Rostova'` |
| `EmailAddress` | STRING | No | Attribute | Corporate email used for RLS dynamic filtering. | `'elena.rostova@retailhub.com'` |
| `JobRole` | STRING | No | Attribute | Supply chain operational job title. | `'Regional Supply Planner'` |
| `Department` | STRING | No | Attribute | Organizational functional department. | `'Regional Demand Planning'` |
| `AssignedRegionKey` | INT64 | No | FK | FK to `DimRegion` governing planner RLS scope. | `2` |
| `AssignedCategoryGroup`| STRING | No | Attribute | Merchandising category group planned. | `'Beverages & Snacks'` |

---

### 1.8 `DimScenario`
| Column Name | Data Type | Nullable | Key Type | Business Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ScenarioKey` | INT64 | No | PK | Surrogate key for simulation baseline. | `1` |
| `ScenarioCode` | STRING | No | Natural Key | Unique scenario identifier code. | `'SCN-BASE'` |
| `ScenarioName` | STRING | No | Attribute | Short scenario title. | `'Baseline Budget Plan'` |
| `Description` | STRING | No | Attribute | Narrative description of simulation parameters. | `'Status-quo demand, contract SLAs'` |
| `DemandMultiplier` | NUMERIC(4, 2) | No | Parameter | Scaling factor applied to projected demand. | `1.00` |
| `LeadTimeShockDays` | INT64 | No | Parameter | Lead-time shift in days added to supplier lead times. | `0` |
| `ServiceLevelTargetPct`| NUMERIC(5, 2)| No | Parameter | Target cycle service level percentage. | `95.00` |
| `AnnualCarryingCostRatePct`| NUMERIC(5, 2)| No | Parameter | Assumed annual inventory holding cost rate. | `22.00` |

---

### 1.9 `BridgeProductSupplier`
| Column Name | Data Type | Nullable | Key Type | Business Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ProductSKU` | STRING | No | PK (Composite) | Natural product SKU identifier. | `'SKU-BEV-001'` |
| `SupplierKey` | INT64 | No | PK, FK | Foreign key to `DimSupplier.SupplierKey`. | `12` |
| `IsPrimarySupplier` | BOOLEAN | No | Attribute | TRUE if designated primary contract vendor. | `TRUE` |
| `ContractAllocationSharePct`| NUMERIC(5, 2)| No | Attribute | Target volume allocation percentage. | `70.00` |
| `ContractUnitCost` | NUMERIC(10, 2)| No | Attribute | Negotiated contract unit purchasing cost. | `1.42` |

---

## 2. Fact Tables & Marts

### 2.1 `FactSales`
| Column Name | Data Type | Nullable | Key Type | Business Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SalesLineKey` | INT64 | No | PK | Surrogate key uniquely identifying sales order line. | `819203` |
| `SalesOrderID` | STRING | No | Degenerate Key | Source ERP sales order document number. | `'SO-2025-99102'` |
| `SalesOrderLineNumber`| INT64 | No | Attribute | Line number on sales order header. | `1` |
| `OrderDateKey` | INT64 | No | FK (Active) | Order placement date linking to `DimDate.DateKey`. | `20250615` |
| `ShipDateKey` | INT64 | No | FK (Inactive) | Physical warehouse dispatch date. | `20250616` |
| `DeliveryDateKey` | INT64 | No | FK (Inactive) | Final customer delivery confirmation date. | `20250618` |
| `ProductKey` | INT64 | No | FK | Specific product revision linking to `DimProduct`. | `10042` |
| `CustomerChannelKey`| INT64 | No | FK | Ordering customer/channel linking to `DimCustomerChannel`. | `145` |
| `WarehouseKey` | INT64 | No | FK | Fulfilling warehouse facility linking to `DimWarehouse`. | `4` |
| `OrderedQuantity` | INT64 | No | Additive Measure | Customer requested order units. | `100` |
| `ShippedQuantity` | INT64 | No | Additive Measure | Units actually fulfilled and dispatched. | `98` |
| `CancelledQuantity` | INT64 | No | Additive Measure | Units unfulfilled and cancelled due to stockout. | `2` |
| `UnitPrice` | NUMERIC(10, 2) | No | Unit Measure | Gross selling price per unit. | `2.99` |
| `UnitStandardCost` | NUMERIC(10, 2) | No | Unit Measure | Landed cost per unit at time of sale. | `1.45` |
| `GrossSalesAmount` | NUMERIC(12, 2) | No | Additive Measure | OrderedQuantity * UnitPrice. | `299.00` |
| `DiscountAmount` | NUMERIC(12, 2) | No | Additive Measure | Commercial customer trade promotion discount. | `15.00` |
| `NetSalesAmount` | NUMERIC(12, 2) | No | Additive Measure | ShippedQuantity * UnitPrice - DiscountAmount. | `278.02` |
| `CostOfGoodsSold` | NUMERIC(12, 2) | No | Additive Measure | ShippedQuantity * UnitStandardCost (COGS). | `142.10` |
| `OrderLineCycleTimeDays`| INT64 | No | Measure | Elapsed days from OrderDate to ShipDate. | `1` |
| `OnTimeInFullFlag` | INT64 | No | Binary Flag | 1 if delivered on-time and 100% in-full, else 0. | `0` |

---

### 2.2 `FactInventorySnapshot`
| Column Name | Data Type | Nullable | Key Type | Business Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SnapshotKey` | INT64 | No | PK | Surrogate key uniquely identifying daily snapshot. | `4920193` |
| `SnapshotDateKey` | INT64 | No | FK (Active) | Snapshot date linking to `DimDate.DateKey`. | `20250630` |
| `SnapshotDate` | DATE | No | Partition Key | BigQuery day partition date. | `2025-06-30` |
| `ProductKey` | INT64 | No | FK (Cluster) | Product revision key linking to `DimProduct`. | `10042` |
| `WarehouseKey` | INT64 | No | FK (Cluster) | Facility key linking to `DimWarehouse`. | `4` |
| `OnHandQuantity` | INT64 | No | Semi-Additive | Physical units present in warehouse bins. | `1420` |
| `ReservedQuantity` | INT64 | No | Semi-Additive | Units allocated to open sales orders awaiting pick. | `320` |
| `AvailableQuantity` | INT64 | No | Semi-Additive | Net uncommitted stock (OnHand - Reserved). | `1100` |
| `InTransitInboundQuantity`| INT64 | No | Semi-Additive | Units in transit from open POs or transfers. | `500` |
| `UnitLandedCost` | NUMERIC(10, 2) | No | Unit Measure | Standard landed unit cost on snapshot date. | `1.45` |
| `InventoryValuation`| NUMERIC(14, 2) | No | Semi-Additive | OnHandQuantity * UnitLandedCost. | `2059.00` |
| `DaysSinceLastMovement`| INT64 | No | Semi-Additive | Consecutive days with zero outward movement. | `14` |
| `IsStockoutFlag` | INT64 | No | Binary Flag | 1 if AvailableQuantity <= 0, else 0. | `0` |
| `IsDeadStockFlag` | INT64 | No | Binary Flag | 1 if DaysSinceLastMovement >= 180, else 0. | `0` |

---

### 2.3 `FactPurchaseOrder`
| Column Name | Data Type | Nullable | Key Type | Business Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `POLineKey` | INT64 | No | PK | Surrogate key uniquely identifying PO line item. | `184920` |
| `PurchaseOrderID` | STRING | No | Degenerate Key | Source ERP purchase order number. | `'PO-2025-1049'` |
| `POLineNumber` | INT64 | No | Attribute | Line number on PO header. | `1` |
| `POCreationDateKey`| INT64 | No | FK (Active) | Order issuance date linking to `DimDate.DateKey`. | `20250501` |
| `PromisedDeliveryDateKey`| INT64| No | FK (Inactive) | Quoted contractual arrival date. | `20250515` |
| `ActualDockReceiptDateKey`| INT64| Yes | FK (Inactive) | Timestamped physical dock arrival date (NULL if open). | `20250517` |
| `SupplierKey` | INT64 | No | FK (Cluster) | Sourcing vendor linking to `DimSupplier`. | `12` |
| `ProductKey` | INT64 | No | FK (Cluster) | Purchased product linking to `DimProduct`. | `10042` |
| `ReceivingWarehouseKey`| INT64 | No | FK (Cluster) | Destination DC linking to `DimWarehouse`. | `4` |
| `BuyerEmployeeKey` | INT64 | No | FK | Purchasing buyer linking to `DimEmployeePlanner`. | `8` |
| `OrderedQuantity` | INT64 | No | Additive Measure | Quantity ordered from vendor. | `2000` |
| `ReceivedQuantity` | INT64 | No | Additive Measure | Quantity received and accepted at dock. | `1950` |
| `RejectedQuantity` | INT64 | No | Additive Measure | Quantity failed quality inspection. | `50` |
| `UnitPurchasePrice` | NUMERIC(10, 2) | No | Unit Measure | Contracted purchase price per unit. | `1.38` |
| `ExtendedPOAmount` | NUMERIC(12, 2) | No | Additive Measure | OrderedQuantity * UnitPurchasePrice. | `2760.00` |
| `PromisedLeadTimeDays`| INT64 | No | Measure | PromisedDate - POCreationDate. | `14` |
| `ActualLeadTimeDays`| INT64 | Yes | Measure | ActualReceiptDate - POCreationDate. | `16` |
| `LeadTimeVarianceDays`| INT64 | Yes | Measure | ActualLeadTimeDays - PromisedLeadTimeDays. | `2` |
| `IsDeliveredOnTimeFlag`| INT64 | No | Binary Flag | 1 if ActualDate <= PromisedDate, else 0. | `0` |
| `IsDeliveredInFullFlag`| INT64 | No | Binary Flag | 1 if ReceivedQty >= OrderedQty, else 0. | `0` |
| `IsSupplierOTIFFlag`| INT64 | No | Binary Flag | 1 if On-Time AND In-Full, else 0. | `0` |
| `POStatus` | STRING | No | Attribute | Current procurement lifecycle status. | `'Completed'` |

---

### 2.4 `FactDemandForecast`
| Column Name | Data Type | Nullable | Key Type | Business Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ForecastKey` | INT64 | No | PK | Surrogate key identifying forecast record. | `304921` |
| `TargetPeriodDateKey`| INT64 | No | FK (Active) | First day of target forecast period. | `20250701` |
| `ForecastGeneratedDateKey`| INT64 | No | FK (Inactive) | Date forecast run was generated. | `20250601` |
| `ProductKey` | INT64 | No | FK (Cluster) | Product key linking to `DimProduct`. | `10042` |
| `WarehouseKey` | INT64 | No | FK (Cluster) | Warehouse location linking to `DimWarehouse`. | `4` |
| `ScenarioKey` | INT64 | No | FK | Simulation scenario linking to `DimScenario`. | `1` |
| `ForecastedQuantity`| INT64 | No | Additive Measure | Consensus projected unit demand. | `3200` |
| `BaselineStatisticalQuantity`| INT64 | No | Additive Measure | Unconstrained algorithmic baseline units. | `3050` |
| `PlannerAdjustmentQuantity`| INT64 | No | Additive Measure | Manual planner override delta units. | `150` |
| `ForecastValue` | NUMERIC(12, 2) | No | Additive Measure | ForecastedQuantity * UnitListPrice. | `9568.00` |
| `ForecastModelVersion`| STRING | No | Attribute | Machine learning / statistical model name. | `'HoltWinters-V2'` |

---

### 2.5 `FactInventoryMovement`
| Column Name | Data Type | Nullable | Key Type | Business Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `MovementKey` | INT64 | No | PK | Surrogate key uniquely identifying movement. | `59201` |
| `MovementTransactionID`| STRING | No | Degenerate Key | Source WMS inventory movement transaction code. | `'MV-991024'` |
| `MovementDateKey` | INT64 | No | FK (Active) | Movement execution date linking to `DimDate`. | `20250618` |
| `ProductKey` | INT64 | No | FK (Cluster) | Transferred product linking to `DimProduct`. | `10042` |
| `OriginWarehouseKey`| INT64 | No | FK (Cluster) | Origin facility linking to `DimWarehouse`. | `1` |
| `DestinationWarehouseKey`| INT64| Yes | FK | Destination facility (NULL for scrap/adjustment). | `4` |
| `ResponsibleEmployeeKey`| INT64 | No | FK | Warehouse supervisor linking to `DimEmployeePlanner`.| `8` |
| `MovementType` | STRING | No | Attribute | Classification: 'Inter-DC Transfer', 'Cycle Count', etc.| `'Inter-DC Transfer'` |
| `MovementQuantity` | INT64 | No | Additive Measure | Quantity transferred (+ for increment, - for decrement).| `500` |
| `MovementValue` | NUMERIC(12, 2) | No | Additive Measure | MovementQuantity * UnitStandardCost. | `725.00` |
| `TransferFreightCost`| NUMERIC(10, 2) | No | Additive Measure | Transportation logistics freight cost incurred. | `120.00` |
| `TransferTransitDays`| INT64 | No | Measure | In-transit duration in calendar days. | `2` |

---

### 2.6 `FactStockout`
| Column Name | Data Type | Nullable | Key Type | Business Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `StockoutEventKey` | INT64 | No | PK | Surrogate key uniquely identifying outage event. | `10291` |
| `StartDateKey` | INT64 | No | FK (Active) | Stockout initiation date linking to `DimDate`. | `20250703` |
| `EndDateKey` | INT64 | No | FK (Inactive) | Stockout recovery date linking to `DimDate`. | `20250707` |
| `StartDate` | DATE | No | Attribute | Start date of continuous zero-stock period. | `2025-07-03` |
| `EndDate` | DATE | No | Attribute | End date of continuous zero-stock period. | `2025-07-07` |
| `ProductKey` | INT64 | No | FK (Cluster) | Out-of-stock product linking to `DimProduct`. | `10042` |
| `WarehouseKey` | INT64 | No | FK (Cluster) | Depleted facility linking to `DimWarehouse`. | `4` |
| `StockoutDurationDays`| INT64 | No | Additive Measure | EndDate - StartDate + 1. | `5` |
| `EstimatedLostDemandUnits`| INT64 | No | Additive Measure | Unfulfilled demand based on historical velocity. | `450` |
| `EstimatedLostRevenueAmount`| NUMERIC(12, 2)| No| Additive Measure| EstimatedLostDemandUnits * UnitListPrice. | `1345.50` |
| `StockoutAttributedReason`| STRING | No | Attribute | Root cause category. | `'Supplier Delayed Inbound'` |
| `SeverityTier` | STRING | No | Attribute | Business severity: 'Critical A', 'Moderate B', etc. | `'Critical A'` |

---

### 2.7 `FactCustomerReturns`
| Column Name | Data Type | Nullable | Key Type | Business Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ReturnLineKey` | INT64 | No | PK | Surrogate key uniquely identifying return item. | `39201` |
| `ReturnID` | STRING | No | Degenerate Key | Source RMA / reverse logistics document number. | `'RMA-2025-0482'` |
| `ReturnDateKey` | INT64 | No | FK (Active) | Return receipt date linking to `DimDate`. | `20250622` |
| `OriginalOrderDateKey`| INT64| No | FK (Inactive) | Date original sales order was placed. | `20250615` |
| `ProductKey` | INT64 | No | FK (Cluster) | Returned product linking to `DimProduct`. | `10042` |
| `ReceivingWarehouseKey`| INT64| No | FK | Return processing facility in `DimWarehouse`. | `4` |
| `CustomerChannelKey`| INT64 | No | FK (Cluster) | Returning customer/channel in `DimCustomerChannel`. | `145` |
| `ReturnedQuantity` | INT64 | No | Additive Measure | Total physical units received back. | `5` |
| `RestockedQuantity` | INT64 | No | Additive Measure | Units passed inspection and returned to saleable stock. | `4` |
| `ScrappedQuantity` | INT64 | No | Additive Measure | Units damaged and disposed of. | `1` |
| `RefundAmount` | NUMERIC(10, 2) | No | Additive Measure | Total monetary reimbursement credited to customer. | `14.95` |
| `ReturnReasonCategory`| STRING | No | Attribute | Cause: 'Defective Item', 'Shipping Damage', etc. | `'Shipping Damage'` |
| `DispositionStatus` | STRING | No | Attribute | Final inventory status: 'Restocked', 'Scrapped'. | `'Restocked'` |

---

### 2.8 `FactSupplierMonthlyPerformance`
| Column Name | Data Type | Nullable | Key Type | Business Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SupplierMonthlyKey`| INT64 | No | PK | Surrogate key uniquely identifying monthly scorecard. | `2491` |
| `YearMonthDateKey` | INT64 | No | FK (Active) | First day of evaluated month linking to `DimDate`. | `20250601` |
| `SupplierKey` | INT64 | No | FK | Vendor key linking to `DimSupplier`. | `12` |
| `YearMonth` | STRING | No | Attribute | Monthly label for display slicers (`YYYY-MM`). | `'2025-06'` |
| `TotalPOCount` | INT64 | No | Additive Measure | Total purchase orders scheduled in month. | `8` |
| `TotalPOLines` | INT64 | No | Additive Measure | Total PO line items scheduled in month. | `24` |
| `TotalOrderedQuantity`| INT64 | No | Additive Measure | Sum of units ordered from vendor across lines. | `48000` |
| `TotalReceivedQuantity`| INT64| No | Additive Measure | Sum of units successfully received at dock. | `46500` |
| `TotalRejectedQuantity`| INT64| No | Additive Measure | Sum of units rejected at receiving inspection. | `1500` |
| `TotalSpendAmount` | NUMERIC(14, 2) | No | Additive Measure | Total committed purchasing spend in month. | `66240.00` |
| `OnTimePOCount` | INT64 | No | Additive Measure | PO lines arriving on or before promised delivery date. | `21` |
| `InFullPOCount` | INT64 | No | Additive Measure | PO lines with 100% of ordered units delivered. | `20` |
| `OTIFLineCount` | INT64 | No | Additive Measure | PO lines arriving both on-time and in-full. | `19` |
| `OTIFRatePct` | NUMERIC(5, 2) | No | Non-Additive Ratio | (OTIFLineCount / TotalPOLines) * 100%. | `79.17` |
| `AverageLeadTimeDays`| NUMERIC(6, 2) | No | Non-Additive Avg | Mean dock receipt lead time in days. | `15.42` |
| `LeadTimeStdDevDays`| NUMERIC(6, 2) | No | Non-Additive StdDev | Standard deviation of dock receipt lead times. | `4.18` |
| `LateDeliveryCount` | INT64 | No | Additive Measure | PO lines delivered past contractual promised date. | `3` |
| `LineFillRatePct` | NUMERIC(5, 2) | No | Non-Additive Ratio | (TotalReceivedQuantity / TotalOrderedQuantity) * 100%. | `96.88` |
| `SupplierMonthlyRiskRating`| STRING | No| Attribute | Algorithmic risk tier: 'Low', 'Moderate', 'Critical'. | `'Moderate Risk'` |
