# ADR-008: Slowly Changing Dimension (SCD) Type 2 Strategy

## Status
Approved

## Date
2026-09-10

## Context
In enterprise retail and FMCG supply chains, dimension attributes undergo substantive operational changes over time:
- Standard landed unit costs fluctuate due to raw material inflation, freight rate changes, and supplier renegotiations.
- Products are reassigned to different brand categories, merchandising subcategories, or product managers.
- SKUs are re-allocated between primary domestic and international vendors.

If historical dimension attributes are overwritten (SCD Type 1), historical financial and inventory calculations (such as historical COGS, past inventory valuations, and historical supplier attribution) become permanently distorted. A formal Slowly Changing Dimension (SCD) strategy is required.

## Decision
We implement a **Slowly Changing Dimension Type 2 (SCD Type 2)** pattern on the primary product dimension: **`DimProduct`**.

Technical implementation specification for `DimProduct`:
1. **Key Architecture:**
   - **`ProductKey` (Surrogate Key):** Integer surrogate key (`INT64`) uniquely identifying each distinct version of a product record over time. Used as the foreign key in all fact tables.
   - **`ProductSKU` (Natural / Business Key):** The stable alphanumeric business identifier (e.g., `SKU-10492`) assigned by the ERP/PLM source system.
2. **Temporal Tracking Columns:**
   - **`EffectiveDate` (DATE):** The start date when this version of the product attributes became active.
   - **`ExpiryDate` (DATE):** The end date when this version was superseded (set to a distant future sentinel date such as `9999-12-31` for active records).
   - **`IsCurrent` (BOOLEAN):** Binary flag (`TRUE` for the current active version, `FALSE` for superseded historical versions).
3. **Tracked SCD Type 2 Attributes:**
   - `UnitStandardCost` (Landed unit cost)
   - `CategoryName` / `SubcategoryName` (Merchandising hierarchy)
   - `PrimarySupplierKey` (Primary sourcing vendor)
   - `HandlingProfile` (Standard, Perishable, Hazardous, Bulk)
4. **Fact Table Binding Rule:**
   - Fact tables join to `DimProduct` on `ProductSKU` where the transaction/snapshot date falls between `EffectiveDate` and `ExpiryDate`, retrieving the specific `ProductKey` representing the state of the product at the time of the transaction:
     ```sql
     ON fact.ProductSKU = dim.ProductSKU
     AND fact.TransactionDate >= dim.EffectiveDate
     AND fact.TransactionDate < dim.ExpiryDate
     ```
5. **dbt Implementation Mechanism:**
   - Managed via dbt snapshots (`dbt snapshot`) using `check` or `timestamp` strategy, ensuring versioning logic is fully automated and version-controlled.

## Alternatives Considered
- **SCD Type 1 (Overwrite In-Place):** Overwrites previous values when changes occur. Rejected for `DimProduct` because overwriting unit costs retroactively recalculates historical inventory valuations and COGS, violating basic financial accounting principles. (SCD Type 1 remains acceptable for low-impact operational attributes like warehouse contact names or customer phone numbers).
- **SCD Type 3 (Previous / Current Columns):** Storing previous and current values in the same row. Rejected because it only tracks a single historical change and fails to support multi-year historical auditing across multiple price revisions.

## Consequences

### Positive
- True historical fidelity: Financial valuations, margin calculations, and inventory balances reflect the exact cost and category structure in effect when the event occurred.
- Point-in-time vs. Current-view analysis: Planners can evaluate historical performance either "as-was" (using transaction-bound surrogate keys) or "as-is" (joining to `IsCurrent = TRUE`).

### Considerations & Risks
- Fact table generation and dbt loading pipelines must perform range-based lookups (`TransactionDate BETWEEN EffectiveDate AND ExpiryDate`) to assign correct surrogate keys.
- Dimension row count increases as product revisions accumulate (though for thousands of SKUs, total row count remains negligible for BigQuery and VertiPaq).

## Future Scalability Implications
If supplier contract terms or vendor tiers require historical tracking in the future, the same SCD Type 2 framework can be seamlessly extended to `DimSupplier` without altering the surrounding data flow.
