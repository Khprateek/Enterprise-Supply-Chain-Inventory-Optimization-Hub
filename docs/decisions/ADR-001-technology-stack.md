# ADR-001: Core Technology Stack & Local-First Strategy

## Status
Approved

## Date
2026-09-10

## Context
The Enterprise Supply Chain & Inventory Optimization Hub requires an enterprise-grade data platform capable of processing multi-million-row fact datasets (5M–10M+ rows across major fact tables), executing Kimball-style dimensional transformations, maintaining business logic consistency, and serving interactive executive and operational dashboards.

We must define the core technology stack and establish a development approach that balances enterprise architectural fidelity with manageable local iteration speed and cost control.

## Decision
We select the following core technology stack:

1. **Analytical Data Warehouse: Google BigQuery**
   - **Selection:** Google BigQuery is selected as the primary analytical warehouse.
   - **Rationale:** Serverless infrastructure, separation of compute and storage, native support for partitioning (date-based) and clustering (SKU/warehouse keys), standard SQL support, and first-class integration with Power BI.
   - **Alternative Considered:** Snowflake was evaluated as a viable alternative; however, BigQuery is the preferred warehouse specified in the project context, and local environment checks confirm dbt-bigquery and Python google-cloud-bigquery libraries are already installed.

2. **Data Transformation & Modeling: dbt (dbt-core / dbt-bigquery) + SQL**
   - **Selection:** dbt is selected as the primary transformation framework.
   - **Rationale:** Supports modular SQL development, automated dependency management (DAGs), built-in testing (schema tests, referential integrity), documentation generation, and version-controlled transformation logic.

3. **Semantic Modeling & BI: Microsoft Power BI Desktop**
   - **Selection:** Microsoft Power BI Desktop is selected as the reporting and semantic modeling tool.
   - **Rationale:** Industry-standard enterprise BI, high-performance in-memory engine (VertiPaq) for dimensional star schemas, expressive DAX calculation capabilities for complex inventory math (reorder points, safety stock, turnover), and existing local installation (Windows Store version 2.157).

4. **Data Generation & Orchestration Scripting: Python 3.12**
   - **Selection:** Python 3.12 with Pandas, NumPy, PyArrow, and BigQuery client libraries.
   - **Rationale:** High-performance vectorized generation of realistic, correlated multi-million-row synthetic supply chain datasets, schema validation, and local-to-cloud loading automation.

5. **Local-First Initial Implementation Strategy**
   - **Selection:** Keep early-phase implementation local wherever possible.
   - **Rationale:** Prototyping data models, developing generation scripts, and validating schema structures locally avoids unnecessary cloud costs, quota limits, or network latency during foundational stages. Cloud ingestion into BigQuery will occur once schemas and generation pipelines are validated.

## Consequences

### Positive
- Direct alignment with project requirements and verified local capabilities.
- Zero initial cloud costs during design, prototyping, and schema validation.
- Clean separation of concerns between data storage (BigQuery), transformation (dbt), and presentation (Power BI).
- Standardized, repeatable transformation pipelines managed in Git.

### Considerations & Risks
- Cloud deployment will require valid GCP credentials / service account configuration when ready to load BigQuery.
- Power BI Desktop on Windows requires explicit data connectivity patterns (DirectQuery or Import) optimized for multi-million-row datasets.
