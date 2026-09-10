# Conformed Dimensions Generator
import numpy as np
import pandas as pd
from datetime import date, timedelta
from python.config import ScaleConfig
from python.common import date_to_key

CATEGORIES = [
    ("Packaged Goods", "Beverages", ["Carbonated Soft Drinks", "Sparkling Water", "Ready-to-Drink Tea", "Fruit Juices", "Energy Drinks"]),
    ("Packaged Goods", "Snacks & Confectionery", ["Potato Crisps", "Tortilla Chips", "Chocolate Bars", "Gummy Candies", "Biscuits"]),
    ("Packaged Goods", "Dry Grocery", ["Pasta & Noodles", "Canned Soups", "Breakfast Cereals", "Cooking Oils", "Spices & Seasonings"]),
    ("Fresh/Chilled", "Dairy & Refrigerated", ["Fresh Milk", "Artisan Cheese", "Greek Yogurt", "Butter & Spreads", "Plant-Based Dairy"]),
    ("Fresh/Chilled", "Chilled Ready Meals", ["Fresh Pasta Meals", "Prepared Salads", "Deli Sandwiches", "Chilled Dips"]),
    ("Non-Food", "Personal Care & Hygiene", ["Shampoo & Haircare", "Body Wash & Soap", "Oral Care", "Deodorants", "Skincare Lotions"]),
    ("Non-Food", "Household Essentials", ["Laundry Detergent", "Surface Cleaners", "Paper Towels", "Trash Bags", "Dishwashing Liquids"]),
]

BRANDS = [
    "AuraPure", "CrispBite", "NatureCrest", "VelvetGlow", "VitalPulse",
    "TerraHarvest", "SwiftClean", "OceanMist", "PeakFrost", "PrimeSelect",
    "GoldenField", "UrbanEats", "EcoLiving", "ZenithHome", "CascadeBrook"
]

REGIONS_DATA = [
    ("REG-NA-EAST", "North America East", "Americas", "United States", "USD", "Marcus Vance"),
    ("REG-NA-MIDWEST", "North America Midwest", "Americas", "United States", "USD", "Sarah Jenkins"),
    ("REG-NA-WEST", "North America West", "Americas", "United States", "USD", "David Chen"),
    ("REG-EU-CENTRAL", "Europe Central", "EMEA", "Germany", "EUR", "Klaus Mueller"),
    ("REG-EU-WEST", "Europe West & UK", "EMEA", "United Kingdom", "GBP", "Emma Watson"),
    ("REG-APAC-SG", "APAC Southeast Asia", "APAC", "Singapore", "USD", "Li Wei"),
]

