"""
bigquery_io.py
==============
Reusable BigQuery read/write helpers built on top of the spark-bigquery-connector.

All jobs in this project import from here instead of calling the connector
options directly — so if the connector API changes, we fix it in one place.

Usage:
    from pyspark_jobs.utils.bigquery_io import read_bq_table, write_bq_table, read_bq_sql

    df = read_bq_table(spark, "supply_chain_marts.fct_inventory_snapshot")
    write_bq_table(df, "supply_chain_marts.ml_demand_forecast", mode="overwrite")
"""

import logging
from pyspark.sql import SparkSession, DataFrame

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# READ helpers
# ─────────────────────────────────────────────────────────────────────────────

def read_bq_table(
    spark: SparkSession,
    table: str,
    project: str | None = None,
    filter: str | None = None,
) -> DataFrame:
    """
    Read a BigQuery table into a Spark DataFrame.

    Args:
        spark:   Active SparkSession.
        table:   Fully-qualified BigQuery table: "dataset.table"
                 or "project.dataset.table".
        project: GCP project ID override. Falls back to SparkSession config.
        filter:  Optional BigQuery WHERE clause pushdown filter, e.g.:
                 "snapshot_date >= '2025-01-01'"

    Returns:
        Spark DataFrame containing the full table (or filtered subset).

    Example:
        df = read_bq_table(spark, "supply_chain_marts.fct_inventory_snapshot",
                           filter="snapshot_date >= '2025-06-01'")
    """
    reader = spark.read.format("bigquery")

    if project:
        reader = reader.option("project", project)
    if filter:
        reader = reader.option("filter", filter)
        logger.info("BigQuery filter pushdown: %s", filter)

    df = reader.load(table)
    logger.info("Read BigQuery table '%s': %d partitions", table, df.rdd.getNumPartitions())
    return df


def read_bq_sql(
    spark: SparkSession,
    sql_query: str,
    project: str | None = None,
) -> DataFrame:
    """
    Execute a BigQuery SQL query and return results as a Spark DataFrame.

    BigQuery executes the query on its own engine; Spark receives the result
    via the BigQuery Storage Read API (fast, Arrow-columnar format).

    Args:
        spark:     Active SparkSession.
        sql_query: Standard SQL query string.
        project:   GCP project to bill the query to.

    Returns:
        Spark DataFrame with query result.

    Example:
        df = read_bq_sql(spark, '''
            SELECT sku_id, SUM(quantity_sold) AS total_sold
            FROM `supply_chain_analytics_hub.supply_chain_marts.fct_sales`
            WHERE order_date >= '2025-01-01'
            GROUP BY sku_id
        ''')
    """
    reader = spark.read.format("bigquery")

    if project:
        reader = reader.option("project", project)

    # The connector maps the query string to a BQ job + materialises a temp table
    df = reader.option("query", sql_query).load()
    logger.info(
        "Executed BigQuery SQL query | partitions=%d | query_preview=%.120s...",
        df.rdd.getNumPartitions(), sql_query.strip(),
    )
    return df


# ─────────────────────────────────────────────────────────────────────────────
# WRITE helpers
# ─────────────────────────────────────────────────────────────────────────────

def write_bq_table(
    df: DataFrame,
    table: str,
    mode: str = "overwrite",
    partition_field: str | None = None,
    clustering_fields: list[str] | None = None,
    project: str | None = None,
) -> None:
    """
    Write a Spark DataFrame to a BigQuery table.

    Args:
        df:                Spark DataFrame to persist.
        table:             BigQuery target: "dataset.table" or "project.dataset.table".
        mode:              Spark write mode: "overwrite" | "append" | "ignore" | "errorifexists".
        partition_field:   BigQuery date-partition or range-partition column name.
        clustering_fields: Up to 4 column names for BigQuery clustering (improves query perf).
        project:           GCP project ID override.

    Example:
        write_bq_table(
            df,
            "supply_chain_marts.ml_demand_forecast",
            mode="overwrite",
            partition_field="forecast_date",
            clustering_fields=["sku_id", "warehouse_id"],
        )
    """
    writer = df.write.format("bigquery").mode(mode)

    if project:
        writer = writer.option("project", project)
    if partition_field:
        writer = writer.option("partitionField", partition_field)
        writer = writer.option("partitionType", "DAY")
    if clustering_fields:
        writer = writer.option("clusteredFields", ",".join(clustering_fields))

    writer.save(table)
    logger.info(
        "Wrote DataFrame to BigQuery '%s' | mode=%s | rows~=%s",
        table, mode, "unknown (BigQuery counts on commit)"
    )


def write_bq_table_partitioned(
    df: DataFrame,
    table: str,
    partition_field: str,
    mode: str = "overwrite",
) -> None:
    """
    Convenience wrapper for writing date-partitioned BigQuery tables.
    Calls write_bq_table with partitioning pre-set.
    """
    write_bq_table(df, table, mode=mode, partition_field=partition_field)
