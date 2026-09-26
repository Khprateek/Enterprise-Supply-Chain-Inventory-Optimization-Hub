import polars as pl
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger("polars_marts")

def build_marts():
    project_root = Path(os.path.abspath(__file__)).parents[1]
    facts_dir = project_root / "data" / "facts"
    dims_dir = project_root / "data" / "dimensions"
    marts_dir = project_root / "data" / "marts"
    
    marts_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Initializing lazy scans for Data Marts...")

    # Load Dimensions
    dim_date = pl.scan_parquet(dims_dir / "dim_date" / "**" / "*.parquet")
    dim_product = pl.scan_parquet(dims_dir / "dim_product" / "**" / "*.parquet")
    dim_warehouse = pl.scan_parquet(dims_dir / "dim_warehouse" / "**" / "*.parquet")
    dim_channel = pl.scan_parquet(dims_dir / "dim_customer_channel" / "**" / "*.parquet")
    dim_supplier = pl.scan_parquet(dims_dir / "dim_supplier" / "**" / "*.parquet")

    # ---------------------------------------------------------
    # 1. Mart: Monthly Sales Summary
    # ---------------------------------------------------------
    logger.info("Building Mart: Monthly Sales Summary...")
    fact_sales = pl.scan_parquet(facts_dir / "FactSales" / "**" / "*.parquet")
    
    sales_mart = (
        fact_sales
        .join(dim_date, left_on="order_date_sk", right_on="date_sk", how="inner")
        .join(dim_product, on="product_sk", how="inner")
        .join(dim_channel, on="customer_channel_sk", how="inner")
        .group_by(["month_year", "year_number", "month_number", "category_name", "brand_name", "channel_name", "customer_segment"])
        .agg([
            pl.col("gross_sales_amount").sum().alias("total_gross_sales"),
            pl.col("net_sales_amount").sum().alias("total_net_sales"),
            pl.col("cost_of_goods_sold").sum().alias("total_cogs"),
            pl.col("gross_margin").sum().alias("total_gross_margin"),
            pl.col("ordered_quantity").sum().alias("total_ordered_qty"),
            pl.col("shipped_quantity").sum().alias("total_shipped_qty"),
            pl.col("on_time_in_full_flag").sum().alias("otif_orders_count"),
            pl.len().alias("total_orders_count")
        ])
        .with_columns(
            (pl.col("otif_orders_count") / pl.col("total_orders_count")).alias("otif_rate")
        )
    )
    
    sales_mart_path = marts_dir / "mart_monthly_sales_summary.parquet"
    sales_mart.collect().write_parquet(sales_mart_path)
    logger.info(f"Saved {sales_mart_path}")

    # ---------------------------------------------------------
    # 2. Mart: Current Inventory Health (Latest Snapshot)
    # ---------------------------------------------------------
    logger.info("Building Mart: Current Inventory Health...")
    fact_inv = pl.scan_parquet(facts_dir / "FactInventorySnapshot" / "**" / "*.parquet")
    
    latest_snapshot = (
        fact_inv
        .join(dim_date, left_on="snapshot_date_sk", right_on="date_sk", how="inner")
        .filter(pl.col("date_key") >= (pl.col("date_key").max() - 7))
        .join(dim_product, on="product_sk", how="inner")
        .join(dim_warehouse, on="warehouse_sk", how="inner")
        .group_by(["warehouse_name", "facility_type", "region_key", "category_name", "brand_name", "product_name"])
        .agg([
            pl.col("on_hand_quantity").sum().alias("total_on_hand"),
            pl.col("in_transit_inbound_quantity").sum().alias("total_in_transit"),
            pl.col("reserved_quantity").sum().alias("total_reserved"),
            pl.col("available_quantity").sum().alias("total_available"),
            pl.col("inventory_valuation").sum().alias("total_inventory_value")
        ])
    )
    
    inv_mart_path = marts_dir / "mart_inventory_health.parquet"
    latest_snapshot.collect().write_parquet(inv_mart_path)
    logger.info(f"Saved {inv_mart_path}")

    # ---------------------------------------------------------
    # 3. Mart: Supplier Reliability Profile
    # ---------------------------------------------------------
    logger.info("Building Mart: Supplier Reliability Profile...")
    fact_perf = pl.scan_parquet(facts_dir / "FactSupplierMonthlyPerformance" / "**" / "*.parquet")
    
    supplier_mart = (
        fact_perf
        .join(dim_supplier, on="supplier_sk", how="inner")
        .group_by(["supplier_name", "supplier_tier", "country", "year_month"])
        .agg([
            pl.col("total_pocount").sum(),
            pl.col("total_ordered_quantity").sum(),
            pl.col("total_received_quantity").sum(),
            pl.col("total_rejected_quantity").sum(),
            pl.col("total_spend_amount").sum(),
            pl.col("on_time_pocount").sum(),
            pl.col("in_full_pocount").sum(),
            (pl.col("average_lead_time_days") * pl.col("total_pocount")).sum() / pl.col("total_pocount").sum().alias("weighted_avg_lead_time")
        ])
        .with_columns([
            (pl.col("total_rejected_quantity") / pl.col("total_received_quantity")).alias("rejection_rate"),
            (pl.col("on_time_pocount") / pl.col("total_pocount")).alias("on_time_rate")
        ])
    )
    
    supplier_mart_path = marts_dir / "mart_supplier_reliability.parquet"
    supplier_mart.collect().write_parquet(supplier_mart_path)
    logger.info(f"Saved {supplier_mart_path}")

    logger.info("All Polars Data Marts successfully built!")

if __name__ == "__main__":
    build_marts()
