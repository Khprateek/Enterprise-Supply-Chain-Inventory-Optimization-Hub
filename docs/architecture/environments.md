# Environment Strategy: Enterprise Supply Chain & Inventory Optimization Hub

## 1. Objectives & Principles
To maintain enterprise analytics engineering discipline without introducing unnecessary cloud costs or infrastructure complexity, this platform employs a three-tier environment strategy:
- **Pragmatic & Accessible:** Engineered specifically for high-fidelity portfolio demonstrations on local workstations and Google Cloud free-tier/sandbox resources.
- **Environment Parity:** All environments share the exact same Kimball dimensional schemas, SQL transformation logic, dbt test definitions, and Power BI semantic models.
- **Cost & Quota Protection:** Heavy data generation, edge-case unit testing, and schema iterations occur in local development before pushing full-scale data to the cloud.

---

## 2. Environment Comparison Matrix

| Environment Attribute | Development (`dev`) | Testing / Staging (`test`) | Production (`prod`) |
| :--- | :--- | :--- | :--- |
| **Primary Purpose** | Code authoring, rapid prototyping, schema testing, algorithm tuning. | Automated data quality assertion, regression testing, CI/CD validation. | Full enterprise scale reporting, executive dashboards, final portfolio demo. |
| **Execution Host** | Local Workstation (Windows 11 / VS Code). | Local / GitHub Actions automated test runner. | Google Cloud Platform (BigQuery) & Power BI Desktop. |
| **Storage Backend** | Local Files (`data/sample/`, `data/staging/`) or BigQuery dataset `sc_dev`. | Local temporary test database or BigQuery dataset `sc_test`. | BigQuery dataset `supply_chain_analytics` (or `sc_prod`). |
| **Target Fact Volume** | 50,000 ? 100,000 sample rows (preserving exact production grain). | 250,000 ? 500,000 rows (representative multi-category batch). | **5,000,000 ? 10,000,000+ rows** across core fact tables. |
| **dbt Target** | `dbt run --target dev` | `dbt test --target test` | `dbt run --target prod` |
| **Git Branch** | `feature/*` or `dev` branch. | `staging` / `test` / PR branch. | `master` / `main` branch. |
| **Power BI Target** | Development `.pbix` connected to sample or `sc_dev`. | Automated visual and measure validation checks. | Production `.pbix` connected to `supply_chain_analytics` (Import Mode). |
| **Cost Profile** | **$0.00** (100% Local / Free Tier). | **$0.00** (Automated transient test datasets). | Minimal cloud storage within BigQuery free tier (10 GB storage, 1 TB query/mo). |

---

## 3. Environment Architecture Details

### 3.1 Development Environment (`dev`)
- **Workflow:**
  1. Python generation scripts synthesize a lightweight, statistically representative sample dataset stored in `data/sample/`.
  2. dbt models are developed and compiled locally using `dbt compile` and `dbt run --target dev`.
  3. Schemas, joins, surrogate keys, and edge cases (e.g., zero sales, negative quantities) are iterated rapidly without network latency or cloud query wait times.
- **Benefits:** Instant feedback loops (< 5 seconds per test cycle), zero cloud spend, complete offline capability.

### 3.2 Testing Environment (`test`)
- **Workflow:**
  1. Triggered prior to merging changes or scaling up the dataset.
  2. Executes complete dbt schema testing suite:
     - `unique` and `not_null` assertions on all surrogate keys and primary keys.
     - `relationships` tests verifying referential integrity across all foreign keys.
     - Custom data assertions verifying inventory continuity ($$I_t = I_{t-1} + R - S$$) and King's safety stock formula bounds.
  3. Executes Python automated unit tests in `tests/` verifying data generation algorithms.
- **Benefits:** Guarantees zero schema breakage or orphan records before loading multi-million-row production tables.

### 3.3 Production Environment (`prod`)
- **Workflow:**
  1. Vectorized Python generator produces the full enterprise-scale dataset (5M?10M+ fact rows).
  2. Data is ingested into BigQuery dataset `supply_chain_analytics`.
  3. Tables are created with daily date partitioning and integer clustering.
  4. dbt executes full production transformations and materializes `FactSupplierMonthlyPerformance`.
  5. Power BI Desktop connects to BigQuery in Import Mode, loads the compressed star schema into VertiPaq memory, and refreshes the executive dashboards.
- **Security & Access:** Secured via dedicated GCP Service Account with `BigQuery Data Viewer` and `BigQuery Job User` permissions; credentials excluded from version control via `.gitignore`.

---

## 4. Configuration & dbt Profile Setup

Environment switching is managed declaratively via `dbt/profiles.yml` utilizing environment variables:

```yaml
supply_chain_hub:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: "{{ env_var('GCP_PROJECT_ID', 'local-portfolio-project') }}"
      dataset: sc_dev
      threads: 4
      keyfile: "{{ env_var('GCP_KEYFILE_PATH', 'credentials/sa_dev.json') }}"

    test:
      type: bigquery
      method: service-account
      project: "{{ env_var('GCP_PROJECT_ID', 'local-portfolio-project') }}"
      dataset: sc_test
      threads: 4
      keyfile: "{{ env_var('GCP_KEYFILE_PATH', 'credentials/sa_test.json') }}"

    prod:
      type: bigquery
      method: service-account
      project: "{{ env_var('GCP_PROJECT_ID', 'local-portfolio-project') }}"
      dataset: supply_chain_analytics
      threads: 8
      keyfile: "{{ env_var('GCP_KEYFILE_PATH', 'credentials/sa_prod.json') }}"
```
