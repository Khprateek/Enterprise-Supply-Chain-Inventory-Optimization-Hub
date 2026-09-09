# Enterprise Supply Chain & Inventory Optimization Hub

## Overview
The **Enterprise Supply Chain & Inventory Optimization Hub** is an end-to-end analytics platform designed for a multinational retail/FMCG organization. Its primary objective is to empower supply chain planners, inventory managers, and operations executives with actionable visibility into stock levels, stockout risks, overstocked capital, supplier lead-time reliability, and optimal replenishment parameters.

## Core Objectives
- **Inventory Visibility:** Track on-hand stock, pipeline orders, and inventory distribution across regional distribution centers and warehouses.
- **Capital & Risk Optimization:** Identify working capital trapped in excess inventory and mitigate stockouts on high-velocity SKUs.
- **Supplier & Lead-Time Analytics:** Measure supplier delivery reliability and lead-time variability.
- **Replenishment Decision Support:** Calculate dynamic safety stock, reorder points, and automated planner alerts.
- **Executive & Operational Reporting:** Deliver role-tailored dashboards and self-service analytics via Microsoft Power BI.

## Technology Stack
- **Data Warehouse:** Google BigQuery (preferred analytical engine for partitioning, clustering, and scalable queries)
- **Data Transformation:** dbt (dbt-core / dbt-bigquery) and standard SQL
- **Semantic Modeling & BI:** Microsoft Power BI Desktop (Kimball star schema, DAX measures)
- **Local Engineering & Scripting:** Python 3.12 (Pandas, PyArrow, Google Cloud BigQuery client)
- **Version Control:** Git & GitHub

## Repository Structure
`
supply-chain-inventory-optimization/
│
├── README.md                           # Project overview, architecture, and setup instructions
├── PROJECT_CONTEXT.md                  # Comprehensive business context, domain definitions, and requirements
├── .gitignore                          # Git ignore rules for data, cache, and secrets
│
├── docs/                               # Project documentation
│   ├── architecture/                   # Architecture blueprints and design specifications
│   │   └── architecture_overview.md
│   ├── business/                       # Business requirements, project charter, and KPI definitions
│   │   └── project_charter.md
│   ├── data-model/                     # Dimensional models, entity relationships, and dictionary
│   ├── decisions/                      # Architecture Decision Records (ADRs)
│   │   └── ADR-001-technology-stack.md
│   └── testing/                        # Test plans, data quality rules, and validation reports
│
├── data/                               # Local data assets (not committed to VCS)
│   ├── raw/                            # Ingested raw source data files
│   ├── staging/                        # Staged / normalized local files
│   └── sample/                         # Small deterministic sample records for unit testing
│
├── dbt/                                # dbt project, models, seeds, tests, and documentation
│
├── sql/                                # Standalone SQL scripts (DDL, views, analytical queries)
│
├── python/                             # Python data generation, validation, and pipeline utilities
│
├── powerbi/                            # Power BI template/report files, measure definitions, DAX scripts
│
├── tests/                              # Automated data quality tests and unit test scripts
│
└── scripts/                            # Operational, setup, and orchestration scripts
`

## Current Project Phase
- **Phase:** Project Initialization (Phase 1)
- **Status:** Initial repository structure, technical documentation, and environment configuration established.
- **Next Steps:** Conceptual and logical data modeling, followed by synthetic data generation strategy definition.

## Setup & Prerequisites
- **OS:** Windows 11 / Linux / macOS
- **Python:** 3.12+
- **Git:** 2.40+
- **dbt:** dbt-core and dbt-bigquery
- **Power BI Desktop:** Required for consuming data models and reports
