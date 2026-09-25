# Shared utilities for data generation
import os
import zlib
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import date, timedelta
from typing import Tuple

def date_to_key(d: date) -> int:
    return d.year * 10000 + d.month * 100 + d.day

def deterministic_hash(val: str, salt: int = 0) -> int:
    # Generates a positive 63-bit integer from string
    b = f"{val}_{salt}".encode('utf-8')
    return zlib.crc32(b) & 0x7FFFFFFF

def save_dataframe(df: pd.DataFrame, entity_name: str, output_dir: str, format_type: str = "parquet", append: bool = False):
    os.makedirs(output_dir, exist_ok=True)
    if format_type.lower() == "parquet":
        file_path = os.path.join(output_dir, f"{entity_name}.parquet")
        
        if append and os.path.exists(file_path):
            existing_table = pq.read_table(file_path)
            existing_df = existing_table.to_pandas()
            df = pd.concat([existing_df, df], ignore_index=True)
            
        table = pa.Table.from_pandas(df, preserve_index=False)
        pq.write_table(table, file_path, compression="snappy")
    else:
        file_path = os.path.join(output_dir, f"{entity_name}.csv")
        df.to_csv(file_path, index=False)
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    print(f"  [SAVED] {entity_name}: {len(df):,} rows -> {file_path} ({file_size_mb:.2f} MB)")
    return file_path, len(df), file_size_mb
