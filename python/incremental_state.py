import os
import json
from datetime import date

STATE_FILE = "data/raw/incremental_state.json"

def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state: dict):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def get_incremental_start_date(scale_name: str, config_start_date: date) -> date:
    state = load_state()
    if state.get("scale") == scale_name and "last_date" in state:
        # Increment by 1 day from the last successfully generated date
        last_date = date.fromisoformat(state["last_date"])
        import datetime
        return last_date + datetime.timedelta(days=1)
    return config_start_date

def get_max_keys(scale_name: str) -> tuple[int, int, int]:
    # Returns (sales_line_key, order_counter, snapshot_key)
    state = load_state()
    if state.get("scale") == scale_name and "max_keys" in state:
        mk = state["max_keys"]
        return mk.get("sales_line_key", 1), mk.get("order_counter", 10000), mk.get("snapshot_key", 1)
    return 1, 10000, 1

def get_inventory_state(scale_name: str) -> dict:
    state = load_state()
    if state.get("scale") == scale_name and "inventory_state" in state:
        # Convert string keys "SKU|WH" back to tuples ("SKU", WH_INT)
        inv_state = {}
        for k, v in state["inventory_state"].items():
            sku, wh = k.split("|")
            inv_state[(sku, int(wh))] = v
        return inv_state
    return {}

def update_state(scale_name: str, end_date: date, next_sales_line_key: int, next_order_counter: int, next_snapshot_key: int, inv_state: dict):
    state = load_state()
    state["scale"] = scale_name
    state["last_date"] = end_date.isoformat()
    if "max_keys" not in state:
        state["max_keys"] = {}
    state["max_keys"]["sales_line_key"] = next_sales_line_key
    state["max_keys"]["order_counter"] = next_order_counter
    state["max_keys"]["snapshot_key"] = next_snapshot_key
    
    # Serialize inventory state tuple keys to string
    state["inventory_state"] = {f"{k[0]}|{k[1]}": v for k, v in inv_state.items()}
    
    save_state(state)

