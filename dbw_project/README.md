# German Road Accident Data Platform

Integrated accident and regional-statistics API built for the *Datenbanken und
Web-Techniken* project task ("Open Data Integration with Accidents in
Germany").

The platform combines:

- **Unfallatlas** accident event data (CSV)
- **Regional indicator data** (e.g. accidents per 10,000 inhabitants)
- **AGS / GV-ISys** regional reference keys for harmonised joins

...into one PostgreSQL database, exposed through a documented FastAPI service,
with a Streamlit demo client for live querying.

---

## 1. Architecture

```
Examiner / Browser
        │
        ▼
 Streamlit demo (app.py)
        │   HTTP (requests)
        ▼
 FastAPI backend (main.py + database.py)
        │   SQL (SQLAlchemy)
        ▼
 PostgreSQL database
        ▲
        │  ETL (extract → parse → map → load → aggregate)
 External sources (Unfallatlas, Regionalatlas, GENESIS, AGS)
```

The frontend never talks to the database directly — it only calls the FastAPI
endpoints, which is what `app.py`'s `api_get()` helper does against
`BASE_URL = "http://127.0.0.1:8000"`.

---

## 2. Prerequisites

- Python 3.11+
- PostgreSQL 14+ (running locally or reachable over the network)
- `pip`

---

## 3. Setup

### 3.1 Clone and create a virtual environment

```bash
git clone <your-repo-url>
cd <your-repo-folder>

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 3.2 Install dependencies

```bash
pip install -r requirements.txt
```

### 3.3 Configure the database connection

Copy the example environment file and fill in your local Postgres
credentials:

```bash
cp .env.example .env
```

`database.py` reads these variables via `os.getenv(...)` and falls back to
sensible local defaults if unset:

| Variable       | Default              | Purpose                          |
|-----------------|----------------------|-----------------------------------|
| `DB_USER`       | `kshitijsmacbookpro` | Postgres role                    |
| `DB_PASSWORD`   | *(empty)*            | Postgres password                |
| `DB_HOST`       | `localhost`          | Postgres host                    |
| `DB_PORT`       | `5432`                | Postgres port                    |
| `DB_NAME`       | `dbw_project`         | Database name                    |
| `DATABASE_URL`  | *(unset)*             | Overrides all of the above if set |

### 3.4 Create the database and schema

```bash
createdb dbw_project          # if it doesn't exist yet
psql -d dbw_project -f db/schema.sql
```

### 3.5 Run the ETL import

This populates `sources`, `regions`, `accidents`, `indicators`, and
`indicator_values`, and records each run in `import_runs`:

```bash
python etl/run_etl.py
```

> Re-running the ETL script should be idempotent — it is designed to refresh
> the database from the official sources without duplicating records or
> re-querying external services unnecessarily. See `docs/data_sources.md`
> for provenance and licence details per source.

---

## 4. Running the application

### 4.1 Start the API

```bash
uvicorn main:app --reload --port 8000
```

- API root: http://127.0.0.1:8000/
- Interactive docs (Swagger UI): **http://127.0.0.1:8000/docs**
- OpenAPI schema (JSON): http://127.0.0.1:8000/openapi.json

### 4.2 Start the demo client

In a second terminal (with the same virtual environment activated):

```bash
streamlit run app.py
```

This opens the dashboard at http://localhost:8501, with pages for:

- **Overview** — API status, registered sources, import history
- **Regional accident rates** — accidents per 10,000 inhabitants by region
- **Accident explorer** — filter by year, state, severity, participant type
- **Fatal accident districts** — cross-source ranking by fatal accident count
- **Bicycle risk districts** — cross-source bicycle accident share ranking

---

## 5. Example API calls (mandatory test questions)

```bash
# Earliest accident year in the complete dataset
curl "http://127.0.0.1:8000/statistics/earliest-year"

# Accidents involving personal injury in Saxony (14) in 2023
curl "http://127.0.0.1:8000/accidents/filter-by-category?year=2023&state_code=14"

# Earliest year with data for North Rhine-Westphalia (05)
curl "http://127.0.0.1:8000/statistics/state-earliest/05"

# Earliest year with data for Mecklenburg-Vorpommern (13)
curl "http://127.0.0.1:8000/statistics/state-earliest/13"

# Pedestrian accidents in Berlin (11) in 2023
curl "http://127.0.0.1:8000/accidents/filter-by-category?year=2023&state_code=11&participant=pedestrian"

# Cross-source: top 5 districts by fatal accidents in 2024, with official rate
curl "http://127.0.0.1:8000/statistics/integrated/fatal-districts/2024?limit=5"

# Cross-source: districts with highest bicycle accident share in 2024
curl "http://127.0.0.1:8000/statistics/integrated/bicycle-risk-districts/2024"
```

Full parameter and response documentation is available live at `/docs`, and
exported as static JSON in `docs/api/openapi.json`.

---

## 6. Project structure

```
.
├── main.py              # FastAPI app: routes, response models, custom Swagger UI
├── database.py          # SQLAlchemy engine/session, reads DB_* env vars
├── app.py                # Streamlit demo client
├── etl/                  # extract / parse / map / load / aggregate scripts
├── db/
│   └── schema.sql        # canonical schema: regions, accidents, indicators, indicator_values, sources, import_runs
├── docs/
│   ├── api/openapi.json   # exported API documentation
│   └── data_sources.md    # provenance, retrieval dates, licences
├── requirements.txt
├── .env.example
└── README.md
```

---

## 7. Data sources and licensing

All integrated datasets are published under
**Datenlizenz Deutschland – Namensnennung – Version 2.0 (DL-DE-BY-2.0)**.
This licence metadata is returned alongside every relevant API response
(see the `metadata` field) and is also queryable directly:

```bash
curl "http://127.0.0.1:8000/metadata/sources"
```

See `docs/data_sources.md` for the full list of sources, access URLs, and
retrieval dates.

---

## 8. Known limitations

- Raw downloaded source files are **not** committed to this repository
  (see `.gitignore`); run the ETL scripts to reproduce them locally.
- *(Add any project-specific caveats here — e.g. years not covered by a
  given state, sampling limitations, or districts excluded due to
  missing population data.)*