def generate_dimensions(config: ScaleConfig, rng: np.random.Generator):
    print(f"--- Generating Dimensions ({config.name} scale) ---")

    # 1. DimDate
    min_date = config.start_date - timedelta(days=365)
    max_date = config.end_date + timedelta(days=365)
    total_days = (max_date - min_date).days + 1
    dates = [min_date + timedelta(days=i) for i in range(total_days)]
    
    date_rows = []
    for d in dates:
        month_name = d.strftime("%B")
        day_name = d.strftime("%A")
        q = (d.month - 1) // 3 + 1
        is_wkend = d.weekday() >= 5
        # Seasonality period assignment
        if d.month in [11, 12]:
            season = "Peak Holiday"
        elif d.month in [7, 8]:
            season = "Summer High"
        elif d.month in [1, 2]:
            season = "Post-Holiday Lull"
        else:
            season = "Normal"
            
        date_rows.append({
            "DateKey": date_to_key(d),
            "FullDate": d,
            "DayOfWeek": (d.weekday() + 1) % 7 + 1, # 1=Sun, 7=Sat
            "DayName": day_name,
            "DayOfMonth": d.day,
            "DayOfYear": d.timetuple().tm_yday,
            "WeekOfYear": int(d.strftime("%W")),
            "MonthNumber": d.month,
            "MonthName": month_name,
            "MonthYear": d.strftime("%Y-%m"),
            "QuarterNumber": q,
            "QuarterName": f"Q{q}",
            "YearNumber": d.year,
            "FiscalMonthNumber": ((d.month + 2) % 12) + 1,
            "FiscalQuarter": f"FQ{q}",
            "FiscalYear": d.year,
            "IsWeekday": not is_wkend,
            "IsHoliday": (d.month == 1 and d.day == 1) or (d.month == 12 and d.day == 25),
            "SeasonalityPeriod": season
        })
    dim_date = pd.DataFrame(date_rows)

    # 2. DimRegion
    num_regions = min(len(REGIONS_DATA), config.num_regions)
    region_rows = []
    for i in range(num_regions):
        code, name, theater, country, curr, director = REGIONS_DATA[i]
        region_rows.append({
            "RegionKey": i + 1,
            "RegionCode": code,
            "RegionName": name,
            "Theater": theater,
            "PrimaryCountry": country,
            "CurrencyCode": curr,
            "RegionalDirector": director
        })
    dim_region = pd.DataFrame(region_rows)

    # 3. DimWarehouse
    wh_types = ["Central DC", "Regional DC", "E-Commerce Hub", "Transit Cross-Dock"]
    wh_rows = []
    for i in range(config.num_warehouses):
        r_key = (i % num_regions) + 1
        w_type = wh_types[i % len(wh_types)]
        cap = int(rng.choice([15000, 25000, 40000, 60000]))
        wh_rows.append({
            "WarehouseKey": i + 1,
            "WarehouseCode": f"DC-{i+1:03d}",
            "WarehouseName": f"Facility {i+1:03d} ({dim_region.loc[dim_region['RegionKey'] == r_key, 'RegionName'].values[0]})",
            "RegionKey": r_key,
            "FacilityType": w_type,
            "StorageCapacityPallets": cap,
            "TotalAreaSqMeters": cap * 2,
            "RefrigeratedCapacityPallets": cap // 5 if "Fresh" in w_type or i % 3 == 0 else 0,
            "OperatingHoursPerWeek": 168 if "Central" in w_type else 120,
            "ActiveFlag": True
        })
    dim_warehouse = pd.DataFrame(wh_rows)

    # 4. DimSupplier
    tier_choices = ["Tier 1 Strategic", "Tier 2 Preferred", "Tier 3 Tactical"]
    tier_probs = [0.20, 0.40, 0.40]
    supplier_rows = []
    for i in range(config.num_suppliers):
        tier = rng.choice(tier_choices, p=tier_probs)
        if tier == "Tier 1 Strategic":
            lead_time = int(rng.integers(7, 15))
            tol = 2
            terms = 45
            risk = round(float(rng.uniform(85.0, 98.0)), 2)
        elif tier == "Tier 2 Preferred":
            lead_time = int(rng.integers(14, 25))
            tol = 3
            terms = 30
            risk = round(float(rng.uniform(75.0, 88.0)), 2)
        else:
            lead_time = int(rng.integers(25, 55))
            tol = 5
            terms = 30
            risk = round(float(rng.uniform(60.0, 78.0)), 2)
            
        supplier_rows.append({
            "SupplierKey": i + 1,
            "SupplierCode": f"SUP-{i+1:04d}",
            "SupplierName": f"Global Vendor {i+1:04d} Co.",
            "Country": rng.choice(["United States", "Germany", "Mexico", "China", "Vietnam", "Canada", "Netherlands"]),
            "City": f"City-{i+1:03d}",
            "RegionZone": "Domestic" if i % 2 == 0 else "Overseas Inbound",
            "SupplierTier": tier,
            "ContractLeadTimeDays": lead_time,
            "LeadTimeToleranceDays": tol,
            "PaymentTermsDays": terms,
            "MinimumOrderQuantity": int(rng.choice([250, 500, 1000, 2000])),
            "PreferredStatusFlag": tier in ["Tier 1 Strategic", "Tier 2 Preferred"],
            "VendorRiskScore": risk
        })
    dim_supplier = pd.DataFrame(supplier_rows)

    # 5. DimProduct (with SCD Type 2 design)
    product_rows = []
    prod_key_seq = 1
    handling_profiles = ["Standard Dry", "Refrigerated", "Frozen", "Hazardous", "Bulk Fragile"]
    
    # Generate flat category list
    flat_subcats = []
    for dept, cat, subcats in CATEGORIES:
        for sc in subcats:
            flat_subcats.append((dept, cat, sc))
            
    for i in range(config.num_skus):
        sku_str = f"SKU-{i+1:05d}"
        dept, cat, subcat = flat_subcats[i % len(flat_subcats)]
        brand = BRANDS[i % len(BRANDS)]
        supp_key = int(rng.integers(1, config.num_suppliers + 1))
        
        # Base pricing
        base_cost = round(float(rng.uniform(0.80, 45.00)), 2)
        margin = float(rng.uniform(1.35, 2.20))
        list_price = round(base_cost * margin, 2)
        
        # ABC & XYZ classification assignment
        # First 20% -> A, next 30% -> B, remaining 50% -> C
        p_pct = i / config.num_skus
        abc = "A" if p_pct < 0.20 else ("B" if p_pct < 0.50 else "C")
        xyz = rng.choice(["X", "Y", "Z"], p=[0.35, 0.45, 0.20])
        
        handling = "Refrigerated" if "Fresh" in dept else rng.choice(handling_profiles, p=[0.70, 0.10, 0.05, 0.05, 0.10])
        
        # SCD Type 2 modeling: 10% of SKUs have a historical version
        has_history = (i % 10 == 0)
        if has_history:
            # Historical Version 1
            hist_cost = round(base_cost * 0.90, 2)
            product_rows.append({
                "ProductKey": prod_key_seq,
                "ProductSKU": sku_str,
                "ProductName": f"{brand} {subcat} Item {i+1}",
                "BrandName": brand,
                "CategoryName": cat,
                "SubcategoryName": subcat,
                "DepartmentName": dept,
                "UnitStandardCost": hist_cost,
                "UnitListPrice": round(hist_cost * margin, 2),
                "HandlingProfile": handling,
                "StorageClass": "High Bay Fast" if abc == "A" else "Standard Rack",
                "WeightKg": round(float(rng.uniform(0.1, 5.0)), 3),
                "VolumeCubicMeters": round(float(rng.uniform(0.0005, 0.02)), 4),
                "PrimarySupplierKey": supp_key,
                "ABCClassification": abc,
                "XYZClassification": xyz,
                "EffectiveFrom": date(2023, 1, 1),
                "EffectiveTo": date(2024, 7, 1),
                "IsCurrent": False
            })
            prod_key_seq += 1
            
            # Current Version 2
            product_rows.append({
                "ProductKey": prod_key_seq,
                "ProductSKU": sku_str,
                "ProductName": f"{brand} {subcat} Item {i+1}",
                "BrandName": brand,
                "CategoryName": cat,
                "SubcategoryName": subcat,
                "DepartmentName": dept,
                "UnitStandardCost": base_cost,
                "UnitListPrice": list_price,
                "HandlingProfile": handling,
                "StorageClass": "High Bay Fast" if abc == "A" else "Standard Rack",
                "WeightKg": round(float(rng.uniform(0.1, 5.0)), 3),
                "VolumeCubicMeters": round(float(rng.uniform(0.0005, 0.02)), 4),
                "PrimarySupplierKey": supp_key,
                "ABCClassification": abc,
                "XYZClassification": xyz,
                "EffectiveFrom": date(2024, 7, 1),
                "EffectiveTo": date(9999, 12, 31),
                "IsCurrent": True
            })
            prod_key_seq += 1
        else:
            # Single Current Version
            product_rows.append({
                "ProductKey": prod_key_seq,
                "ProductSKU": sku_str,
                "ProductName": f"{brand} {subcat} Item {i+1}",
                "BrandName": brand,
                "CategoryName": cat,
                "SubcategoryName": subcat,
                "DepartmentName": dept,
                "UnitStandardCost": base_cost,
                "UnitListPrice": list_price,
                "HandlingProfile": handling,
                "StorageClass": "High Bay Fast" if abc == "A" else "Standard Rack",
                "WeightKg": round(float(rng.uniform(0.1, 5.0)), 3),
                "VolumeCubicMeters": round(float(rng.uniform(0.0005, 0.02)), 4),
                "PrimarySupplierKey": supp_key,
                "ABCClassification": abc,
                "XYZClassification": xyz,
                "EffectiveFrom": date(2023, 1, 1),
                "EffectiveTo": date(9999, 12, 31),
                "IsCurrent": True
            })
            prod_key_seq += 1
            
    dim_product = pd.DataFrame(product_rows)

    # 6. DimCustomerChannel
    channels = ["Wholesale B2B", "Retail Chain Stores", "E-Commerce Direct"]
    channel_probs = [0.25, 0.50, 0.25]
    cust_rows = []
    for i in range(config.num_customers):
        ch = rng.choice(channels, p=channel_probs)
        if ch == "Wholesale B2B":
            seg = rng.choice(["Tier 1 National Distributor", "Regional Wholesaler"])
            prio = "P1 Critical"
            terms = 45
        elif ch == "Retail Chain Stores":
            seg = rng.choice(["National Hypermarket", "Regional Supermarket", "Convenience Retailer"])
            prio = "P2 Standard"
            terms = 30
        else:
            seg = "Direct Consumer Account"
            prio = "P3 Economy"
            terms = 0
            
        cust_rows.append({
            "CustomerChannelKey": i + 1,
            "CustomerChannelCode": f"CUST-{i+1:05d}",
            "ChannelName": ch,
            "CustomerAccountName": f"Commercial Partner {i+1:04d}" if ch != "E-Commerce Direct" else f"Direct Consumer {i+1:05d}",
            "CustomerSegment": seg,
            "CreditTermsDays": terms,
            "DeliveryPriorityTier": prio
        })
    dim_customer = pd.DataFrame(cust_rows)

    # 7. DimEmployeePlanner
    roles = ["VP Operations", "Regional Supply Planner", "Warehouse Planner", "Procurement Manager", "Supply Chain Analyst"]
    planner_rows = []
    for i in range(config.num_planners):
        r_key = (i % num_regions) + 1
        role = roles[i % len(roles)]
        planner_rows.append({
            "PlannerKey": i + 1,
            "EmployeeNumber": f"EMP-{5000+i+1:04d}",
            "PlannerName": f"Planner {chr(65 + i%26)}.{i+1:02d}",
            "EmailAddress": f"planner.{i+1:02d}@retailhub.com",
            "JobRole": role,
            "Department": "Operations Planning" if "Planner" in role else "Strategic Sourcing",
            "AssignedRegionKey": r_key,
            "AssignedCategoryGroup": flat_subcats[i % len(flat_subcats)][1]
        })
    dim_planner = pd.DataFrame(planner_rows)

    # 8. DimScenario
    scenarios = [
        ("SCN-BASE", "Baseline Plan", "Standard commercial baseline operating model", 1.00, 0, 95.00, 22.00),
        ("SCN-SURGE10", "Demand Surge +10%", "Macro consumer spending surge across all categories", 1.10, 0, 95.00, 22.00),
        ("SCN-PORT7D", "Port Disruption +7d", "Ocean freight and port customs delay shock", 1.00, 7, 95.00, 24.00),
        ("SCN-SLA98", "High Service Target 98%", "Executive SLA elevation to 98% on Class A SKUs", 1.00, 0, 98.00, 22.00),
        ("SCN-INFLATION25", "High Carrying Cost 25%", "Elevated benchmark interest rates increasing capital costs", 1.00, 0, 95.00, 25.00),
    ]
    scenario_rows = []
    for i, s in enumerate(scenarios):
        scenario_rows.append({
            "ScenarioKey": i + 1,
            "ScenarioCode": s[0],
            "ScenarioName": s[1],
            "Description": s[2],
            "DemandMultiplier": s[3],
            "LeadTimeShockDays": s[4],
            "ServiceLevelTargetPct": s[5],
            "AnnualCarryingCostRatePct": s[6],
        })
    dim_scenario = pd.DataFrame(scenario_rows)

    # 9. BridgeProductSupplier (Approved sourcing authorizations)
    curr_prods = dim_product[dim_product["IsCurrent"]].copy()
    bridge_rows = []
    for _, row in curr_prods.iterrows():
        sku = row["ProductSKU"]
        p_supp = row["PrimarySupplierKey"]
        # Primary mapping (70% share)
        bridge_rows.append({
            "ProductSKU": sku,
            "SupplierKey": p_supp,
            "IsPrimarySupplier": True,
            "ContractAllocationSharePct": 70.0,
            "ContractUnitCost": row["UnitStandardCost"]
        })
        # Secondary backup supplier (30% share) for 40% of SKUs
        if int(sku.split("-")[1]) % 3 == 0:
            sec_supp = (p_supp % config.num_suppliers) + 1
            bridge_rows.append({
                "ProductSKU": sku,
                "SupplierKey": sec_supp,
                "IsPrimarySupplier": False,
                "ContractAllocationSharePct": 30.0,
                "ContractUnitCost": round(row["UnitStandardCost"] * 1.05, 2)
            })
    bridge_product_supplier = pd.DataFrame(bridge_rows)

    return {
        "DimDate": dim_date,
        "DimRegion": dim_region,
        "DimWarehouse": dim_warehouse,
        "DimSupplier": dim_supplier,
        "DimProduct": dim_product,
        "DimCustomerChannel": dim_customer,
        "DimEmployeePlanner": dim_planner,
        "DimScenario": dim_scenario,
        "BridgeProductSupplier": bridge_product_supplier,
    }
