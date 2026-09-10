# Inventory Movements Generator
import numpy as np
import pandas as pd
from datetime import date, timedelta
from python.config import ScaleConfig
from python.common import date_to_key

def generate_movements(config: ScaleConfig, dimensions: dict, active_pairs: list, rng: np.random.Generator):
    print("--- Generating Inventory Movements (FactInventoryMovement) ---")
    
    dim_product = dimensions["DimProduct"]
    dim_warehouse = dimensions["DimWarehouse"]
    dim_planner = dimensions["DimEmployeePlanner"]
    
    curr_prods = dim_product[dim_product["IsCurrent"]].copy()
    sku_to_pk = dict(zip(curr_prods["ProductSKU"], curr_prods["ProductKey"]))
    sku_to_cost = dict(zip(curr_prods["ProductSKU"], curr_prods["UnitStandardCost"]))
    
    wh_keys = dim_warehouse["WarehouseKey"].values
    planner_keys = dim_planner["PlannerKey"].values
    
    total_days = (config.end_date - config.start_date).days + 1
    dates = [config.start_date + timedelta(days=i) for i in range(total_days)]
    
    movement_records = []
    mov_key = 1
    txn_counter = 1000
    
    # Generate weekly movements across warehouses
    mov_types = ["Inter-DC Transfer", "Cycle Count Adjustment", "Spoilage Scrap", "Damage Write-off"]
    mov_probs = [0.55, 0.25, 0.12, 0.08]
    
    # Sample daily movements
    daily_mov_count = max(2, int(round(config.daily_sales_orders_avg * 0.08)))
    
    for cur_date in dates:
        for _ in range(daily_mov_count):
            sku, orig_wh = active_pairs[rng.integers(0, len(active_pairs))]
            m_type = rng.choice(mov_types, p=mov_probs)
            p_key = sku_to_pk[sku]
            cost = sku_to_cost[sku]
            
            if m_type == "Inter-DC Transfer":
                dest_wh = int(rng.choice([w for w in wh_keys if w != orig_wh]))
                qty = int(rng.choice([100, 250, 500, 1000]))
                freight = round(float(rng.uniform(40.0, 350.0)), 2)
                transit_days = int(rng.choice([1, 2, 3, 4]))
            elif m_type == "Cycle Count Adjustment":
                dest_wh = None
                qty = int(rng.integers(-15, 16)) # signed discrepancy
                if qty == 0:
                    qty = 5
                freight = 0.0
                transit_days = 0
            else: # Spoilage / Damage
                dest_wh = None
                qty = -int(rng.integers(5, 50)) # negative decrement
                freight = 0.0
                transit_days = 0
                
            movement_records.append({
                "MovementKey": mov_key,
                "MovementTransactionID": f"MV-{cur_date.year}-{txn_counter:07d}",
                "MovementDateKey": date_to_key(cur_date),
                "MovementDate": cur_date,
                "ProductKey": p_key,
                "ProductSKU": sku,
                "OriginWarehouseKey": orig_wh,
                "DestinationWarehouseKey": dest_wh,
                "ResponsibleEmployeeKey": int(rng.choice(planner_keys)),
                "MovementType": m_type,
                "MovementQuantity": qty,
                "MovementValue": round(abs(qty) * cost, 2),
                "TransferFreightCost": freight,
                "TransferTransitDays": transit_days
            })
            mov_key += 1
            txn_counter += 1
            
    df_mov = pd.DataFrame(movement_records)
    print(f"Generated {len(df_mov):,} inventory movement records.")
    return df_mov
