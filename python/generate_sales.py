# Outbound Sales Fulfillment Generator
import numpy as np
import pandas as pd
from datetime import date, timedelta
from python.config import ScaleConfig
from python.common import date_to_key

def generate_sales(config: ScaleConfig, dimensions: dict, active_pairs: list, rng: np.random.Generator, dormant_pairs: set = None):
    print("--- Generating Sales (FactSales) ---")
    
    if dormant_pairs is None:
        dormant_pairs = set()
    dormant_cutoff_date = config.start_date + timedelta(days=120)
    
    dim_product = dimensions["DimProduct"]
    dim_customer = dimensions["DimCustomerChannel"]
    dim_warehouse = dimensions["DimWarehouse"]
    
    # Build temporal product version lookups for SCD Type 2 point-in-time resolution
    early_map = {}
    late_map = {}
    for _, row in dim_product.iterrows():
        sku = row["ProductSKU"]
        info = {
            "key": int(row["ProductKey"]),
            "cost": float(row["UnitStandardCost"]),
            "price": float(row["UnitListPrice"]),
            "abc": row["ABCClassification"]
        }
        if row["IsCurrent"]:
            late_map[sku] = info
            if sku not in early_map:
                early_map[sku] = info
        else:
            early_map[sku] = info
    
    sku_to_abc = {sku: late_map[sku]["abc"] for sku in late_map}
    hist_cut_date = date(2024, 7, 1)
    
    cust_keys = dim_customer["CustomerChannelKey"].values
    cust_channel_map = dict(zip(dim_customer["CustomerChannelKey"], dim_customer["ChannelName"]))
    
    wh_region_map = dict(zip(dim_warehouse["WarehouseKey"], dim_warehouse["RegionKey"]))
    
    # Filter active pairs
    active_skus = list(set([p[0] for p in active_pairs]))
    sku_to_whs = {}
    for s, w in active_pairs:
        sku_to_whs.setdefault(s, []).append(w)
        
    # Weight SKUs by popularity (Pareto)
    sku_weights = []
    for s in active_skus:
        abc = sku_to_abc.get(s, "C")
        if abc == "A":
            w = 8.0
        elif abc == "B":
            w = 2.5
        else:
            w = 0.5
        sku_weights.append(w)
    sku_weights = np.array(sku_weights) / sum(sku_weights)
    
    total_days = (config.end_date - config.start_date).days + 1
    
    sales_records = []
    sales_line_key = 1
    order_counter = 10000
    
    # Pre-generate dates and seasonal multipliers
    dates = [config.start_date + timedelta(days=i) for i in range(total_days)]
    
    for current_date in dates:
        # Multiplicative seasonality
        # Annual
        month = current_date.month
        if month in [11, 12]:
            s_annual = 1.35
        elif month in [6, 7, 8]:
            s_annual = 1.15
        elif month in [1, 2]:
            s_annual = 0.82
        else:
            s_annual = 1.00
            
        # Weekly
        dow = current_date.weekday() # 0=Mon, 6=Sun
        s_weekly = 1.20 if dow < 5 else 0.70
        
        daily_order_target = int(round(config.daily_sales_orders_avg * s_annual * s_weekly))
        daily_order_count = max(5, int(rng.poisson(daily_order_target)))
        
        prod_map = early_map if current_date < hist_cut_date else late_map
        
        # Sample customers for today
        day_custs = rng.choice(cust_keys, size=daily_order_count, replace=True)
        
        for o_idx in range(daily_order_count):
            cust_k = day_custs[o_idx]
            ch_name = cust_channel_map[cust_k]
            
            # Determine line count per order based on customer channel
            if ch_name == "Wholesale B2B":
                num_lines = int(rng.choice([1, 2, 3, 4], p=[0.40, 0.35, 0.15, 0.10]))
            elif ch_name == "Retail Chain Stores":
                num_lines = int(rng.choice([1, 2, 3], p=[0.50, 0.35, 0.15]))
            else: # E-Commerce Direct
                num_lines = int(rng.choice([1, 2], p=[0.85, 0.15]))
                
            # Cycle time for the order header (1-3 days)
            cycle_days = int(rng.choice([1, 2, 3], p=[0.60, 0.30, 0.10]))
            ship_date = current_date + timedelta(days=cycle_days)
            deliv_date = ship_date + timedelta(days=int(rng.integers(1, 4)))
            
            order_id = f"SO-{current_date.year}-{order_counter:07d}"
            
            # Sample distinct SKUs for this order
            order_skus = rng.choice(active_skus, size=num_lines, p=sku_weights, replace=False)
            
            line_no = 1
            for sku in order_skus:
                # Select warehouse stocking this SKU
                avail_whs = sku_to_whs.get(sku, [1])
                if current_date >= dormant_cutoff_date and dormant_pairs:
                    filtered_whs = [w for w in avail_whs if (sku, w) not in dormant_pairs]
                    if filtered_whs:
                        avail_whs = filtered_whs
                    else:
                        continue # Skip dormant/discontinued pair
                wh_k = int(rng.choice(avail_whs))
                
                p_info = prod_map[sku]
                p_key = p_info["key"]
                unit_cost = p_info["cost"]
                unit_price = p_info["price"]
                abc = p_info["abc"]
                
                # Order quantity based on channel & ABC
                if ch_name == "Wholesale B2B":
                    base_q = 120 if abc == "A" else (50 if abc == "B" else 20)
                    disc_rate = float(rng.uniform(0.08, 0.18))
                elif ch_name == "Retail Chain Stores":
                    base_q = 60 if abc == "A" else (25 if abc == "B" else 10)
                    disc_rate = float(rng.uniform(0.03, 0.10))
                else: # E-Commerce
                    base_q = 3 if abc == "A" else (2 if abc == "B" else 1)
                    disc_rate = float(rng.uniform(0.00, 0.05))
                    
                ord_qty = max(1, int(rng.poisson(base_q)))
                
                # Shipment fulfillment (96% initial fulfillment probability, subject to stock in inventory generator)
                is_full = rng.random() < 0.96
                ship_qty = ord_qty if is_full else max(0, int(round(ord_qty * rng.uniform(0.70, 0.95))))
                canc_qty = ord_qty - ship_qty
                
                gross_sales = round(ord_qty * unit_price, 2)
                disc_amt = round(gross_sales * disc_rate, 2)
                net_sales = round(ship_qty * unit_price - disc_amt, 2)
                cogs = round(ship_qty * unit_cost, 2)
                
                is_otif = 1 if (is_full and cycle_days <= 2) else 0
                
                sales_records.append({
                    "SalesLineKey": sales_line_key,
                    "SalesOrderID": order_id,
                    "SalesOrderLineNumber": line_no,
                    "OrderDateKey": date_to_key(current_date),
                    "ShipDateKey": date_to_key(ship_date),
                    "DeliveryDateKey": date_to_key(deliv_date),
                    "OrderDate": current_date,
                    "ShipDate": ship_date,
                    "DeliveryDate": deliv_date,
                    "ProductKey": p_key,
                    "ProductSKU": sku,
                    "CustomerChannelKey": cust_k,
                    "WarehouseKey": wh_k,
                    "OrderedQuantity": ord_qty,
                    "ShippedQuantity": ship_qty,
                    "CancelledQuantity": canc_qty,
                    "UnitPrice": unit_price,
                    "UnitStandardCost": unit_cost,
                    "GrossSalesAmount": gross_sales,
                    "DiscountAmount": disc_amt,
                    "NetSalesAmount": net_sales,
                    "CostOfGoodsSold": cogs,
                    "OrderLineCycleTimeDays": cycle_days,
                    "OnTimeInFullFlag": is_otif
                })
                
                sales_line_key += 1
                line_no += 1
                
            order_counter += 1
            
    df_sales = pd.DataFrame(sales_records)
    print(f"Generated {len(df_sales):,} sales order lines.")
    return df_sales
