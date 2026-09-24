"""
pyspark_env_config.py
=====================
Centralised configuration for the PySpark layer of the Enterprise Supply Chain Hub.

Reads from environment variables (or falls back to defaults) so that the same
code runs locally, on Dataproc, and in Serverless Spark without any code changes.

Usage:
    from pyspark_jobs.utils.pyspark_env_config import PySpark EnvConfig, get_pyspark_config

    config = get_pyspark_config()
    print(config.gcp_project_id)
    print(config.bq_dataset_marts)
"""

import os
from dataclasses import dataclass, field


@dataclass
class PySparkEnvConfig:
    """
    All environment-specific settings the PySpark layer needs.

    Every field maps to an environment variable (see get_pyspark_config()).
    Values can be overridden at runtime — useful for unit tests or CI jobs.
    """

    # ── Execution environment ─────────────────────────────────────────────────
    env: str = "local"
    """Spark execution environment: 'local' | 'dataproc' | 'serverless'"""

    # ── GCP project ───────────────────────────────────────────────────────────
    gcp_project_id: str = "supply-chain-analytics-hub"
    """Google Cloud project that hosts BigQuery, GCS, and Dataproc."""

    gcp_region: str = "us-central1"
    """Region for Dataproc cluster and GCS buckets."""

    # ── GCS buckets ───────────────────────────────────────────────────────────
    gcs_raw_landing_bucket: str = "sc-analytics-raw-landing"
    """GCS bucket where raw Parquet files are deposited by the data generation layer."""

    gcs_spark_temp_bucket: str = "sc-analytics-spark-temp"
    """GCS bucket used by the BigQuery connector as a staging area for data export."""

    gcs_outputs_bucket: str = "sc-analytics-outputs"
    """GCS bucket for storing Spark job outputs (e.g., processed Parquet files)."""

    # ── BigQuery datasets ─────────────────────────────────────────────────────
    bq_dataset_raw: str = "raw_supply_chain"
    """BigQuery dataset containing raw / landing tables."""

    bq_dataset_staging: str = "supply_chain_staging"
    """BigQuery dataset for dbt staging layer."""

    bq_dataset_marts: str = "supply_chain_marts"
    """BigQuery dataset for dbt dimensional marts (fact + dimension tables)."""

    bq_dataset_ml: str = "supply_chain_ml"
    """BigQuery dataset for ML model outputs written by PySpark jobs."""

    bq_dataset_spark_temp: str = "spark_temp"
    """BigQuery dataset for materialised BigQuery SQL query results (connector requirement)."""

    # ── Dataproc cluster ──────────────────────────────────────────────────────
    dataproc_cluster_name: str = "sc-hub-spark-cluster"
    """Name of the Dataproc cluster (used by Airflow DataprocSubmitJobOperator)."""

    # ── Authentication ────────────────────────────────────────────────────────
    google_application_credentials: str = ""
    """Path to the GCP service account JSON key file (for local dev only)."""

    # ── Spark tuning overrides ────────────────────────────────────────────────
    spark_shuffle_partitions: int = 8
    """
    Number of Spark shuffle partitions.
    Local default: 8 (low, so local mode is fast).
    Dataproc: overridden to 36 inside spark_session.py.
    """

    extra_spark_conf: dict = field(default_factory=dict)
    """Any additional spark configuration key-value pairs."""


def get_pyspark_config() -> PySparkEnvConfig:
    """
    Build a PySparkEnvConfig from environment variables.

    Precedence: environment variable → hardcoded default.

    Set these variables in a .env file (for local dev) or in your
    Dataproc job submission / Airflow Variables (for cloud runs).
    """
    return PySparkEnvConfig(
        env=os.getenv("SPARK_ENV", "local"),
        gcp_project_id=os.getenv("GCP_PROJECT_ID", "supply-chain-analytics-hub"),
        gcp_region=os.getenv("GCP_REGION", "us-central1"),
        gcs_raw_landing_bucket=os.getenv("GCS_RAW_LANDING_BUCKET", "sc-analytics-raw-landing"),
        gcs_spark_temp_bucket=os.getenv("GCS_TEMP_BUCKET", "sc-analytics-spark-temp"),
        gcs_outputs_bucket=os.getenv("GCS_OUTPUTS_BUCKET", "sc-analytics-outputs"),
        bq_dataset_raw=os.getenv("BQ_DATASET_RAW", "raw_supply_chain"),
        bq_dataset_staging=os.getenv("BQ_DATASET_STAGING", "supply_chain_staging"),
        bq_dataset_marts=os.getenv("BQ_DATASET_MARTS", "supply_chain_marts"),
        bq_dataset_ml=os.getenv("BQ_DATASET_ML", "supply_chain_ml"),
        bq_dataset_spark_temp=os.getenv("BQ_DATASET_SPARK_TEMP", "spark_temp"),
        dataproc_cluster_name=os.getenv("DATAPROC_CLUSTER_NAME", "sc-hub-spark-cluster"),
        google_application_credentials=os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""),
        spark_shuffle_partitions=int(os.getenv("SPARK_SHUFFLE_PARTITIONS", "8")),
    )
