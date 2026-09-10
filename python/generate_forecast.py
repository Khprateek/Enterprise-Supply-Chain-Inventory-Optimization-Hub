# Demand Forecast Generator
import numpy as np
import pandas as pd
from datetime import date, timedelta
from python.config import ScaleConfig
from python.common import date_to_key

def generate_forecast(config: ScaleConfig, dimensions: dict, df_sales: pd.DataFrame, active_pairs: list, rng: np.random.Generator):
    print("--- Generating Demand Forecasts (FactDemandForecast) ---")
    
    dim_product = dimensions["DimProduct"]
    curr_prods = dim_product[dim_product["IsCurrent"]].copy()
    sku_to_pk = dict(zip(curr_prods["ProductSKU"], curr_prods["ProductKey"]))
    sku_to_price = dict(zip(curr_prods["ProductSKU"], curr_prods["UnitListPrice"]))
    sku_to_xyz = dict(zip(curr_prods["ProductSKU"], curr_prods["XYZClassification"]))
    
    # Calculate monthly historical demand per SKU-Warehouse
    df_sales["YearMonth"] = df_sales["OrderDate"].apply(lambda d: f"{d.year}-{d.month:02d}")
    monthly_sales = df_sales.groupby(["YearMonth", "ProductSKU", "WarehouseKey"])["OrderedQuantity"].sum().to_dict()
    
    months = sorted(list(set(df_sales["YearMonth"].values)))
    
    forecast_records = []
    fc_key = 1
    
    for ym in months:
        y, m = map(int, ym.split("-"))
        target_date = date(y, m, 1)
        gen_date = target_date - timedelta(days=30)
        
        for sku, wh_key in active_pairs:
            p_key = sku_to_pk[sku]
            price = sku_to_price[sku]
            xyz = sku_to_xyz.get(sku, "Y")
            
            actual_d = monthly_sales.get((ym, sku, wh_key), 0)
            if actual_d == 0:
                actual_d = rng.integers(10, 80)
                
            # Error variance & bias based on XYZ
            if xyz == "X":
                bias = rng.uniform(-0.03, 0.03)
                err_std = 0.08
            elif xyz == "Y":
                bias = rng.uniform(0.02, 0.08) # slight over-forecast bias
                err_std = 0.18
            else: # Z
                bias = rng.uniform(-0.12, 0.15)
                err_std = 0.35
                
            baseline_qty = max(1, int(round(actual_d * (1 + rng.normal(0, err_std)))))
            planner_adj = int(round(baseline_qty * bias))
            final_fc = max(1, baseline_qty + planner_adj)
            
            forecast_records.append({
                "ForecastKey": fc_key,
                "TargetPeriodDateKey": date_to_key(target_date),
                "ForecastGeneratedDateKey": date_to_key(gen_date),
                "TargetPeriodDate": target_date,
                "ForecastGeneratedDate": gen_date,
                "ProductKey": p_key,
                "ProductSKU": sku,
                "WarehouseKey": wh_key,
                "ScenarioKey": 1, # Baseline
                "ForecastedQuantity": final_fc,
                "BaselineStatisticalQuantity": baseline_qty,
                "PlannerAdjustmentQuantity": planner_adj,
                "ForecastValue": round(final_fc * price, 2),
                "ForecastModelVersion": "HoltWinters-V2" if xyz != "Z" else "Croston-Intermittent"
            })
            fc_key += 1
            
    df_fc = pd.DataFrame(forecast_records)
    print(f"Generated {len(df_fc):,} forecast records.")
    return df_fc
