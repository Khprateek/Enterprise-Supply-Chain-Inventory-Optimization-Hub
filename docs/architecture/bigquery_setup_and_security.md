# BigQuery Analytical Warehouse Setup & Security Architecture

This document defines the exact cloud architecture, security boundaries, authentication methods, IAM roles, and billing requirements for Google BigQuery in the **Enterprise Supply Chain & Inventory Optimization Hub**.

---

## 1. Google Cloud Platform (GCP) Project & Datasets

### 1.1 GCP Project Configuration
* **Project Name:** Enterprise Supply Chain Analytics
* **Project ID:** supply-chain-analytics-hub (or enterprise designated ID)
* **Default Data Location:** US (multi-region) or us-central1

### 1.2 Physical Dataset Architecture
To enforce clean data governance, physical separation of ELT stages, and least-privilege access control, five isolated BigQuery datasets are provisioned:

| Dataset ID | Purpose / ELT Layer | Default Expiration | Access Scope |
| :--- | :--- | :--- | :--- |
| aw_supply_chain | Landing of raw source Parquet files | None | Restricted (Read-only for dbt) |
| stg_supply_chain | Cleansed staging views | None | Internal to ELT transformation |
| int_supply_chain | Reusable intermediate joined models | None | Internal to ELT transformation |
| nalytics_supply_chain | Conformed Kimball dimensional star schema (Marts) | None | Read-only for Power BI, Analysts, Planners |
| snapshots_supply_chain | Historical SCD Type 2 audit snapshots | None | Internal to ELT audit versioning |

---

## 2. Authentication & Identity Management

### 2.1 Service Account Provisioning
A dedicated automation service account is provisioned for dbt execution:
* **Service Account ID:** sa-dbt-pipeline@supply-chain-analytics-hub.iam.gserviceaccount.com
* **Display Name:** dbt Automation Service Account
* **Key Format:** JSON private key (credentials/sa_dbt.json)

### 2.2 Local Developer Authentication (Interactive)
For developers working locally with Google Cloud SDK installed:
`powershell
# Authenticate local machine via Google Cloud ADC
gcloud auth application-default login
gcloud config set project supply-chain-analytics-hub
`

---

## 3. Least-Privilege IAM Permission Design

Adhering strictly to the principle of least privilege, the dbt service account is **never** granted high-privilege roles like oles/owner, oles/editor, or project-wide oles/bigquery.admin.

### 3.1 Project-Level IAM Permissions
At the GCP project level, the service account is granted:
* **Role:** oles/bigquery.jobUser
  * Allows submitting BigQuery jobs (queries, table creation tasks) and consuming query slots.
  * Does **not** permit reading or modifying project datasets without explicit dataset-level grants.

### 3.2 Dataset-Level IAM Permissions
Permissions are scoped granularly per dataset:

| Target Dataset | Assigned IAM Role | Permissions Granted |
| :--- | :--- | :--- |
| aw_supply_chain | oles/bigquery.dataViewer | Read raw landed tables; **no** delete, alter, or insert permissions. |
| stg_supply_chain | oles/bigquery.dataEditor | Create, replace, and manage staging views. |
| int_supply_chain | oles/bigquery.dataEditor | Create, replace, and manage intermediate models. |
| nalytics_supply_chain | oles/bigquery.dataEditor | Materialize Kimball fact and dimension tables. |
| snapshots_supply_chain | oles/bigquery.dataEditor | Insert and update SCD Type 2 snapshot records. |

### 3.3 Downstream BI / Power BI Access
Power BI service accounts and reporting analysts are granted:
* Project level: oles/bigquery.jobUser
* Dataset level: oles/bigquery.dataViewer on nalytics_supply_chain **only**.
* Staging, raw, and intermediate layers remain completely invisible and inaccessible to reporting consumers.

---

## 4. Secret & Credential Handling Rules

1. **Zero Secrets in Git:**
   - The credentials/ directory is explicitly added to .gitignore.
   - Service account keys, JSON tokens, and API credentials are never committed.
2. **Environment Variable Injection:**
   - File paths and project IDs are injected at runtime via environment variables in profiles.yml:
     - GCP_PROJECT_ID
     - GCP_KEYFILE_PATH
3. **Key Rotation & Lifecycle:**
   - In production CI/CD pipelines (e.g., GitHub Actions), service account keys are managed via Google Cloud Workload Identity Federation (OIDC) to eliminate long-lived service account keys entirely.

---

## 5. Billing & Cost Disclosures

### 5.1 Google Cloud Free Tier Allowance
Google Cloud BigQuery offers a monthly free tier:
* **Storage:** 10 GB active storage per month (.00).
* **Queries:** 1 TB query data processed per month (.00).
* **Our Footprint:** The entire 9.55M-record synthetic dataset occupies ~205 MB in compressed Parquet, comfortably within the 10 GB free tier.

### 5.2 Paid Cloud Service Disclosures
* A valid Google Cloud Billing Account must be associated with the GCP Project to enable the BigQuery API.
* On-demand query pricing beyond 1 TB/month is billed at **.25 per TB**.
* To prevent unexpected query charges:
  - All fact tables are partitioned by day/month and clustered on frequently queried dimensional foreign keys.
  - Queries must include date filter predicates to prune partition scans.
  - Maximum query bytes billed limits can be enforced at the project or dbt profile level (maximum_bytes_billed: 1000000000 = 1 GB cap).
