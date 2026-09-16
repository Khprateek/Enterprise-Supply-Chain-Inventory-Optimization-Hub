"""
Apache Airflow Production Reference DAG: Enterprise Supply Chain & Inventory Optimization Hub
Schedule: Daily @ 02:00 UTC (0 2 * * *)
SLA: < 6.0 Hours end-to-end latency

Orchestration Pipeline Stages:
1. Validate incoming raw Parquet landing files in Google Cloud Storage.
2. Trigger BigQuery external table partition synchronization.
3. Execute dbt transformation pipeline (staging -> intermediate -> marts).
4. Run dbt automated data testing suite (173 assertions).
5. Trigger Power BI REST API semantic model incremental refresh.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectsWithPrefixExistenceSensor
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.http.operators.http import SimpleHttpOperator

default_args = {
    "owner": "supply-chain-analytics",
    "depends_on_past": False,
    "email": ["supply-chain-alerts@enterprise-hub.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=60),
}

with DAG(
    dag_id="dag_supply_chain_daily_elt",
    default_args=default_args,
    description="Daily automated ELT orchestration: GCS -> BigQuery -> dbt Core -> Power BI",
    schedule_interval="0 2 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["supply_chain", "bigquery", "dbt", "powerbi", "inventory"],
) as dag:

    start = EmptyOperator(task_id="pipeline_start")

    # Stage 1: Sensor to verify raw daily Parquet files in Google Cloud Storage
    check_gcs_raw_landing = GCSObjectsWithPrefixExistenceSensor(
        task_id="check_gcs_raw_landing",
        bucket="{{ var.value.GCP_RAW_LANDING_BUCKET | default('sc-analytics-raw-landing') }}",
        prefix="raw/",
        mode="reschedule",
        poke_interval=60,
        timeout=1800,
    )

    # Stage 2: Synchronize BigQuery External Tables & Partitions
    sync_bigquery_raw_tables = BigQueryInsertJobOperator(
        task_id="sync_bigquery_raw_tables",
        configuration={
            "query": {
                "query": """
                    -- Refresh external table metadata partitions for daily snapshot and sales
                    CALL `{{ var.value.GCP_PROJECT_ID | default('supply-chain-analytics-hub') }}.raw_supply_chain.refresh_external_partitions`();
                """,
                "useLegacySql": False,
            }
        },
    )

    # Stage 3: Execute dbt transformation pipeline
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

    # Stage 4: Run dbt Automated Data Quality & Referential Integrity Tests
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

    # Stage 5: Trigger Power BI REST API Incremental Model Refresh
    trigger_powerbi_refresh = SimpleHttpOperator(
        task_id="trigger_powerbi_refresh",
        http_conn_id="powerbi_api",
        endpoint="/v1.0/myorg/groups/{{ var.value.POWERBI_WORKSPACE_ID | default('sc-hub-workspace') }}/datasets/{{ var.value.POWERBI_DATASET_ID | default('sc-hub-semantic-model') }}/refreshes",
        method="POST",
        headers={"Content-Type": "application/json"},
        data='{"notifyOption": "MailOnFailure"}',
    )

    end = EmptyOperator(task_id="pipeline_complete")

    # Task Execution Topology
    start >> check_gcs_raw_landing >> sync_bigquery_raw_tables >> dbt_run >> dbt_test >> trigger_powerbi_refresh >> end
