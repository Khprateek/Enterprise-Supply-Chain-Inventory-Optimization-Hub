# Outbound Sales Fulfillment Generator
import numpy as np
import pandas as pd
from datetime import date, timedelta
from python.config import ScaleConfig
from python.common import date_to_key

def generate_sales(config: ScaleConfig, dimensions: dict, active_pairs: list, rng: np.random.Generator):
    print("--- Generating Sales (FactSales) ---")
    
    dim_product = dimensions["DimProduct"]
    dim_customer = dimensions["DimCustomerChannel"]
    dim_warehouse = dimensions["DimWarehouse"]
    
    # Map products
    curr_prods = dim_product[dim_product["IsCurrent"]].copy()
    sku_to_pk = dict(zip(curr_prods["ProductSKU"], curr_prods["ProductKey"]))
    sku_to_cost = dict(zip(curr_prods["ProductSKU"], curr_prods["UnitStandardCost"]))
    sku_to_price = dict(zip(curr_prods["ProductSKU"], curr_prods["UnitListPrice"]))
    sku_to_abc = dict(zip(curr_prods["ProductSKU"], curr_prods["ABCClassification"]))
    
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
        
        # Sample customers for today
        day_custs = rng.choice(cust_keys, size=daily_order_count, replace=True)
        # Sample SKUs for today
        day_skus = rng.choice(active_skus, size=daily_order_count, p=sku_weights, replace=True)
        
        for o_idx in range(daily_order_count):
            cust_k = day_custs[o_idx]
            sku = day_skus[o_idx]
            ch_name = cust_channel_map[cust_k]
            
            # Select warehouse stocking this SKU
            avail_whs = sku_to_whs.get(sku, [1])
            wh_k = int(rng.choice(avail_whs))
            
            p_key = sku_to_pk[sku]
            unit_cost = sku_to_cost[sku]
            unit_price = sku_to_price[sku]
            abc = sku_to_abc[sku]
            
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
            
            # Cycle time (1-3 days)
            cycle_days = int(rng.choice([1, 2, 3], p=[0.60, 0.30, 0.10]))
            ship_date = current_date + timedelta(days=cycle_days)
            deliv_date = ship_date + timedelta(days=int(rng.integers(1, 4)))
            
            gross_sales = round(ord_qty * unit_price, 2)
            disc_amt = round(gross_sales * disc_rate, 2)
            net_sales = round(ship_qty * unit_price - disc_amt, 2)
            cogs = round(ship_qty * unit_cost, 2)
            
            is_otif = 1 if (is_full and cycle_days <= 2) else 0
            
            sales_records.append({
                "SalesLineKey": sales_line_key,
                "SalesOrderID": f"SO-{current_date.year}-{order_counter:07d}",
                "SalesOrderLineNumber": 1,
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
            order_counter += 1
            
    df_sales = pd.DataFrame(sales_records)
    print(f"Generated {len(df_sales):,} sales order lines.")
    return df_sales
