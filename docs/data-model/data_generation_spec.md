# Synthetic Data Generation Specification: Supply Chain & Inventory Optimization Hub

## 1. Objectives & Principles
This specification defines the mathematical and behavioral models for synthesizing realistic enterprise supply-chain data. Rather than generating independent random numbers, every generated record reflects causal dependencies across commercial demand, inventory state transitions, supplier reliability, and operational logistics.

---

## 2. Statistical Distributions & Behavioral Rules

### 2.1 Product Popularity & SKU Segmentation (Pareto Principle)
- **Revenue Contribution (ABC Classification):**
  - **Class A SKUs:** Top **20%** of active catalog generates **75%** of gross sales demand. Modeled via a Pareto/Power-law distribution:
    $$D_i \propto i^{-\alpha}, \quad \alpha \approx 0.85$$
  - **Class B SKUs:** Next **30%** of catalog generates **20%** of demand.
  - **Class C SKUs:** Bottom **50%** of catalog (the long tail) generates **5%** of demand.
- **Demand Volatility (XYZ Classification):**
  - **Class X (Steady):** Coefficient of Variation $$CV < 0.25$$. Highly predictable, low variance.
  - **Class Y (Moderate):** $$0.25 \le CV < 0.75$$. Seasonal or promotion-sensitive.
  - **Class Z (Erratic / Lumpy):** $$CV \ge 0.75$$. Low frequency, high variance Poisson/intermittent demand.

### 2.2 Seasonality & Calendar Dynamics
Demand on day $$t$$ incorporates multiplicative annual and weekly cyclicality:
$$\text{DemandMultiplier}(t) = S_{\text{annual}}(t) \times S_{\text{weekly}}(t) \times S_{\text{promo}}(t)$$
- **Annual Seasonal Wave ($$S_{\text{annual}}$$):**
  - Q4 Holiday Peak (October ? December): Lift factor of $$1.25 \times$$ to $$1.45 \times$$.
  - Summer Seasonality (June ? August): Beverage/packaged goods lift of $$1.15 \times$$.
  - Post-Holiday Trough (January ? February): Drop factor of $$0.80 \times$$.
- **Day-of-Week Seasonality ($$S_{\text{weekly}}$$):**
  - Retail/Wholesale orders: Heavy ordering on Monday?Wednesday ($$1.20 \times$$) for weekend retail shelf restocking.
  - Weekend orders: Reduced B2B volume ($$0.60 \times$$), balanced by increased E-Commerce consumer direct demand ($$1.30 \times$$).

### 2.3 Regional Demand Heterogeneity
Each operating region applies an economic and market weight:
- **North America East (`REG-NA-EAST`):** Weight $$1.30 \times$$ (Large metropolitan density).
- **North America Midwest (`REG-NA-MIDWEST`):** Weight $$1.10 \times$$ (Central logistics corridor).
- **North America West (`REG-NA-WEST`):** Weight $$1.25 \times$$ (High e-commerce penetration).
- **Europe Central (`REG-EU-CENTRAL`):** Weight $$1.00 \times$$ (Baseline European operations).
- **APAC Singapore (`REG-APAC-SG`):** Weight $$0.85 \times$$ (Growing regional hub).

### 2.4 Customer Demand Modeling
- **High-Velocity SKUs (Class A/B):** Modeled using a Negative Binomial distribution to capture natural demand clustering and variance overdispersion ($$\sigma^2 > \mu$$):
  $$\text{DailyDemand} \sim \text{NegBinomial}(r, p)$$
- **Slow-Moving / Lumpy SKUs (Class C):** Modeled using an intermittent Poisson / Croston process where probability of non-zero demand on day $$t$$ is $$p_{\text{active}} \in [0.10, 0.40]$$.

### 2.5 Supplier Delivery Performance & Lead Times
- **Contracted SLA Lead Times:**
  - Domestic Tier 1 Strategic: 7 to 14 days ($$\sigma = 1.2$$ days, OTIF target 95%).
  - Regional Tier 2 Preferred: 14 to 21 days ($$\sigma = 3.5$$ days, OTIF target 88%).
  - Overseas Tier 3 Tactical: 30 to 60 days ($$\sigma = 8.0$$ days, OTIF target 75%).
- **Actual Dock Receipt Lead Time ($$LT_{\text{actual}}$$):**
  Modeled via a shifted Log-Normal distribution parameterized by quoted lead time:
  $$LT_{\text{actual}} = \text{Round}\left( \exp(\mu + \sigma Z) \right), \quad Z \sim \mathcal{N}(0, 1)$$
  - Right-skewed tail accounts for port congestion and customs holds.
- **Inbound Quality Inspection Defect Rate:**
  $$0.5\% - 3.0\%$$ of delivered units fail inspection and are recorded as `RejectedQuantity`.

### 2.6 Stateful Inventory Balance Continuity
Inventory balances are mathematically linked across sequential calendar dates:
$$\text{OnHand}_t = \max\left(0, \text{OnHand}_{t-1} + \text{Receipts}_t + \text{TransfersIn}_t - \text{Shipments}_t - \text{TransfersOut}_t + \text{ReturnsRestocked}_t - \text{ScrapAdjustments}_t\right)$$
- **Replenishment Purchase Trigger:**
  $$\text{NetAvailable} = \text{OnHand}_t + \text{InTransitInbound}_t - \text{Reserved}_t$$
  $$\text{If } \text{NetAvailable} \le \text{ROP}, \quad \text{Trigger Purchase Order with } Q = \text{EOQ or Target Max}$$

### 2.7 Stockout Occurrence & Outage Consolidation
- A stockout is triggered whenever cumulative customer order demand on day $$t$$ exceeds available stock:
  $$\text{Unfulfilled Demand} = \text{OrderedQuantity}_t - \text{AvailableQuantity}_t$$
- Consecutive daily snapshots where `AvailableQuantity <= 0` are consolidated into a single record in `FactStockout`:
  - `StockoutDurationDays` = count of contiguous days without stock.
  - `EstimatedLostDemandUnits` = trailing 30-day average daily sales $$\times$$ duration.
  - `EstimatedLostRevenueAmount` = lost units $$\times$$ unit list price.

### 2.8 Demand Forecasting Imperfection & Bias
Forecasts are generated to reflect realistic enterprise planning models with statistical error and cognitive bias:
$$\text{ForecastQuantity}_{i, t} = \max\left(1, \text{Round}\left( \text{TrueDemand}_{i, t} \times (1 + \text{Bias}_c) + \epsilon_{i, t} \right)\right)$$
- **Bias Factor ($$\text{Bias}_c$$):**
  - Fast-moving promotional categories: Positive commercial bias ($$+5\% \text{ to } +15\%$$ over-forecasting).
  - Volatile Z-class items: Negative bias ($$-10\% \text{ to } -20\%$$ under-forecasting).
- **Error Distribution ($$\epsilon$$):** Gaussian noise scaled by SKU coefficient of variation ($$\sigma_{\epsilon} = CV \times \text{TrueDemand}$$).

### 2.9 Customer Returns Reverse Logistics
- **Return Lag:** Customer returns occur 3 to 21 days after initial shipment (Log-Normal distribution).
- **Channel Return Propensity:**
  - Wholesale B2B: $$1.5\% - 2.5\%$$.
  - Retail Stores: $$3.0\% - 5.0\%$$.
  - E-Commerce Direct: $$8.0\% - 14.0\%$$.
- **Disposition Allocation:**
  - Restocked to Saleable Stock: $$80\%$$.
  - Damaged / Scrapped: $$15\%$$.
  - Return to Vendor (RTV): $$5\%$$.
