# Master Orchestrator for Enterprise Supply Chain Data Generation
import os
import sys
import time
import argparse
import numpy as np
import pandas as pd

from python.config import get_config
from python.common import save_dataframe
from python.generate_dimensions import generate_dimensions
from python.generate_procurement import generate_procurement
from python.generate_sales import generate_sales
from python.generate_inventory import generate_inventory
from python.generate_forecast import generate_forecast
from python.generate_movements import generate_movements
from python.generate_stockouts import generate_stockouts
from python.generate_returns import generate_returns
from python.generate_supplier_perf import generate_supplier_performance

def run_pipeline(scale_name: str = "dev", output_dir: str = "data/raw", format_type: str = "parquet", seed: int = 42):
    start_time = time.time()
    print("=" * 80)
    print(f"ENTERPRISE SUPPLY CHAIN HUB: DATA GENERATION PIPELINE")
    print(f"Scale: {scale_name.upper()} | Output: {output_dir} | Format: {format_type} | Seed: {seed}")
    print("=" * 80)
    
    config = get_config(scale_name)
    if seed is not None:
        config.seed = seed
        
    rng = np.random.default_rng(config.seed)
    
    # 1. Dimensions
    t0 = time.time()
    dims = generate_dimensions(config, rng)
    print(f"  Dimensions generated in {time.time() - t0:.2f}s")
    
    # 2. Procurement (FactPurchaseOrder)
    t0 = time.time()
    df_po, active_pairs, dormant_pairs = generate_procurement(config, dims, rng)
    print(f"  Procurement generated in {time.time() - t0:.2f}s")
    
    # 3. Sales (FactSales with multi-line orders and SCD2 resolution)
    t0 = time.time()
    df_sales = generate_sales(config, dims, active_pairs, rng, dormant_pairs=dormant_pairs)
    print(f"  Sales generated in {time.time() - t0:.2f}s")
    
    # 4. Movements (FactInventoryMovement)
    t0 = time.time()
    df_movements = generate_movements(config, dims, active_pairs, rng)
    print(f"  Movements generated in {time.time() - t0:.2f}s")
    
    # 5. Inventory (FactInventorySnapshot - reconciled with sales, PO receipts, and movements)
    t0 = time.time()
    df_inventory = generate_inventory(config, dims, df_sales, df_po, active_pairs, rng, df_movements=df_movements)
    print(f"  Inventory snapshots generated in {time.time() - t0:.2f}s")
    
    # 6. Forecast (FactDemandForecast)
    t0 = time.time()
    df_forecast = generate_forecast(config, dims, df_sales, active_pairs, rng)
    print(f"  Forecast generated in {time.time() - t0:.2f}s")
    
    # 7. Stockouts (FactStockout)
    t0 = time.time()
    df_stockouts = generate_stockouts(dims, df_inventory, df_sales, rng)
    print(f"  Stockouts derived in {time.time() - t0:.2f}s")
    
    # 8. Returns (FactCustomerReturns)
    t0 = time.time()
    df_returns = generate_returns(dims, df_sales, rng)
    print(f"  Returns generated in {time.time() - t0:.2f}s")
    
    # 9. Supplier Monthly Performance Mart (FactSupplierMonthlyPerformance)
    t0 = time.time()
    df_supp_perf = generate_supplier_performance(dims, df_po)
    print(f"  Supplier performance mart materialized in {time.time() - t0:.2f}s")
    
    # Persist all dataframes
    print("-" * 80)
    print(f"SAVING ARTIFACTS TO {output_dir}")
    print("-" * 80)
    
    manifest = []
    
    # Dimensions
    for dim_name, df in dims.items():
        p, count, size_mb = save_dataframe(df, dim_name, output_dir, format_type)
        manifest.append({"Entity": dim_name, "Type": "Dimension" if "Dim" in dim_name else "Bridge", "Rows": count, "SizeMB": size_mb})
        
    # Facts & Marts
    facts = [
        ("FactSales", df_sales),
        ("FactInventorySnapshot", df_inventory),
        ("FactPurchaseOrder", df_po),
        ("FactDemandForecast", df_forecast),
        ("FactInventoryMovement", df_movements),
        ("FactStockout", df_stockouts),
        ("FactCustomerReturns", df_returns),
        ("FactSupplierMonthlyPerformance", df_supp_perf),
    ]
    
    for fact_name, df in facts:
        p, count, size_mb = save_dataframe(df, fact_name, output_dir, format_type)
        manifest.append({"Entity": fact_name, "Type": "Fact" if "Fact" in fact_name else "Mart", "Rows": count, "SizeMB": size_mb})
        
    df_manifest = pd.DataFrame(manifest)
    
    total_elapsed = time.time() - start_time
    total_fact_rows = sum([m["Rows"] for m in manifest if m["Type"] in ["Fact", "Mart"]])
    total_all_rows = sum([m["Rows"] for m in manifest])
    total_size_mb = sum([m["SizeMB"] for m in manifest])
    
    print("=" * 80)
    print(f"PIPELINE SUMMARY ({scale_name.upper()} SCALE)")
    print(f"Total Tables: {len(manifest)}")
    print(f"Total Fact / Mart Rows: {total_fact_rows:,}")
    print(f"Total All Rows: {total_all_rows:,}")
    print(f"Total Storage Size: {total_size_mb:.2f} MB")
    print(f"Total Execution Time: {total_elapsed:.2f} seconds")
    print("=" * 80)
    
    return df_manifest, total_elapsed

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enterprise Supply Chain Data Generator")
    parser.add_argument("--scale", choices=["dev", "full"], default="dev", help="Scale profile (dev or full)")
    parser.add_argument("--output", default="data/raw", help="Output directory")
    parser.add_argument("--format", choices=["parquet", "csv"], default="parquet", help="Output file format")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    
    args = parser.parse_args()
    run_pipeline(args.scale, args.output, args.format, args.seed)
