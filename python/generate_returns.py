# Customer Returns & Reverse Logistics Generator
import numpy as np
import pandas as pd
from datetime import timedelta
from python.common import date_to_key

def generate_returns(dimensions: dict, df_sales: pd.DataFrame, rng: np.random.Generator):
    print("--- Generating Customer Returns (FactCustomerReturns) ---")
    
    dim_customer = dimensions["DimCustomerChannel"]
    ch_map = dict(zip(dim_customer["CustomerChannelKey"], dim_customer["ChannelName"]))
    
    reasons = ["Defective Item", "Shipping Damage", "Wrong Item Shipped", "Customer Remorse"]
    reason_probs = [0.35, 0.25, 0.15, 0.25]
    
    return_records = []
    ret_key = 1
    rma_counter = 1000
    
    # Sub-sample sales lines for returns based on channel return propensity
    for idx, sale in df_sales.iterrows():
        ch_name = ch_map.get(sale["CustomerChannelKey"], "Retail Chain Stores")
        
        # Channel return probability
        if ch_name == "Wholesale B2B":
            ret_prob = 0.015
        elif ch_name == "Retail Chain Stores":
            ret_prob = 0.035
        else: # E-Commerce
            ret_prob = 0.085
            
        if rng.random() < ret_prob:
            ship_qty = sale["ShippedQuantity"]
            if ship_qty <= 0:
                continue
                
            # Return units (partial or full line)
            ret_qty = max(1, int(round(ship_qty * rng.uniform(0.2, 1.0))))
            
            # Return lag (3 to 21 days)
            lag_days = int(rng.integers(3, 22))
            ret_date = sale["OrderDate"] + timedelta(days=lag_days)
            
            # Disposition: 80% restocked, 20% scrapped
            is_restocked = rng.random() < 0.80
            if is_restocked:
                restocked_qty = ret_qty
                scrapped_qty = 0
                disposition = "Restocked"
            else:
                restocked_qty = 0
                scrapped_qty = ret_qty
                disposition = "Scrapped"
                
            refund_amt = round(ret_qty * sale["UnitPrice"], 2)
            reason = rng.choice(reasons, p=reason_probs)
            
            return_records.append({
                "ReturnLineKey": ret_key,
                "ReturnID": f"RMA-{ret_date.year}-{rma_counter:06d}",
                "ReturnDateKey": date_to_key(ret_date),
                "OriginalOrderDateKey": sale["OrderDateKey"],
                "ReturnDate": ret_date,
                "OriginalOrderDate": sale["OrderDate"],
                "ProductKey": sale["ProductKey"],
                "ProductSKU": sale["ProductSKU"],
                "ReceivingWarehouseKey": sale["WarehouseKey"],
                "CustomerChannelKey": sale["CustomerChannelKey"],
                "ReturnedQuantity": ret_qty,
                "RestockedQuantity": restocked_qty,
                "ScrappedQuantity": scrapped_qty,
                "RefundAmount": refund_amt,
                "ReturnReasonCategory": reason,
                "DispositionStatus": disposition
            })
            ret_key += 1
            rma_counter += 1
            
    df_returns = pd.DataFrame(return_records)
    print(f"Generated {len(df_returns):,} customer return records.")
    return df_returns
