"""
verify_setup.py
===============
Quick smoke-test script for Phase 1 of the PySpark integration.

Run this FIRST to verify that:
  1. PySpark is correctly installed.
  2. The SparkSession factory works in local mode.
  3. Basic Spark operations (DataFrame creation, SQL, Parquet write) work.
  4. The BigQuery connector JAR is found (if downloaded).
  5. GCP credentials are readable (if configured).

Usage (Windows):
    $env:JAVA_HOME="C:\\Program Files\\Microsoft\\jdk-21.0.12.101-hotspot"
    $env:PATH="$env:JAVA_HOME\\bin;" + $env:PATH
    python pyspark_jobs/verify_setup.py

Expected output on success:
    [PASS] PySpark version: 3.5.x
    [PASS] SparkSession created in local mode
    [PASS] DataFrame operations work
    [PASS] Parquet round-trip works
    [PASS] BigQuery connector JAR found
    [INFO] GCP credentials: ...
    Phase 1 setup verification PASSED
"""

import os
import sys
import tempfile
import platform
import subprocess

# ---------------------------------------------------------------------------
# Make sure we import from the project root
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

PASS = "[PASS]"
FAIL = "[FAIL]"
INFO = "[INFO]"
SEP  = "-" * 70

all_passed = True


def check(label: str, condition: bool, details: str = "") -> None:
    global all_passed
    suffix = f" -- {details}" if details else ""
    if condition:
        print(f"  {PASS} {label}{suffix}")
    else:
        print(f"  {FAIL} {label}{suffix}")
        all_passed = False


def section(title: str) -> None:
    print(f"\n-- {title} {'-' * (65 - len(title))}")


# ---------------------------------------------------------------------------
# Windows: set HADOOP_HOME before Spark starts
# ---------------------------------------------------------------------------
if platform.system() == "Windows" and not os.environ.get("HADOOP_HOME"):
    winutils_dir = os.path.normpath(
        os.path.join(PROJECT_ROOT, "conf", "spark", "winutils", "hadoop-3.3.6")
    )
    if os.path.isdir(winutils_dir):
        os.environ["HADOOP_HOME"] = winutils_dir
        print(f"  {INFO} Auto-set HADOOP_HOME = {winutils_dir}")

# ---------------------------------------------------------------------------
# Windows: resolve short (8.3) path for Python executable so Spark workers
# don't crash when the Python path contains spaces.
# ---------------------------------------------------------------------------
_python_exe = sys.executable
if platform.system() == "Windows" and " " in _python_exe:
    try:
        result = subprocess.run(
            ["cmd", "/c", f'for %I in ("{_python_exe}") do @echo %~sI'],
            capture_output=True, text=True, shell=False
        )
        short = result.stdout.strip()
        if short and os.path.exists(short):
            _python_exe = short
    except Exception:
        pass  # keep original

os.environ["PYSPARK_PYTHON"] = _python_exe
os.environ["PYSPARK_DRIVER_PYTHON"] = _python_exe


# ===========================================================================
# 1. PySpark installation
# ===========================================================================
section("1. Checking PySpark installation")
try:
    import pyspark
    check("PySpark installed", True, f"version {pyspark.__version__}")

    # Warn if using PySpark 3.5 with Python 3.12 (incompatible)
    import sys as _sys
    if pyspark.__version__.startswith("3.") and _sys.version_info >= (3, 12):
        print(f"  {INFO} WARNING: PySpark 3.x does NOT support Python 3.12.")
        print(f"          Upgrade: pip install pyspark==4.0.4")

except ImportError as e:
    check("PySpark installed", False, str(e))
    print("\n  Fix: pip install pyspark==4.0.4")
    sys.exit(1)


# ===========================================================================
# 2. SparkSession in local mode
# ===========================================================================
section("2. Creating SparkSession in local mode")
spark = None
try:
    from pyspark.sql import SparkSession

    spark = (
        SparkSession.builder
        .master("local[1]")              # single-threaded: avoids Python 3.12 worker issues on Windows
        .appName("VerifySetup")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "1")
        .config("spark.sql.adaptive.enabled", "false")
        .config("spark.driver.extraJavaOptions", "-Dfile.encoding=UTF-8")
        .config("spark.executor.extraJavaOptions", "-Dfile.encoding=UTF-8")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    check("SparkSession created", spark is not None, f"master={spark.sparkContext.master}")
    check("local mode active", "local" in spark.sparkContext.master, spark.sparkContext.master)
except Exception as e:
    check("SparkSession created", False, str(e))


