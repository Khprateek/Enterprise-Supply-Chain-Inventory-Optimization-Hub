# Derived Stockout Outage Events Generator
import numpy as np
import pandas as pd
from datetime import timedelta
from python.common import date_to_key

def generate_stockouts(dimensions: dict, df_inventory: pd.DataFrame, df_sales: pd.DataFrame, rng: np.random.Generator):
    print("--- Deriving Stockout Outage Events (FactStockout) ---")
    
    dim_product = dimensions["DimProduct"]
    curr_prods = dim_product[dim_product["IsCurrent"]].copy()
    sku_to_price = dict(zip(curr_prods["ProductSKU"], curr_prods["UnitListPrice"]))
    sku_to_abc = dict(zip(curr_prods["ProductSKU"], curr_prods["ABCClassification"]))
    
    # Pre-calculate daily average sales per SKU-warehouse for lost demand estimation
    avg_sales = df_sales.groupby(["ProductSKU", "WarehouseKey"])["OrderedQuantity"].mean().to_dict()
    
    # Filter snapshot rows with zero available inventory
    zero_inv = df_inventory[df_inventory["AvailableQuantity"] <= 0].sort_values(["ProductSKU", "WarehouseKey", "SnapshotDate"]).copy()
    
    if len(zero_inv) == 0:
        print("No zero inventory snapshots detected. Creating empty FactStockout.")
        return pd.DataFrame(columns=[
            "StockoutEventKey", "StartDateKey", "EndDateKey", "StartDate", "EndDate",
            "ProductKey", "ProductSKU", "WarehouseKey", "StockoutDurationDays",
            "EstimatedLostDemandUnits", "EstimatedLostRevenueAmount", "StockoutAttributedReason", "SeverityTier"
        ])
        
    stockout_events = []
    event_key = 1
    
    reasons = ["Supplier Delayed Inbound", "Unexpected Demand Surge", "Inventory Record Inaccuracy", "Quality Hold"]
    reason_probs = [0.50, 0.30, 0.15, 0.05]
    
    # Group by (ProductSKU, WarehouseKey) and consolidate contiguous dates
    for (sku, wh_k), group in zero_inv.groupby(["ProductSKU", "WarehouseKey"]):
        dates = group["SnapshotDate"].tolist()
        p_key = group["ProductKey"].iloc[0]
        price = sku_to_price.get(sku, 5.0)
        abc = sku_to_abc.get(sku, "C")
        daily_velocity = avg_sales.get((sku, wh_k), 5.0)
        
        # Consolidate consecutive dates
        start_d = dates[0]
        prev_d = dates[0]
        
        for i in range(1, len(dates)):
            curr_d = dates[i]
            if curr_d == prev_d + timedelta(days=1):
                prev_d = curr_d
            else:
                # Contiguous block ended
                duration = (prev_d - start_d).days + 1
                lost_units = max(1, int(round(daily_velocity * duration)))
                lost_rev = round(lost_units * price, 2)
                reason = rng.choice(reasons, p=reason_probs)
                sev = "Critical Tier A" if abc == "A" else ("Moderate Tier B" if abc == "B" else "Low Tier C")
                
                stockout_events.append({
                    "StockoutEventKey": event_key,
                    "StartDateKey": date_to_key(start_d),
                    "EndDateKey": date_to_key(prev_d),
                    "StartDate": start_d,
                    "EndDate": prev_d,
                    "ProductKey": p_key,
                    "ProductSKU": sku,
                    "WarehouseKey": wh_k,
                    "StockoutDurationDays": duration,
                    "EstimatedLostDemandUnits": lost_units,
                    "EstimatedLostRevenueAmount": lost_rev,
                    "StockoutAttributedReason": reason,
                    "SeverityTier": sev
                })
                event_key += 1
                start_d = curr_d
                prev_d = curr_d
                
        # Final block
        duration = (prev_d - start_d).days + 1
        lost_units = max(1, int(round(daily_velocity * duration)))
        lost_rev = round(lost_units * price, 2)
        reason = rng.choice(reasons, p=reason_probs)
        sev = "Critical Tier A" if abc == "A" else ("Moderate Tier B" if abc == "B" else "Low Tier C")
        
        stockout_events.append({
            "StockoutEventKey": event_key,
            "StartDateKey": date_to_key(start_d),
            "EndDateKey": date_to_key(prev_d),
            "StartDate": start_d,
            "EndDate": prev_d,
            "ProductKey": p_key,
            "ProductSKU": sku,
            "WarehouseKey": wh_k,
            "StockoutDurationDays": duration,
            "EstimatedLostDemandUnits": lost_units,
            "EstimatedLostRevenueAmount": lost_rev,
            "StockoutAttributedReason": reason,
            "SeverityTier": sev
        })
        event_key += 1
        
    df_stockout = pd.DataFrame(stockout_events)
    print(f"Consolidated {len(zero_inv):,} zero-stock snapshots into {len(df_stockout):,} distinct outage events.")
    return df_stockout
