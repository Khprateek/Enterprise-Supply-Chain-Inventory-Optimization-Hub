"""
dag_supply_chain_with_pyspark.py
=================================
Extended Airflow DAG — Phase 1 PySpark Integration
Enterprise Supply Chain & Inventory Optimization Hub

This DAG extends the original 'dag_supply_chain_daily_elt' with PySpark jobs
submitted to Google Cloud Dataproc.

Pipeline stages:
  1. [SENSOR]   Verify raw Parquet files have landed in GCS
  2. [SPARK]    (Optional) Run PySpark data-quality pre-check job on raw data
  3. [BIGQUERY] Sync BigQuery external table partitions
  4. [dbt]      Run dbt transformation pipeline
  5. [dbt]      Run dbt automated test suite
  6. [SPARK]    Run PySpark ML demand-forecast job (writes to supply_chain_ml dataset)
  7. [POWERBI]  Trigger Power BI incremental semantic model refresh

Schedule: Daily @ 02:00 UTC (after raw data lands from previous day)
SLA: < 6.0 hours end-to-end

Note on Dataproc operators:
  DataprocSubmitJobOperator submits the PySpark job to the existing cluster
  defined in conf/gcp/dataproc_cluster.yaml and waits for it to complete.
  If the cluster is auto-deleted (idle TTL), create it first with:
    python scripts/create_dataproc_cluster.py --action create
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectsWithPrefixExistenceSensor
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator
from airflow.providers.http.operators.http import SimpleHttpOperator

# ─────────────────────────────────────────────────────────────────────────────
# Airflow Variables (set in Airflow UI or via airflow variables CLI)
# ─────────────────────────────────────────────────────────────────────────────
# var.value.GCP_PROJECT_ID          -> your GCP project
# var.value.GCP_REGION              -> dataproc cluster region (e.g. us-central1)
# var.value.GCS_RAW_LANDING_BUCKET  -> bucket with raw Parquet
# var.value.GCS_TEMP_BUCKET         -> temp bucket for Spark-BQ connector
# var.value.DATAPROC_CLUSTER_NAME   -> cluster name from dataproc_cluster.yaml
# var.value.DBT_PROJECT_DIR         -> filesystem path to dbt project
# var.value.GCP_KEYFILE_PATH        -> service account key path on Airflow worker
# var.value.POWERBI_WORKSPACE_ID    -> Power BI workspace GUID
# var.value.POWERBI_DATASET_ID      -> Power BI dataset GUID

default_args = {
    "owner": "supply-chain-analytics",
    "depends_on_past": False,
    "email": ["supply-chain-alerts@enterprise-hub.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=120),  # Increased for Spark jobs
}

with DAG(
    dag_id="dag_supply_chain_with_pyspark",
    default_args=default_args,
    description="Daily ELT + PySpark jobs: GCS → Dataproc → BigQuery → dbt → Power BI",
    schedule_interval="0 2 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["supply_chain", "bigquery", "dbt", "pyspark", "dataproc", "powerbi"],
) as dag:

    start = EmptyOperator(task_id="pipeline_start")

    # ── Stage 1: GCS sensor ──────────────────────────────────────────────────
    check_gcs_raw_landing = GCSObjectsWithPrefixExistenceSensor(
        task_id="check_gcs_raw_landing",
        bucket="{{ var.value.GCS_RAW_LANDING_BUCKET | default('sc-analytics-raw-landing') }}",
        prefix="raw/",
        mode="reschedule",
        poke_interval=60,
        timeout=1800,
    )

    # ── Stage 2: PySpark raw data pre-check (Phase 1 baseline validation job) ─
    # This is a lightweight job that reads raw Parquet from GCS and validates
    # row counts and null checks before loading into BigQuery.
    # In Phase 2 this will be replaced by the full data generation job.
    pyspark_raw_validation = DataprocSubmitJobOperator(
        task_id="pyspark_raw_data_validation",
        job={
            "reference": {"project_id": "{{ var.value.GCP_PROJECT_ID | default('supply-chain-analytics-hub') }}"},
            "placement": {
                "cluster_name": "{{ var.value.DATAPROC_CLUSTER_NAME | default('sc-hub-spark-cluster') }}"
            },
            "pyspark_job": {
                "main_python_file_uri": (
                    "gs://{{ var.value.GCS_RAW_LANDING_BUCKET | default('sc-analytics-raw-landing') }}"
                    "/spark_jobs/raw_data_validator.py"
                ),
                "args": [
                    "--project={{ var.value.GCP_PROJECT_ID | default('supply-chain-analytics-hub') }}",
                    "--input-bucket={{ var.value.GCS_RAW_LANDING_BUCKET | default('sc-analytics-raw-landing') }}",
                    "--temp-bucket={{ var.value.GCS_TEMP_BUCKET | default('sc-analytics-spark-temp') }}",
                    "--execution-date={{ ds }}",
                ],
                "python_file_uris": [],
                "jar_file_uris": [
                    "gs://spark-lib/bigquery/spark-bigquery-with-dependencies_2.12-0.36.1.jar"
                ],
                "properties": {
                    "spark.sql.adaptive.enabled": "true",
                },
            },
        },
        region="{{ var.value.GCP_REGION | default('us-central1') }}",
        project_id="{{ var.value.GCP_PROJECT_ID | default('supply-chain-analytics-hub') }}",
    )

    # ── Stage 3: Sync BigQuery external tables ───────────────────────────────
    sync_bigquery_raw_tables = BigQueryInsertJobOperator(
        task_id="sync_bigquery_raw_tables",
        configuration={
            "query": {
                "query": """
                    CALL `{{ var.value.GCP_PROJECT_ID | default('supply-chain-analytics-hub') }}.raw_supply_chain.refresh_external_partitions`();
                """,
                "useLegacySql": False,
            }
        },
    )

    # ── Stage 4: dbt run ─────────────────────────────────────────────────────
    dbt_run = BashOperator(
        task_id="dbt_run_transformations",
        bash_command="""
            cd {{ var.value.DBT_PROJECT_DIR | default('/opt/dbt') }} && \
            dbt run --profiles-dir . --target prod --select staging intermediate marts
        """,
        env={
            "GCP_PROJECT_ID": "{{ var.value.GCP_PROJECT_ID | default('supply-chain-analytics-hub') }}",
            "GCP_KEYFILE_PATH": "{{ var.value.GCP_KEYFILE_PATH | default('/opt/dbt/credentials/sa_dbt.json') }}",
        },
    )

    # ── Stage 5: dbt test ────────────────────────────────────────────────────
    dbt_test = BashOperator(
        task_id="dbt_test_suite",
        bash_command="""
            cd {{ var.value.DBT_PROJECT_DIR | default('/opt/dbt') }} && \
            dbt test --profiles-dir . --target prod
        """,
        env={
            "GCP_PROJECT_ID": "{{ var.value.GCP_PROJECT_ID | default('supply-chain-analytics-hub') }}",
            "GCP_KEYFILE_PATH": "{{ var.value.GCP_KEYFILE_PATH | default('/opt/dbt/credentials/sa_dbt.json') }}",
        },
    )

    # ── Stage 6: PySpark ML forecast job (placeholder for Phase 3) ───────────
    # This task submits the demand forecasting MLlib job to Dataproc.
    # The actual job script (pyspark_jobs/ml_models/demand_forecast.py) will
    # be built in Phase 3. For now this is commented out — uncomment when ready.
    #
    # pyspark_ml_forecast = DataprocSubmitJobOperator(
    #     task_id="pyspark_ml_demand_forecast",
    #     job={
    #         "reference": {"project_id": "{{ var.value.GCP_PROJECT_ID }}"},
    #         "placement": {"cluster_name": "{{ var.value.DATAPROC_CLUSTER_NAME }}"},
    #         "pyspark_job": {
    #             "main_python_file_uri": "gs://.../spark_jobs/demand_forecast.py",
    #             "jar_file_uris": [
    #                 "gs://spark-lib/bigquery/spark-bigquery-with-dependencies_2.12-0.36.1.jar"
    #             ],
    #         },
    #     },
    #     region="{{ var.value.GCP_REGION | default('us-central1') }}",
    #     project_id="{{ var.value.GCP_PROJECT_ID }}",
    # )

    # ── Stage 7: Power BI refresh ────────────────────────────────────────────
    trigger_powerbi_refresh = SimpleHttpOperator(
        task_id="trigger_powerbi_refresh",
        http_conn_id="powerbi_api",
        endpoint="/v1.0/myorg/groups/{{ var.value.POWERBI_WORKSPACE_ID | default('sc-hub-workspace') }}/datasets/{{ var.value.POWERBI_DATASET_ID | default('sc-hub-semantic-model') }}/refreshes",
        method="POST",
        headers={"Content-Type": "application/json"},
        data='{"notifyOption": "MailOnFailure"}',
    )

    end = EmptyOperator(task_id="pipeline_complete")

    # ── Task dependency graph ────────────────────────────────────────────────
    #
    #  start
    #    └─► check_gcs_raw_landing
    #          └─► pyspark_raw_validation   (Dataproc Spark)
    #                └─► sync_bigquery_raw_tables
    #                      └─► dbt_run
    #                            └─► dbt_test
    #                                  └─► trigger_powerbi_refresh
    #                                            └─► end
    #
    (
        start
        >> check_gcs_raw_landing
        >> pyspark_raw_validation
        >> sync_bigquery_raw_tables
        >> dbt_run
        >> dbt_test
        >> trigger_powerbi_refresh
        >> end
    )
