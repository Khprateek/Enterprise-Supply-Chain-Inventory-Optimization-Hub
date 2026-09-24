"""
download_spark_jars.py
======================
Downloads the spark-bigquery-connector JAR to conf/spark/jars/ so that
PySpark jobs can run locally without internet access during a job run.

This only needs to run ONCE when setting up a new developer machine.

Usage:
    python scripts/download_spark_jars.py

What it downloads:
    spark-bigquery-with-dependencies_2.12-0.36.1.jar   (~65 MB)
    From: https://storage.googleapis.com/spark-lib/bigquery/
"""

import os
import sys
import urllib.request
import hashlib

# Force UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# ── JAR to download ────────────────────────────────────────────────────────────
# PySpark 4.0 uses Spark 4.0 (Scala 2.13) → use connector 0.38.x with _2.13 suffix
# PySpark 3.5 uses Spark 3.5 (Scala 2.12) → use connector 0.36.x with _2.12 suffix
BQ_CONNECTOR_VERSION = "0.38.0"
SCALA_SUFFIX = "2.13"  # Spark 4.0 uses Scala 2.13
JAR_FILENAME = f"spark-bigquery-with-dependencies_{SCALA_SUFFIX}-{BQ_CONNECTOR_VERSION}.jar"
JAR_URL = f"https://storage.googleapis.com/spark-lib/bigquery/{JAR_FILENAME}"

# Destination: conf/spark/jars/ (relative to project root)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JAR_DIR = os.path.join(PROJECT_ROOT, "conf", "spark", "jars")
JAR_PATH = os.path.join(JAR_DIR, JAR_FILENAME)


def _progress_hook(block_count: int, block_size: int, total_size: int) -> None:
    """Print download progress bar to stdout."""
    downloaded = block_count * block_size
    if total_size > 0:
        pct = min(downloaded / total_size * 100, 100)
        bar_len = 40
        filled = int(bar_len * pct / 100)
        bar = "#" * filled + "." * (bar_len - filled)
        mb_done = downloaded / (1024 * 1024)
        mb_total = total_size / (1024 * 1024)
        print(
            f"\r  [{bar}] {pct:5.1f}%  {mb_done:.1f}/{mb_total:.1f} MB",
            end="",
            flush=True,
        )



def download_jar() -> None:
    os.makedirs(JAR_DIR, exist_ok=True)

    if os.path.exists(JAR_PATH):
        size_mb = os.path.getsize(JAR_PATH) / (1024 * 1024)
        print(f"  [OK] JAR already exists: {JAR_PATH} ({size_mb:.1f} MB)")
        print("     Delete it and re-run this script to force re-download.")
        return


    print(f"  Downloading {JAR_FILENAME}...")
    print(f"  Source : {JAR_URL}")
    print(f"  Dest   : {JAR_PATH}")
    print()

    try:
        urllib.request.urlretrieve(JAR_URL, JAR_PATH, reporthook=_progress_hook)
        print()  # newline after progress bar
    except Exception as e:
        print(f"\n  [FAILED] Download failed: {e}")
        print("     Check your internet connection or download manually from:")
        print(f"     {JAR_URL}")
        sys.exit(1)

    size_mb = os.path.getsize(JAR_PATH) / (1024 * 1024)
    print(f"  [OK] Downloaded: {JAR_PATH} ({size_mb:.1f} MB)")



def main() -> None:
    print("=" * 65)
    print("  Spark JAR Downloader — Enterprise Supply Chain Hub")
    print("=" * 65)
    download_jar()
    print()
    print("  Next step: run the verification script:")
    print("  python pyspark_jobs/verify_setup.py")
    print()


if __name__ == "__main__":
    main()
