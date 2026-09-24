"""
spark_session.py
================
Centralised SparkSession factory for the Enterprise Supply Chain Hub.

Usage:
    from pyspark_jobs.utils.spark_session import get_spark_session

    spark = get_spark_session(env="local")   # local development
    spark = get_spark_session(env="dataproc") # Google Cloud Dataproc

Environments supported:
    - "local"       : Single-machine development (runs on your laptop)
    - "dataproc"    : Google Cloud Dataproc managed cluster
    - "serverless"  : Serverless Spark on BigQuery (no cluster management)
"""

import os
import logging
from pyspark.sql import SparkSession
from pyspark import SparkConf

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Spark-BigQuery connector version (keep in sync with requirements-spark.txt)
# PySpark 4.0.x → use connector 0.38.x (Spark 3.5.x → use 0.36.x)
# ─────────────────────────────────────────────────────────────────────────────
_BQ_CONNECTOR_VERSION = "0.38.0"
_BQ_CONNECTOR_JAR = (
    f"gs://spark-lib/bigquery/spark-bigquery-with-dependencies_2.13-{_BQ_CONNECTOR_VERSION}.jar"
)
# Local JAR path for offline/laptop use (downloaded by setup script)
# Note: Spark 4.0 uses Scala 2.13 (vs 2.12 in Spark 3.5)
_BQ_CONNECTOR_LOCAL_JAR = os.path.join(
    os.path.dirname(__file__), "..", "..", "conf", "spark", "jars",
    f"spark-bigquery-with-dependencies_2.13-{_BQ_CONNECTOR_VERSION}.jar"
)


def get_spark_session(
    env: str = "local",
    app_name: str = "EnterpriseSupplyChainHub",
    gcp_project_id: str | None = None,
    gcs_temp_bucket: str | None = None,
    extra_conf: dict | None = None,
) -> SparkSession:
    """
    Build and return a configured SparkSession.

    Args:
        env:              Execution environment. One of: "local", "dataproc", "serverless".
        app_name:         Application name shown in Spark UI.
        gcp_project_id:   GCP project ID (overrides env-var GCP_PROJECT_ID).
        gcs_temp_bucket:  GCS bucket used as temp storage by the BigQuery connector
                          (overrides env-var GCS_TEMP_BUCKET).
        extra_conf:       Additional Spark config key-value pairs.

    Returns:
        A fully-configured SparkSession ready to use.
    """
    project_id = gcp_project_id or os.getenv("GCP_PROJECT_ID", "supply-chain-analytics-hub")
    temp_bucket = gcs_temp_bucket or os.getenv("GCS_TEMP_BUCKET", "sc-analytics-spark-temp")

    conf = SparkConf()
    conf.setAppName(app_name)

    # ── Environment-specific master & resource settings ──────────────────────
    if env == "local":
        _configure_local(conf)
    elif env == "dataproc":
        _configure_dataproc(conf)
    elif env == "serverless":
        _configure_serverless(conf, project_id)
    else:
        raise ValueError(f"Unknown environment '{env}'. Choose: local | dataproc | serverless")

    # ── BigQuery connector settings (common to all environments) ─────────────
    _configure_bigquery(conf, project_id, temp_bucket, env)

    # ── User-supplied overrides ───────────────────────────────────────────────
    if extra_conf:
        for key, value in extra_conf.items():
            conf.set(key, value)

    spark = SparkSession.builder.config(conf=conf).getOrCreate()

    # Set BigQuery-specific SQL extensions
    spark.conf.set("viewsEnabled", "true")
    spark.conf.set("materializationProject", project_id)
    spark.conf.set("materializationDataset", "spark_temp")

    logger.info(
        "SparkSession created | env=%s | project=%s | appName=%s",
        env, project_id, app_name
    )
    return spark


# ─────────────────────────────────────────────────────────────────────────────
# Private helpers
# ─────────────────────────────────────────────────────────────────────────────

