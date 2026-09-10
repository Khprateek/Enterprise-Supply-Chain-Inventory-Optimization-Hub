# ADR-004: Adoption of Kimball Dimensional Modeling Architecture

## Status
Approved

## Date
2026-09-10

## Context
The Supply Chain & Inventory Optimization Hub must deliver intuitive, high-performance reporting across disparate business processes (sales fulfillment, daily warehouse inventory, vendor procurement, demand forecasting, stockouts, movements, and customer returns). 

Without a disciplined dimensional design, analytics systems degenerate into either highly normalized 3NF relational schemas (which suffer from slow, complex multi-table joins) or giant unorganized flat tables (which bloat memory, cause metric duplication, and break cross-process drill-through).

## Decision
We adopt the **Kimball Dimensional Modeling methodology**, implementing a conformed Star Schema across all business processes.

Core modeling rules:
1. **Fact Tables Organized by Business Process:**
   - Transactional Facts: `FactSales`, `FactInventoryMovement`, `FactCustomerReturns`.
   - Periodic Snapshot Facts: `FactInventorySnapshot` (Daily grain: SKU ? Warehouse ? Date), `FactDemandForecast`.
   - Accumulating / Transactional Facts: `FactPurchaseOrder`.
   - Derived Event Facts: `FactStockout` (Consolidated outage episodes).
   - Materialized Analytical Marts: `FactSupplierMonthlyPerformance`.
2. **Conformed Dimensions:**
   - Shared across all fact tables to ensure consistent slicing: `DimDate`, `DimProduct`, `DimSupplier`, `DimWarehouse`, `DimRegion`, `DimCustomerChannel`, `DimEmployeePlanner`, `DimScenario`.
3. **Surrogate Keys:**
   - Every dimension utilizes an integer surrogate key (`<Dimension>Key`) independent of source business keys.
4. **Pure Star Schemas:**
   - Snowflaking is explicitly avoided in the presentation model. Dimension hierarchies (e.g., Category -> Subcategory -> Product) are fully denormalized into their respective dimension tables.
5. **No Monolithic Flat Tables:**
   - Power BI reports will consume the dimensional star schema directly, allowing VertiPaq columnar dictionary encoding to optimize memory.

## Alternatives Considered
- **Third Normal Form (3NF) Relational Architecture (Inmon Model):** Excellent for operational OLTP systems; however, writing analytical queries and DAX measures across dozens of normalized tables requires extensive joins, degrades VertiPaq compression, and creates cognitive overload for business users.
- **Single Flat Denormalized Wide Table (OBT - One Big Table):** Simplifies initial single-process queries, but breaks when analyzing cross-process dynamics (e.g., joining sales transactions with daily inventory balances creates astronomical row duplication and Cartesian explosion).

## Consequences

### Positive
- Cross-process drill-through: Planners can seamlessly compare sales demand, inventory balances, and inbound PO pipeline for the same SKU and warehouse.
- Maximum VertiPaq performance: Low-cardinality dimension tables compress efficiently, and fact tables store only narrow integer foreign keys and additive/semi-additive numeric measures.
- Clear mental model for report authors and business users.

### Considerations & Risks
- Requires disciplined upfront grain definition for every fact table.
- Dimension updates (e.g., product attribute changes) must be managed systematically using slowly changing dimension (SCD) patterns.

## Future Scalability Implications
Conformed dimensions allow new operational processes (e.g., transportation logistics, manufacturing shop-floor execution) to be added as new fact tables without altering or breaking existing reports.
