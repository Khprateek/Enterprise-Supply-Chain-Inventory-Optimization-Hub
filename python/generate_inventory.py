# Stateful Inventory Snapshot Generator
import numpy as np
import pandas as pd
from datetime import date, timedelta
from python.config import ScaleConfig
from python.common import date_to_key

def generate_inventory(
    config: ScaleConfig,
    dimensions: dict,
    df_sales: pd.DataFrame,
    df_po: pd.DataFrame,
    active_pairs: list,
    rng: np.random.Generator,
    df_movements: pd.DataFrame = None,
    **kwargs
):
    print("--- Generating Stateful Inventory Snapshots (FactInventorySnapshot) ---")
    
    start_snapshot_key = kwargs.get("start_snapshot_key", 1)
    prior_state = kwargs.get("prior_state", {})

    dim_product = dimensions["DimProduct"]
    curr_prods = dim_product[dim_product["IsCurrent"]].copy()
    sku_to_pk = dict(zip(curr_prods["ProductSKU"], curr_prods["ProductKey"]))
    sku_to_cost = dict(zip(curr_prods["ProductSKU"], curr_prods["UnitStandardCost"]))
    
    # Pre-aggregate outbound sales demand by (Date, SKU, Warehouse)
    sales_agg = df_sales.groupby(["OrderDate", "ProductSKU", "WarehouseKey"])["ShippedQuantity"].sum().to_dict()
    
    # Pre-aggregate inbound PO receipts by (DockDate, SKU, Warehouse)
    po_completed = df_po[df_po["POStatus"] == "Completed"].copy()
    po_agg = po_completed.groupby(["ActualDockReceiptDate", "ProductSKU", "ReceivingWarehouseKey"])["AcceptedQuantity"].sum().to_dict()
    
    # Pre-aggregate physical inventory movements (Transfers, Damage, Scrap, Cycle Counts)
    movement_agg = {}
    if df_movements is not None and not df_movements.empty:
        for _, m_row in df_movements.iterrows():
            m_type = m_row["MovementType"]
            m_qty = int(m_row["MovementQuantity"])
            orig_wh = int(m_row["OriginWarehouseKey"])
            m_date = m_row["MovementDate"]
            m_sku = m_row["ProductSKU"]
            
            if m_type == "Inter-DC Transfer":
                # Decrement origin DC
                k_orig = (m_date, m_sku, orig_wh)
                movement_agg[k_orig] = movement_agg.get(k_orig, 0) - abs(m_qty)
                # Increment destination DC upon transit arrival
                dest_wh = m_row["DestinationWarehouseKey"]
                if pd.notna(dest_wh):
                    transit = int(m_row.get("TransferTransitDays", 1))
                    arr_date = m_date + timedelta(days=transit)
                    k_dest = (arr_date, m_sku, int(dest_wh))
                    movement_agg[k_dest] = movement_agg.get(k_dest, 0) + abs(m_qty)
            elif m_type in ["Spoilage Scrap", "Damage Write-off"]:
                # Scrap / damage decrement at facility
                k_orig = (m_date, m_sku, orig_wh)
                movement_agg[k_orig] = movement_agg.get(k_orig, 0) - abs(m_qty)
            elif m_type == "Cycle Count Adjustment":
                # Signed physical inventory count reconciliation
                k_orig = (m_date, m_sku, orig_wh)
                movement_agg[k_orig] = movement_agg.get(k_orig, 0) + m_qty
    
    total_days = (config.end_date - config.start_date).days + 1
    dates = [config.start_date + timedelta(days=i) for i in range(total_days)]
    
    snapshot_records = []
    snapshot_key = start_snapshot_key
    
    # Initialize state for each active pair
    for sku, wh_key in active_pairs:
        p_key = sku_to_pk[sku]
        unit_cost = sku_to_cost[sku]
        
        pair_state = prior_state.get((sku, wh_key))
        if pair_state:
            curr_on_hand = pair_state["on_hand"]
            days_stagnant = pair_state["days_stagnant"]
        else:
            # Initial starting inventory on day 0
            curr_on_hand = int(rng.choice([1500, 3000, 5000, 8000]))
            days_stagnant = int(rng.integers(0, 15))
        
        for cur_date in dates:
            # 1. Inbound receipts for today
            inbound = po_agg.get((cur_date, sku, wh_key), 0)
            
            # 2. Outbound sales for today
            outbound = sales_agg.get((cur_date, sku, wh_key), 0)
            
            # 3. Inventory movements net delta (transfers, scrap, adjustments)
            movement_net = movement_agg.get((cur_date, sku, wh_key), 0)
            
            # 4. Stateful balance continuity
            curr_on_hand = max(0, curr_on_hand + inbound - outbound + movement_net)
            
            # Reserved stock
            reserved = min(curr_on_hand, int(round(outbound * rng.uniform(0.5, 1.2))))
            avail = max(0, curr_on_hand - reserved)
            
            # Aging
            if outbound > 0 or inbound > 0 or movement_net != 0:
                days_stagnant = 0
            else:
                days_stagnant += 1
                
            is_stockout = 1 if avail <= 0 else 0
            is_dead = 1 if days_stagnant >= 180 else 0
            val = round(curr_on_hand * unit_cost, 2)
            
            # Pipeline in-transit placeholder
            in_transit = 0
            
            snapshot_records.append({
                "SnapshotKey": snapshot_key,
                "SnapshotDateKey": date_to_key(cur_date),
                "SnapshotDate": cur_date,
                "ProductKey": p_key,
                "ProductSKU": sku,
                "WarehouseKey": wh_key,
                "OnHandQuantity": curr_on_hand,
                "ReservedQuantity": reserved,
                "AvailableQuantity": avail,
                "InTransitInboundQuantity": in_transit,
                "UnitLandedCost": unit_cost,
                "InventoryValuation": val,
                "DaysSinceLastMovement": days_stagnant,
                "IsStockoutFlag": is_stockout,
                "IsDeadStockFlag": is_dead
            })
            snapshot_key += 1
            
        # After completing all dates for this pair, save the final state
        prior_state[(sku, wh_key)] = {
            "on_hand": curr_on_hand,
            "days_stagnant": days_stagnant
        }
            
    df_snapshot = pd.DataFrame(snapshot_records)
    print(f"Generated {len(df_snapshot):,} inventory snapshot rows.")
    return df_snapshot, snapshot_key, prior_state
