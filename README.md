# Medical Telegram Data Warehouse

An end-to-end data engineering pipeline that extracts medical, pharmaceutical, and cosmetic data from Telegram channels, loads it into a PostgreSQL data lake, and transforms it into a production-ready Star Schema using dbt.

## Architecture & Data Model

### 1. Ingestion Layer (Data Lake)
* **Source:** Telegram channels parsed from JSON partition chunks via Telethon/Pandas.
* **Target:** `raw.telegram_messages` (PostgreSQL table).

### 2. Transformation Layer (dbt Analytics Warehouse)
* **Staging:** `analytics.stg_telegram_messages` (Cleaned, typed, and deduplicated view).
* **Marts (Star Schema Tables):**
  * `dim_channels`: Unique surrogate keys (`MD5`), sector categorization (Pharmaceutical/Cosmetics/Medical), and channel aggregations.
  * `dim_dates`: Time-intelligence attributes for time-series parsing (weekend flags, ISO days, months, quarters).
  * `fct_messages`: Central metrics containing message contents, views, forwards, lengths, and foreign key mappings.

---

## Getting Started

### Prerequisites
* Docker & Docker Compose
* Python 3.11+
* dbt-core with `dbt-postgres` adapter

### Setup & Execution

1. **Spin up the PostgreSQL database container:**
   ```bash
   docker compose up -d

```

2. **Ingest raw data into the Data Lake:**
```bash
python src/load_raw_data.py

```


3. **Run dbt transformations to build the Star Schema:**
```bash
cd medical_warehouse
dbt run --profiles-dir .

```



---

##  Security Note

Local `.session` token authentication mappings, raw `.env` credential configurations, and dbt target logs are explicitly untracked via `.gitignore` to maintain secure pipeline integrity.

```

```