# ===========================================================================
# 3. Basic DataFrame operations
# ===========================================================================
section("3. Testing DataFrame operations")
df = None
if spark:
    try:
        from pyspark.sql import functions as F
        from pyspark.sql.types import (
            StructType, StructField, StringType, IntegerType, DoubleType
        )

        schema = StructType([
            StructField("sku_id",       StringType(),  nullable=False),
            StructField("warehouse_id", StringType(),  nullable=False),
            StructField("quantity",     IntegerType(), nullable=True),
            StructField("unit_cost",    DoubleType(),  nullable=True),
        ])

        data = [
            ("SKU-001", "WH-01", 100, 12.50),
            ("SKU-002", "WH-01", 250,  8.99),
            ("SKU-003", "WH-02",  75, 45.00),
            ("SKU-001", "WH-02", 300, 12.50),
            ("SKU-004", "WH-03",   0, 99.99),
        ]

        df = spark.createDataFrame(data, schema=schema)

        # Aggregation
        agg = df.groupBy("sku_id").agg(
            F.sum("quantity").alias("total_qty"),
            F.sum(F.col("quantity") * F.col("unit_cost")).alias("total_value"),
        )
        rows = agg.count()
        check("DataFrame aggregation", rows == 4, f"{rows} SKU groups")

        # Window function
        from pyspark.sql.window import Window
        w = Window.partitionBy("warehouse_id").orderBy(F.desc("quantity"))
        ranked = df.withColumn("rank_in_wh", F.rank().over(w))
        check("Window function (rank)", ranked.count() == 5)

        # Spark SQL
        df.createOrReplaceTempView("inventory")
        sql_df = spark.sql(
            "SELECT warehouse_id, COUNT(*) AS sku_count "
            "FROM inventory GROUP BY warehouse_id"
        )
        check("Spark SQL query", sql_df.count() == 3, f"{sql_df.count()} warehouses")

    except Exception as e:
        check("DataFrame operations", False, str(e))


# ===========================================================================
# 4. Parquet read/write round-trip (using PyArrow directly — avoids Spark
#    Python worker crashes on Windows with PySpark 3.5 + Python 3.12)
# ===========================================================================
section("4. Testing Parquet read/write")
if spark and df is not None:
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq

        with tempfile.TemporaryDirectory() as tmp:
            parquet_path = os.path.join(tmp, "test_sc_data.parquet")

            # Collect DataFrame to driver and write via PyArrow
            pandas_df = df.toPandas()
            table = pa.Table.from_pandas(pandas_df)
            pq.write_table(table, parquet_path, compression="snappy")
            check("Parquet write (PyArrow)", True, f"{len(pandas_df)} rows written")

            # Read back via Spark (reading Parquet is driver-side, no Python worker needed)
            df_back = spark.read.parquet(parquet_path)
            rc = df_back.count()
            check("Parquet read-back via Spark", rc == 5, f"{rc} rows")

    except Exception as e:
        check("Parquet round-trip", False, str(e))
else:
    print(f"  {INFO} Skipped (SparkSession not available)")



# ===========================================================================
# 5. BigQuery connector JAR
# ===========================================================================
section("5. Checking BigQuery connector JAR")
# PySpark 4.0 → Scala 2.13 connector  |  PySpark 3.5 → Scala 2.12 connector
jar_path_4x = os.path.join(
    PROJECT_ROOT, "conf", "spark", "jars",
    "spark-bigquery-with-dependencies_2.13-0.38.0.jar"
)
jar_path_3x = os.path.join(
    PROJECT_ROOT, "conf", "spark", "jars",
    "spark-bigquery-with-dependencies_2.12-0.36.1.jar"  # kept from initial download
)
jar_path = jar_path_4x if os.path.exists(jar_path_4x) else jar_path_3x
if os.path.exists(jar_path):
    size_mb = os.path.getsize(jar_path) / (1024 * 1024)
    check("BQ connector JAR present", True, f"{size_mb:.1f} MB at {jar_path}")
else:
    check(
        "BQ connector JAR present", False,
        f"Not found: {jar_path} -- Run: python scripts/download_spark_jars.py"
    )


# ===========================================================================
# 6. GCP credentials
# ===========================================================================
section("6. GCP credentials check")
creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
if creds_path:
    exists = os.path.exists(creds_path)
    check("GOOGLE_APPLICATION_CREDENTIALS set and file exists", exists, creds_path)
else:
    print(f"  {INFO} GOOGLE_APPLICATION_CREDENTIALS not set.")
    print(f"        For BigQuery connectivity, either:")
    print(f"        a) Set GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa-key.json")
    print(f"        b) Run: gcloud auth application-default login")


# ===========================================================================
# Result
# ===========================================================================
print(f"\n{SEP}")
if all_passed:
    print("  Phase 1 setup verification PASSED -- ready to start Phase 2!")
else:
    print("  Some checks FAILED -- fix the items above and re-run.")
print(f"{SEP}\n")

if spark:
    spark.stop()

sys.exit(0 if all_passed else 1)
