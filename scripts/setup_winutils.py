"""
setup_winutils.py
=================
Downloads winutils.exe and hadoop.dll for Windows — required by PySpark
to perform local file system operations (Parquet write, temp directory creation).

This is a WINDOWS-ONLY requirement. On Linux/Mac this is not needed.

Usage:
    python scripts/setup_winutils.py

What it does:
    1. Downloads winutils.exe + hadoop.dll from the cdarlint/winutils GitHub repo
       (the standard community-maintained Hadoop Windows binaries).
    2. Places them in: conf/spark/winutils/hadoop-3.3.6/bin/
    3. Prints the HADOOP_HOME env variable you need to set.

After running this, add to your .env file:
    HADOOP_HOME=<project-root>/conf/spark/winutils/hadoop-3.3.6

Or set it permanently in Windows:
    [System Properties] -> [Environment Variables] -> New System Variable
    Name:  HADOOP_HOME
    Value: D:\\path\\to\\project\\conf\\spark\\winutils\\hadoop-3.3.6
"""

import os
import sys
import urllib.request
import platform

# Force UTF-8 on Windows
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# ── Config ─────────────────────────────────────────────────────────────────────
HADOOP_VERSION = "3.3.6"
WINUTILS_BASE_URL = (
    f"https://github.com/cdarlint/winutils/raw/master/hadoop-{HADOOP_VERSION}/bin"
)
FILES_TO_DOWNLOAD = ["winutils.exe", "hadoop.dll"]

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WINUTILS_DIR = os.path.join(
    PROJECT_ROOT, "conf", "spark", "winutils", f"hadoop-{HADOOP_VERSION}", "bin"
)


def download_file(url: str, dest_path: str) -> None:
    filename = os.path.basename(dest_path)
    if os.path.exists(dest_path):
        size_kb = os.path.getsize(dest_path) / 1024
        print(f"  [OK] {filename} already exists ({size_kb:.0f} KB)")
        return

    print(f"  Downloading {filename}...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        size_kb = os.path.getsize(dest_path) / 1024
        print(f"  [OK] {filename} downloaded ({size_kb:.0f} KB)")
    except Exception as e:
        print(f"  [FAILED] Could not download {filename}: {e}")
        print(f"     Manual download URL: {url}")


def main() -> None:
    if platform.system() != "Windows":
        print("  [INFO] winutils is only needed on Windows. Skipping.")
        return

    print("=" * 65)
    print("  WinUtils Setup — Enterprise Supply Chain Hub (Windows)")
    print("=" * 65)
    print()

    os.makedirs(WINUTILS_DIR, exist_ok=True)
    print(f"  Download directory: {WINUTILS_DIR}")
    print()

    for filename in FILES_TO_DOWNLOAD:
        url = f"{WINUTILS_BASE_URL}/{filename}"
        dest = os.path.join(WINUTILS_DIR, filename)
        download_file(url, dest)

    hadoop_home = os.path.join(
        PROJECT_ROOT, "conf", "spark", "winutils", f"hadoop-{HADOOP_VERSION}"
    )

    print()
    print("=" * 65)
    print("  Setup complete! Add this to your .env file:")
    print()
    print(f"  HADOOP_HOME={hadoop_home}")
    print()
    print("  Or set it permanently in Windows Environment Variables.")
    print("=" * 65)


if __name__ == "__main__":
    main()
