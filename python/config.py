# Configuration profiles for data generation
import os
from dataclasses import dataclass
from datetime import date

@dataclass
class ScaleConfig:
    name: str
    seed: int
    start_date: date
    end_date: date
    num_skus: int
    num_suppliers: int
    num_warehouses: int
    num_regions: int
    num_customers: int
    num_planners: int
    active_pairs_count: int
    daily_sales_orders_avg: int
    po_frequency_days: int
    forecast_horizons_months: int

# Dev profile for rapid validation
DEV_CONFIG = ScaleConfig(
    name="dev",
    seed=42,
    start_date=date(2025, 1, 1),
    end_date=date(2025, 6, 30), # 181 days
    num_skus=300,
    num_suppliers=50,
    num_warehouses=10,
    num_regions=5,
    num_customers=250,
    num_planners=10,
    active_pairs_count=600,
    daily_sales_orders_avg=150,
    po_frequency_days=7,
    forecast_horizons_months=6,
)

# Full enterprise scale targeting 5M-10M+ fact rows
FULL_CONFIG = ScaleConfig(
    name="full",
    seed=42,
    start_date=date(2024, 1, 1),
    end_date=date(2025, 12, 31), # 731 days (2 full years)
    num_skus=10000,
    num_suppliers=500,
    num_warehouses=100,
    num_regions=6,
    num_customers=5000,
    num_planners=40,
    active_pairs_count=7500,       # 7,500 active SKU-warehouse pairs across 731 days = ~5.4M inventory snapshots alone!
    daily_sales_orders_avg=3000,  # ~2.2M sales orders over 2 years (each with 1-3 lines = ~3.5M fact sales lines)
    po_frequency_days=5,          # ~800k PO lines
    forecast_horizons_months=12,  # ~600k forecast records
)

def get_config(scale_name: str) -> ScaleConfig:
    if scale_name.lower() == "full":
        return FULL_CONFIG
    return DEV_CONFIG