def _configure_local(conf: SparkConf) -> None:
    """Local mode: use all available CPU cores on developer laptop."""
    conf.setMaster("local[*]")

    # Memory settings safe for a developer laptop (8-16 GB RAM)
    conf.set("spark.driver.memory", "4g")
    conf.set("spark.executor.memory", "4g")
    conf.set("spark.driver.maxResultSize", "2g")

    # Shuffle & performance tweaks for local mode
    conf.set("spark.sql.shuffle.partitions", "8")  # Low for local; default 200 is too high
    conf.set("spark.sql.adaptive.enabled", "true")
    conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")

    # Auto-detect winutils HADOOP_HOME on Windows (required for Parquet writes)
    import platform
    if platform.system() == "Windows" and not os.environ.get("HADOOP_HOME"):
        winutils_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "conf", "spark", "winutils", "hadoop-3.3.6"
        )
        winutils_dir = os.path.normpath(winutils_dir)
        if os.path.isdir(winutils_dir):
            os.environ["HADOOP_HOME"] = winutils_dir
            logger.info("Auto-set HADOOP_HOME = %s", winutils_dir)
        else:
            logger.warning(
                "HADOOP_HOME not set and winutils not found at %s. "
                "Parquet writes may fail on Windows. "
                "Run: python scripts/setup_winutils.py",
                winutils_dir,
            )

    # Point to the locally downloaded BQ JAR
    # On Windows, convert backslash path to file:/// URI so Spark handles spaces correctly
    if os.path.exists(_BQ_CONNECTOR_LOCAL_JAR):
        # Normalise path and convert to URI (required when path has spaces on Windows)
        import urllib.parse
        abs_jar = os.path.normpath(_BQ_CONNECTOR_LOCAL_JAR)
        # Percent-encode the path (turns spaces → %20, & → %26, etc.)
        jar_uri = "file:///" + urllib.parse.quote(abs_jar.replace("\\", "/"), safe="/:")
        conf.set("spark.jars", jar_uri)
        logger.info("Using local BigQuery connector JAR: %s", abs_jar)
    else:
        logger.warning(
            "Local BigQuery connector JAR not found at %s. "
            "BigQuery reads/writes will not work until you run: "
            "python scripts/download_spark_jars.py",
            _BQ_CONNECTOR_LOCAL_JAR,
        )




def _configure_dataproc(conf: SparkConf) -> None:
    """
    Dataproc mode: Spark master is set automatically by Dataproc YARN.
    We tune parallelism for the cluster defined in conf/gcp/dataproc_cluster.yaml.
    """
    # Dataproc injects YARN master automatically — do NOT hardcode spark.master here.
    # Resource config should match the cluster worker nodes:
    #   n2-standard-4  ->  4 vCPUs, 16 GB RAM per worker
    conf.set("spark.executor.cores", "4")
    conf.set("spark.executor.memory", "12g")
    conf.set("spark.executor.memoryOverhead", "2g")
    conf.set("spark.driver.memory", "4g")

    # Tune shuffle partitions for the cluster (workers * cores * 2-3 is a good start)
    # Default cluster has 3 workers → 3 * 4 * 3 = 36 partitions
    conf.set("spark.sql.shuffle.partitions", "36")
    conf.set("spark.sql.adaptive.enabled", "true")
    conf.set("spark.sql.adaptive.skewJoin.enabled", "true")

    # BigQuery connector JAR hosted on GCS (standard for Dataproc)
    conf.set("spark.jars", _BQ_CONNECTOR_JAR)


def _configure_serverless(conf: SparkConf, project_id: str) -> None:
    """
    Serverless Spark (BigQuery Spark): Google manages everything.
    No master config needed — just tune parallelism and memory.
    """
    conf.set("spark.driver.memory", "4g")
    conf.set("spark.executor.memory", "8g")
    conf.set("spark.sql.shuffle.partitions", "50")
    conf.set("spark.sql.adaptive.enabled", "true")
    conf.set("spark.jars", _BQ_CONNECTOR_JAR)


def _configure_bigquery(
    conf: SparkConf, project_id: str, temp_bucket: str, env: str
) -> None:
    """Apply BigQuery-connector Spark settings shared across all environments."""
    conf.set("spark.hadoop.google.cloud.auth.service.account.enable", "true")

    # In local dev, use the key file path from environment variable
    if env == "local":
        keyfile = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
        if keyfile:
            conf.set(
                "spark.hadoop.google.cloud.auth.service.account.json.keyfile",
                keyfile,
            )

    # BigQuery connector defaults (can be overridden per-job via DataFrameReader options)
    conf.set("spark.bigquery.project", project_id)
    conf.set("spark.bigquery.tempGcsBucket", temp_bucket)

    # Read format: ARROW is faster than AVRO for analytical workloads
    conf.set("spark.bigquery.read.format", "arrow")
    conf.set("spark.bigquery.write.method", "indirect")  # Reliable for large writes
