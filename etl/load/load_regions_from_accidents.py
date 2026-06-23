import pandas as pd
import psycopg2
from datetime import datetime

DB_USER = "kshitijsmacbookpro"

FILES = [
    ("accident_per_location_2023.csv", 1),
    ("accident_per_location_2021_in_Schleswig-Holstein.csv", 2)
]

conn = psycopg2.connect(
    host="localhost",
    database="dbw_project",
    user=DB_USER,
    port="5432"
)

cur = conn.cursor()

total_regions = 0

for file_name, source_id in FILES:

    cur.execute("""
        INSERT INTO import_runs (source_id, started_at, status, notes)
        VALUES (%s, %s, %s, %s)
        RETURNING run_id
    """, (
        source_id,
        datetime.now(),
        "RUNNING",
        f"Importing regions from {file_name}"
    ))

    run_id = cur.fetchone()[0]

    df = pd.read_csv(file_name, sep=";", low_memory=False)

    # Build AGS-like region key:
    # state(2) + district(2) + municipality(3)
    df["state_code"] = df["ULAND"].astype(int).astype(str).str.zfill(2)
    df["district_code"] = df["UKREIS"].astype(int).astype(str).str.zfill(2)
    df["municipality_code"] = df["UGEMEINDE"].astype(int).astype(str).str.zfill(3)

    df["ags"] = df["state_code"] + df["district_code"] + df["municipality_code"]

    regions = df[["ags"]].drop_duplicates()

    records = 0

    for _, row in regions.iterrows():
        cur.execute("""
            INSERT INTO regions (ags, name, level)
            VALUES (%s, %s, %s)
            ON CONFLICT (ags) DO NOTHING
        """, (
            row["ags"],
            "Unknown region " + row["ags"],
            "municipality"
        ))

        records += 1

    cur.execute("""
        UPDATE import_runs
        SET finished_at = %s,
            records_imported = %s,
            status = %s
        WHERE run_id = %s
    """, (
        datetime.now(),
        records,
        "SUCCESS",
        run_id
    ))

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
        "regions",
        "distinct_regions_loaded",
        records,
        f"Distinct municipality keys extracted from {file_name}"
    ))

    total_regions += records

conn.commit()
cur.close()
conn.close()

print(f"Region ETL completed. Processed {total_regions} region keys.")