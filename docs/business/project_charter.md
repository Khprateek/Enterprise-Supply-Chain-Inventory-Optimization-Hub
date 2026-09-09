# Project Charter: Enterprise Supply Chain & Inventory Optimization Hub

## 1. Executive Summary & Background
In high-volume retail and Fast-Moving Consumer Goods (FMCG) operations, maintaining optimal inventory balance is a critical operational challenge. Inefficient inventory management leads to two severe failure modes:
1. **Stockouts:** Lost revenue, damaged customer relationships, and eroded brand loyalty.
2. **Excess Stock:** Working capital tied up in slow-moving or obsolete inventory, increased holding costs, and elevated risk of write-downs.

The **Enterprise Supply Chain & Inventory Optimization Hub** project aims to establish a centralized, enterprise-grade analytics foundation that connects inventory levels, sales velocity, purchasing pipelines, and supplier reliability to drive data-informed replenishment and working-capital efficiency.

## 2. Business Objectives & Key Questions
The platform is designed to provide clear, actionable answers to core operational questions:

1. **Current Inventory Position:** What inventory do we currently have across all nodes in the network?
2. **Overstock Exposure:** Where is inventory overstocked, and which SKUs/locations represent the greatest trapped capital?
3. **Stockout Incidents & Risk:** Where are stockout events actively occurring or imminent?
4. **Working Capital Drivers:** Which specific SKUs drive the highest working-capital exposure?
5. **Demand & Forecast Accuracy:** Which products have poor forecast accuracy or high demand volatility?
6. **Supplier Reliability:** Which suppliers are consistently causing lead-time delays or variability?
7. **Dynamic Safety Stock:** What should recommended safety stock levels be under varying demand and lead-time volatility?
8. **Replenishment Triggering:** When should purchase replenishment orders be triggered for each SKU-warehouse pair?
9. **Actionable Planner Queue:** Which SKUs require immediate intervention from supply chain planners today?
10. **Multi-Dimensional Variance:** How does performance vary across regions, distribution centers, product categories, suppliers, and fiscal periods?
11. **Scenario & Sensitivity Analysis:** What are the working capital and service level impacts if demand swings, lead times shift, or service level targets change?

## 3. Operational Domain & Scope
The project models an enterprise-scale multinational retail/FMCG distribution network covering:
- **Geographic Coverage:** Multiple operational regions and international markets.
- **Logistics Nodes:** Multiple regional Distribution Centers (DCs) and fulfillment warehouses.
- **Procurement Ecosystem:** Broad supplier network with varying contract terms, lead times, and reliability profiles.
- **Product Hierarchy:** Thousands of SKUs organized across categories, subcategories, and handling profiles (e.g., standard, perishable, bulk).
- **Commercial Channels:** B2B wholesale, retail stores, and direct e-commerce fulfillment channels.
- **Core Business Processes:**
  - Inbound purchase orders and line-item receipts
  - Outbound sales orders and customer fulfillment
  - Daily/periodic physical inventory snapshots
  - Internal inventory movements and transfers between warehouses
  - Replenishment forecasts and target safety stock recommendations
  - Stockout incidents, lost sales, and customer returns

## 4. Analytical Scale & Data Realism Requirements
To reflect true enterprise conditions, the analytical foundation must satisfy strict volume and fidelity criteria:
- **Target Fact Volume:** Minimum of 5 million rows; target of 10M+ rows across core fact tables.
- **Dimension Realism:** Sensibly sized dimension tables reflecting realistic catalog sizes (thousands of SKUs, dozens of warehouses/suppliers).
- **Data Integrity:** Strict avoidance of random noise; datasets must reflect authentic demand seasonality, regional growth differences, supplier delivery distributions, and operational correlation.

## 5. Stakeholders & Personas
- **Supply Chain Planners:** Require operational worklists, reorder triggers, and safety-stock recommendations.
- **Inventory & Warehouse Managers:** Require visibility into warehouse capacity, stock aging, and stock transfers.
- **Procurement & Sourcing Specialists:** Require supplier scorecarding, lead-time variance tracking, and on-time/in-full (OTIF) metrics.
- **Executive Operations Leadership (VP Supply Chain / COO):** Require macro-level working capital KPIs, inventory turnover trends, and network-wide risk exposure.

## 6. Constraints & Project Boundary (Current Phase)
- **Phase 1 Boundary:** This charter documents project goals and scope. No production schemas, mock datasets, DAX measures, or dashboards are deployed at this initial stage.
- **Technology Alignment:** Architected for Kimball dimensional modeling targeting Google BigQuery, dbt transformations, and Microsoft Power BI reporting.
