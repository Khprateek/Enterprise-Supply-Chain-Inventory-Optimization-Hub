# PySpark Implementation Roadmap: Enterprise Supply Chain & Inventory Optimization Hub

## Executive Summary

Currently, the project leverages a robust modern data stack: **Python** (for data generation), **BigQuery** (Data Warehouse), **dbt** (SQL-based transformations), and **Power BI** (Reporting), all orchestrated by **Airflow**. 

In the initial architecture (per `ADR-005`), PySpark was bypassed for core ETL because BigQuery and dbt are highly efficient for standard SQL transformations on 5M-10M rows. However, introducing **PySpark** unlocks next-level enterprise capabilities that are difficult or impossible to achieve with SQL alone.

This roadmap outlines a phased approach to integrating PySpark, focusing on its core strengths: **Massive parallel processing, Machine Learning (MLlib), Complex non-SQL logic (Graph processing), and Real-time streaming**.

---

## Phase 1: Infrastructure & Architecture Setup
*Goal: Establish the PySpark execution environment and integrate it with the existing Google Cloud ecosystem.*

### 1.1 Choose the Execution Environment
- **Option A: Google Cloud Dataproc** (Recommended): Native managed Spark on GCP. Integrates perfectly with BigQuery and Google Cloud Storage (GCS).
- **Option B: Serverless Spark on BigQuery**: Good for running Spark jobs directly from BigQuery without managing clusters.
- **Option C: Local/Dockerized Spark**: For local development and testing before cloud deployment.

### 1.2 Setup BigQuery Connector
- Integrate the `spark-bigquery-connector` to allow PySpark to read from and write to BigQuery seamlessly.
- **Action**: Add `.jar` dependencies to the Spark configuration.

### 1.3 Local Development Setup
- Install PySpark locally (`pip install pyspark`).
- Update the project structure:
  ```text
  â”œâ”€â”€ pyspark_jobs/
  â”‚   â”œâ”€â”€ __init__.py
  â”‚   â”œâ”€â”€ data_generation/
  â”‚   â”œâ”€â”€ ml_models/
  â”‚   â””â”€â”€ complex_transforms/
  ```

---

## Phase 2: Scaling Data Generation (Replacing Pandas)
*Goal: Upgrade the current Python synthetic data generators to PySpark to scale from 10M rows to 100M+ or 1B+ rows for true enterprise load testing.*

### 2.1 Refactor Master Orchestrator
- Currently, `orchestrator.py` uses `pandas` and `numpy`. These run on a single node and will hit Out-Of-Memory (OOM) errors at massive scales.
- **Action**: Rewrite the generators (e.g., `generate_sales.py`, `generate_movements.py`) using PySpark DataFrames.

### 2.2 Distributed Data Generation
- Use PySpark's parallelization (`spark.range()`) to generate massive datasets distributed across a cluster.
- Utilize Spark SQL functions (`pyspark.sql.functions.rand()`) for synthetic randomization.
- **Action**: Output data directly to GCS in partitioned `.parquet` format for BigQuery external table ingestion.

---

## Phase 3: Advanced Analytics & Machine Learning
*Goal: Introduce predictive capabilities using PySpark MLlib that cannot be done in standard SQL (dbt).*

### 3.1 AI-Driven Demand Forecasting
- Replace static forecast rules with actual Machine Learning.
- **Data Prep**: Use PySpark to read historical sales and inventory data from BigQuery.
- **Modeling**: Implement Time-Series forecasting or regression models (e.g., Random Forest Regressor) using `pyspark.ml` to predict `forecast_quantity` at the SKU-Facility level.
- **Writeback**: Write the predictions back to a new BigQuery table (e.g., `ml_demand_forecast`).

### 3.2 Inventory Optimization & Safety Stock
- Calculate dynamic safety stock levels based on demand volatility and supplier lead time standard deviations using complex statistical functions in PySpark.

### 3.3 Anomaly Detection
- Implement clustering algorithms (like K-Means) to detect anomalous supply chain events (e.g., fraudulent returns, abnormal shipping delays).

---

## Phase 4: Complex Data Processing (Beyond SQL)
*Goal: Handle complex supply chain logic that is brittle or slow in dbt/SQL.*

### 4.1 Bill of Materials (BOM) Explosion
- If the project expands to manufacturing, SQL recursive CTEs for BOMs can be slow and complex. PySpark (and GraphFrames) can process recursive graph structures easily.

### 4.2 Network Routing Optimization
- Calculate the most optimal warehouse to fulfill an order from, based on geographical distance and current inventory. This requires complex iterative logic well-suited for PySpark.

### 4.3 (Optional) Real-Time Streaming
- If IoT sensors (truck GPS, warehouse scanners) are introduced, use **Spark Structured Streaming** to read from Kafka/PubSub, process events in real-time, and append to BigQuery.

---

## Phase 5: Airflow Orchestration Integration
*Goal: Seamlessly trigger PySpark jobs from the existing Apache Airflow setup.*

### 5.1 Airflow Operators
- Introduce `DataprocSubmitJobOperator` (if using Dataproc) or `SparkSubmitOperator` into the Airflow DAGs.
- **DAG Flow**:
  1. `generate_raw_data` (PySpark Job)
  2. `load_to_bigquery` (GCS to BQ Operator)
  3. `run_dbt_models` (DbtRunOperator)
  4. `run_ml_forecast` (PySpark Job reading from BQ, writing to BQ)

---

## Next Steps for Immediate Implementation:
1. **Create the `pyspark_jobs` directory** in your repository.
2. **Pick one module** to rewrite first. A great starting point is migrating the **Demand Forecasting** script to use PySpark, as it naturally fits ML and complex analytics.
3. Let me know which step you would like to tackle first, and we can begin pair-programming the PySpark code!
