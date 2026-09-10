# Inbound Procurement & Purchase Orders Generator
import numpy as np
import pandas as pd
from datetime import date, timedelta
from python.config import ScaleConfig
from python.common import date_to_key

def generate_procurement(config: ScaleConfig, dimensions: dict, rng: np.random.Generator):
    print("--- Generating Procurement (FactPurchaseOrder) ---")
    
    dim_product = dimensions["DimProduct"]
    dim_supplier = dimensions["DimSupplier"]
    dim_warehouse = dimensions["DimWarehouse"]
    dim_planner = dimensions["DimEmployeePlanner"]
    
    # Active current products and mappings
    curr_prods = dim_product[dim_product["IsCurrent"]].copy()
    sku_list = curr_prods["ProductSKU"].values
    prod_key_map = dict(zip(curr_prods["ProductSKU"], curr_prods["ProductKey"]))
    supp_key_map = dict(zip(curr_prods["ProductSKU"], curr_prods["PrimarySupplierKey"]))
    cost_map = dict(zip(curr_prods["ProductSKU"], curr_prods["UnitStandardCost"]))
    
    supp_lead_time_map = dict(zip(dim_supplier["SupplierKey"], dim_supplier["ContractLeadTimeDays"]))
    supp_tier_map = dict(zip(dim_supplier["SupplierKey"], dim_supplier["SupplierTier"]))
    
    wh_keys = dim_warehouse["WarehouseKey"].values
    planner_keys = dim_planner["PlannerKey"].values
    
    # Generate PO schedule across active pairs
    # Determine active SKU-warehouse stocking pairs
    num_pairs = min(config.active_pairs_count, len(sku_list) * len(wh_keys))
    pair_skus = rng.choice(sku_list, size=num_pairs, replace=True)
    pair_whs = rng.choice(wh_keys, size=num_pairs, replace=True)
    active_pairs = list(set(zip(pair_skus, pair_whs)))
    
    total_days = (config.end_date - config.start_date).days + 1
    
    po_records = []
    po_line_key = 1
    po_counter = 1000
    
    # Generate periodic replenishment orders
    for sku, wh_key in active_pairs:
        supp_key = supp_key_map[sku]
        prod_key = prod_key_map[sku]
        unit_cost = cost_map[sku]
        contract_lt = supp_lead_time_map[supp_key]
        tier = supp_tier_map[supp_key]
        
        # Scheduling interval based on frequency
        interval = rng.integers(max(3, config.po_frequency_days - 2), config.po_frequency_days + 4)
        curr_offset = rng.integers(0, interval)
        
        while curr_offset < total_days:
            po_date = config.start_date + timedelta(days=int(curr_offset))
            if po_date > config.end_date:
                break
                
            promised_date = po_date + timedelta(days=int(contract_lt))
            
            # Actual lead time distribution based on vendor tier
            if tier == "Tier 1 Strategic":
                actual_lt = max(1, int(round(rng.normal(contract_lt, 1.2))))
                in_full_prob = 0.96
            elif tier == "Tier 2 Preferred":
                actual_lt = max(1, int(round(rng.normal(contract_lt + 0.5, 3.2))))
                in_full_prob = 0.88
            else: # Tier 3
                # Right-skewed delay
                actual_lt = max(1, int(round(contract_lt + rng.exponential(4.0))))
                in_full_prob = 0.76
                
            actual_dock_date = po_date + timedelta(days=int(actual_lt))
            
            # Batch order quantity
            ord_qty = int(rng.choice([100, 250, 500, 1000, 2000, 4000]))
            
            # Receipt quantity & defect rate
            if rng.random() < in_full_prob:
                rec_qty = ord_qty
            else:
                rec_qty = int(round(ord_qty * rng.uniform(0.70, 0.95)))
                
            defect_rate = rng.uniform(0.005, 0.03) if tier != "Tier 1 Strategic" else rng.uniform(0.001, 0.01)
            rej_qty = int(round(rec_qty * defect_rate))
            accepted_qty = rec_qty - rej_qty
            
            # Status
            if actual_dock_date <= config.end_date:
                status = "Completed"
                actual_key = date_to_key(actual_dock_date)
                is_on_time = int(actual_dock_date <= promised_date)
                is_in_full = int(rec_qty >= ord_qty)
            else:
                status = "Open In-Transit"
                actual_key = None
                is_on_time = 0
                is_in_full = 0
                
            is_otif = 1 if (is_on_time == 1 and is_in_full == 1) else 0
            
            po_records.append({
                "POLineKey": po_line_key,
                "PurchaseOrderID": f"PO-{po_date.year}-{po_counter:06d}",
                "POLineNumber": 1,
                "POCreationDateKey": date_to_key(po_date),
                "PromisedDeliveryDateKey": date_to_key(promised_date),
                "ActualDockReceiptDateKey": actual_key,
                "POCreationDate": po_date,
                "PromisedDeliveryDate": promised_date,
                "ActualDockReceiptDate": actual_dock_date if status == "Completed" else None,
                "SupplierKey": supp_key,
                "ProductKey": prod_key,
                "ProductSKU": sku,
                "ReceivingWarehouseKey": wh_key,
                "BuyerEmployeeKey": int(rng.choice(planner_keys)),
                "OrderedQuantity": ord_qty,
                "ReceivedQuantity": rec_qty if status == "Completed" else 0,
                "AcceptedQuantity": accepted_qty if status == "Completed" else 0,
                "RejectedQuantity": rej_qty if status == "Completed" else 0,
                "UnitPurchasePrice": unit_cost,
                "ExtendedPOAmount": round(ord_qty * unit_cost, 2),
                "PromisedLeadTimeDays": contract_lt,
                "ActualLeadTimeDays": actual_lt if status == "Completed" else None,
                "LeadTimeVarianceDays": (actual_lt - contract_lt) if status == "Completed" else None,
                "IsDeliveredOnTimeFlag": is_on_time,
                "IsDeliveredInFullFlag": is_in_full,
                "IsSupplierOTIFFlag": is_otif,
                "POStatus": status
            })
            
            po_line_key += 1
            po_counter += 1
            curr_offset += interval
            
    df_po = pd.DataFrame(po_records)
    print(f"Generated {len(df_po):,} purchase order lines.")
    return df_po, active_pairs
