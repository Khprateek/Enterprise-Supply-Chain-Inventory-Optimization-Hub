import pandas as pd
import numpy as np
from datetime import timedelta

def enrich_data():
    print("--- Starting Data Enrichment for Industry Realism ---")
    rng = np.random.default_rng(42)
    
    # 1. Load Dimensions
    df_wh = pd.read_parquet('data/raw/DimWarehouse.parquet')
    df_reg = pd.read_parquet('data/raw/DimRegion.parquet')
    wh_to_reg = dict(zip(df_wh['WarehouseKey'], df_wh['RegionKey']))
    reg_key_to_name = dict(zip(df_reg['RegionKey'], df_reg['RegionName']))
    wh_to_reg_name = {w: reg_key_to_name[r] for w, r in wh_to_reg.items()}
    
    # 2. Enrich FactSales (Regional OTIF Variation)
    print("Enriching FactSales...")
    df_sales = pd.read_parquet('data/raw/FactSales.parquet')
    reg_names = df_sales['WarehouseKey'].map(wh_to_reg_name)
    
    # Target OTIF rates by region:
    # APAC: 81.5% (< 85% -> High Risk)
    # NA East: 86.4% (Moderate Risk)
    # NA West: 87.2% (Moderate Risk)
    # NA Midwest: 93.2% (Normal Risk)
    # Europe Central: 91.5% (Normal Risk)
    # Europe West & UK: 89.4% (Normal Risk)
    otif_targets = {
        'APAC Southeast Asia': 0.815,
        'North America East': 0.864,
        'North America West': 0.872,
        'North America Midwest': 0.932,
        'Europe Central': 0.915,
        'Europe West & UK': 0.894
    }
    
    otif_flags = []
    cycle_days_list = []
    
    for r_name in reg_names:
        target_otif = otif_targets.get(r_name, 0.864)
        is_otif = 1 if rng.random() < target_otif else 0
        otif_flags.append(is_otif)
        if is_otif == 1:
            cycle_days_list.append(int(rng.choice([1, 2], p=[0.7, 0.3])))
        else:
            cycle_days_list.append(int(rng.choice([3, 4, 5], p=[0.6, 0.3, 0.1])))
            
    df_sales['OnTimeInFullFlag'] = otif_flags
    df_sales['OrderLineCycleTimeDays'] = cycle_days_list
    
    df_sales.to_parquet('data/raw/FactSales.parquet', index=False)
    print(f"FactSales updated ({len(df_sales):,} rows).")
    
    # 3. Enrich FactInventorySnapshot (Aging Buckets + Regional Stockouts)
    print("Enriching FactInventorySnapshot...")
    df_inv = pd.read_parquet('data/raw/FactInventorySnapshot.parquet')
    
    # Regional Stockout Rates:
    # Target Stockouts:
    # APAC: 0.25% (> 0.1% -> High Risk)
    # NA East: 0.16% (> 0.1% -> Moderate Risk)
    # NA West: 0.14% (> 0.1% -> Moderate Risk)
    # NA Midwest: 0.05% (<= 0.1% -> Normal Risk)
    # Europe Central: 0.06% (<= 0.1% -> Normal Risk)
    # Europe West & UK: 0.07% (<= 0.1% -> Normal Risk)
    stockout_targets = {
        'APAC Southeast Asia': 0.0025,
        'North America East': 0.0016,
        'North America West': 0.0014,
        'North America Midwest': 0.0005,
        'Europe Central': 0.0006,
        'Europe West & UK': 0.0007
    }
    
    inv_reg_names = df_inv['WarehouseKey'].map(wh_to_reg_name)
    stockout_probs = inv_reg_names.map(stockout_targets).fillna(0.001).values
    df_inv['IsStockoutFlag'] = (rng.random(len(df_inv)) < stockout_probs).astype(int)
    
    # 4. Inventory Aging Stratification on Snapshot Date
    max_date = df_inv['SnapshotDate'].max()
    latest_mask = df_inv['SnapshotDate'] == max_date
    latest_indices = df_inv[latest_mask].index.values
    
    shuffled_idx = rng.permutation(latest_indices)
    shuffled_vals = df_inv.loc[shuffled_idx, 'InventoryValuation'].values
    cum_vals = np.cumsum(shuffled_vals)
    total_val = cum_vals[-1]
    print(f"Total Valuation on {max_date}: ${total_val:,.2f}")
    
    dead_target = total_val * 0.0200      # ~2% ($594M)
    stagnant_target = total_val * 0.1400  # cum ~14% (12% stagnant)
    slow_target = total_val * 0.3600      # cum ~36% (22% slow moving)
    
    idx_dead = shuffled_idx[cum_vals <= dead_target]
    idx_stagnant = shuffled_idx[(cum_vals > dead_target) & (cum_vals <= stagnant_target)]
    idx_slow = shuffled_idx[(cum_vals > stagnant_target) & (cum_vals <= slow_target)]
    idx_healthy = shuffled_idx[cum_vals > slow_target]
    
    print(f"Dead Stock count: {len(idx_dead)}, Valuation: ${df_inv.loc[idx_dead, 'InventoryValuation'].sum():,.2f}")
    print(f"Stagnant count: {len(idx_stagnant)}, Valuation: ${df_inv.loc[idx_stagnant, 'InventoryValuation'].sum():,.2f}")
    print(f"Slow count: {len(idx_slow)}, Valuation: ${df_inv.loc[idx_slow, 'InventoryValuation'].sum():,.2f}")
    print(f"Healthy count: {len(idx_healthy)}, Valuation: ${df_inv.loc[idx_healthy, 'InventoryValuation'].sum():,.2f}")
    
    df_inv.loc[idx_dead, 'DaysSinceLastMovement'] = rng.integers(185, 270, size=len(idx_dead))
    df_inv.loc[idx_dead, 'IsDeadStockFlag'] = 1
    
    df_inv.loc[idx_stagnant, 'DaysSinceLastMovement'] = rng.integers(122, 179, size=len(idx_stagnant))
    df_inv.loc[idx_stagnant, 'IsDeadStockFlag'] = 0
    
    df_inv.loc[idx_slow, 'DaysSinceLastMovement'] = rng.integers(62, 118, size=len(idx_slow))
    df_inv.loc[idx_slow, 'IsDeadStockFlag'] = 0
    
    df_inv.loc[idx_healthy, 'DaysSinceLastMovement'] = rng.integers(1, 45, size=len(idx_healthy))
    df_inv.loc[idx_healthy, 'IsDeadStockFlag'] = 0
    
    df_inv.to_parquet('data/raw/FactInventorySnapshot.parquet', index=False)
    print("FactInventorySnapshot updated and saved.")
    print("Enrichment complete!")

if __name__ == "__main__":
    enrich_data()
