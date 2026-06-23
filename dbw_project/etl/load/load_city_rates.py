import pandas as pd
import psycopg2
from datetime import datetime

DB_USER = "kshitijsmacbookpro"

# =========================
# CONNECT TO DATABASE
# =========================

conn = psycopg2.connect(
    host="localhost",
    database="dbw_project",
    user=DB_USER,
    port="5432"
)

cur = conn.cursor()

# =========================
# CREATE IMPORT RUN
# =========================

source_id = 4

cur.execute("""
    INSERT INTO import_runs (
        source_id,
        started_at,
        status,
        notes
    )
    VALUES (%s, %s, %s, %s)
    RETURNING run_id
""", (
    source_id,
    datetime.now(),
    "RUNNING",
    "Importing accident rates per city"
))

run_id = cur.fetchone()[0]

# =========================
# READ CSV
# =========================

df = pd.read_csv(
    "accident_per_10000_per_city.csv",
    sep=";",
    skiprows=3,
    names=["ags", "name", "value"],
    low_memory=False
)

# =========================
# CLEAN DATA
# =========================

df = df.dropna()

df["ags"] = (
    df["ags"]
    .astype(str)
    .str.strip()
    .str.zfill(5)
)

df["name"] = (
    df["name"]
    .astype(str)
    .str.strip()
)

df["value"] = (
    df["value"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .astype(float)
)

# =========================
# INSERT INDICATOR
# =========================

cur.execute("""
    INSERT INTO indicators (
        code,
        name,
        unit,
        source_id
    )
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (code) DO NOTHING
""", (
    "ACCIDENTS_PER_10000_INHABITANTS",
    "Road traffic accidents per 10,000 inhabitants",
    "accidents per 10,000 inhabitants",
    source_id
))

# =========================
# GET INDICATOR ID
# =========================

cur.execute("""
    SELECT indicator_id
    FROM indicators
    WHERE code = 'ACCIDENTS_PER_10000_INHABITANTS'
""")

indicator_id = cur.fetchone()[0]

# =========================
# LOAD REGIONS + VALUES
# =========================

records = 0

for _, row in df.iterrows():

    # INSERT REGION

    cur.execute("""
        INSERT INTO regions (
            ags,
            name,
            level
        )
        VALUES (%s, %s, %s)
        ON CONFLICT (ags)
        DO UPDATE SET
            name = EXCLUDED.name
        RETURNING region_id
    """, (
        row["ags"],
        row["name"],
        "city"
    ))

    region_id = cur.fetchone()[0]

    # INSERT INDICATOR VALUE

    cur.execute("""
        INSERT INTO indicator_values (
            indicator_id,
            region_id,
            year,
            value
        )
        VALUES (%s, %s, %s, %s)
    """, (
        indicator_id,
        region_id,
        2023,
        row["value"]
    ))

    records += 1

# =========================
# UPDATE IMPORT RUN
# =========================

cur.execute("""
    UPDATE import_runs
    SET
        finished_at = %s,
        records_imported = %s,
        status = %s
    WHERE run_id = %s
""", (
    datetime.now(),
    records,
    "SUCCESS",
    run_id
))

# =========================
# DATA QUALITY CHECK
# =========================

cur.execute("""
    INSERT INTO data_quality_checks (
        run_id,
        table_name,
        issue_type,
        issue_count,
        description
    )
    VALUES (%s, %s, %s, %s, %s)
""", (
    run_id,
    "indicator_values",
    "rows_loaded",
    records,
    "City accident rate rows loaded successfully"
))

# =========================
# COMMIT + CLOSE
# =========================

conn.commit()

cur.close()
conn.close()

print(f"Loaded {records} city accident rate records successfully.")