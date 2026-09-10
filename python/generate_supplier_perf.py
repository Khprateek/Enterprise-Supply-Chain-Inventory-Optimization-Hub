# Materialized Monthly Supplier Performance Mart Generator
import numpy as np
import pandas as pd
from datetime import date
from python.common import date_to_key

def generate_supplier_performance(dimensions: dict, df_po: pd.DataFrame):
    print("--- Materializing Monthly Supplier Performance (FactSupplierMonthlyPerformance) ---")
    
    # Filter completed POs
    df_po_work = df_po[df_po["POStatus"] == "Completed"].copy()
    
    if len(df_po_work) == 0:
        return pd.DataFrame()
        
    df_po_work["YearMonth"] = df_po_work["POCreationDate"].apply(lambda d: f"{d.year}-{d.month:02d}")
    
    perf_records = []
    perf_key = 1
    
    for (s_key, ym), group in df_po_work.groupby(["SupplierKey", "YearMonth"]):
        y, m = map(int, ym.split("-"))
        ym_date = date(y, m, 1)
        
        tot_pos = group["PurchaseOrderID"].nunique()
        tot_lines = len(group)
        tot_ord_qty = int(group["OrderedQuantity"].sum())
        tot_rec_qty = int(group["ReceivedQuantity"].sum())
        tot_rej_qty = int(group["RejectedQuantity"].sum())
        tot_spend = round(float(group["ExtendedPOAmount"].sum()), 2)
        
        ontime_lines = int(group["IsDeliveredOnTimeFlag"].sum())
        infull_lines = int(group["IsDeliveredInFullFlag"].sum())
        otif_lines = int(group["IsSupplierOTIFFlag"].sum())
        late_lines = tot_lines - ontime_lines
        
        otif_rate = round((otif_lines / tot_lines) * 100.0, 2) if tot_lines > 0 else 100.0
        line_fill_rate = round((tot_rec_qty / tot_ord_qty) * 100.0, 2) if tot_ord_qty > 0 else 100.0
        
        # Lead time statistics
        lt_series = group["ActualLeadTimeDays"].dropna()
        avg_lt = round(float(lt_series.mean()), 2) if len(lt_series) > 0 else 14.0
        std_lt = round(float(lt_series.std()), 2) if len(lt_series) > 1 else 1.0
        if np.isnan(std_lt):
            std_lt = 0.5
            
        # Risk classification
        if otif_rate >= 90.0 and std_lt <= 3.0:
            risk = "Low Risk (Compliant)"
        elif otif_rate >= 78.0:
            risk = "Moderate Risk (Watchlist)"
        else:
            risk = "Critical SLA Breach"
            
        perf_records.append({
            "SupplierMonthlyKey": perf_key,
            "YearMonthDateKey": date_to_key(ym_date),
            "YearMonthDate": ym_date,
            "SupplierKey": s_key,
            "YearMonth": ym,
            "TotalPOCount": tot_pos,
            "TotalPOLines": tot_lines,
            "TotalOrderedQuantity": tot_ord_qty,
            "TotalReceivedQuantity": tot_rec_qty,
            "TotalRejectedQuantity": tot_rej_qty,
            "TotalSpendAmount": tot_spend,
            "OnTimePOCount": ontime_lines,
            "InFullPOCount": infull_lines,
            "OTIFLineCount": otif_lines,
            "OTIFRatePct": otif_rate,
            "AverageLeadTimeDays": avg_lt,
            "LeadTimeStdDevDays": std_lt,
            "LateDeliveryCount": late_lines,
            "LineFillRatePct": line_fill_rate,
            "SupplierMonthlyRiskRating": risk
        })
        perf_key += 1
        
    df_perf = pd.DataFrame(perf_records)
    print(f"Materialized {len(df_perf):,} monthly supplier scorecard records.")
    return df_perf
