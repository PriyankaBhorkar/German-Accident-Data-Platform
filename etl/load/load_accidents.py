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

total_loaded = 0

def to_float(value):
    if pd.isna(value):
        return None
    return float(str(value).replace(",", "."))

for file_name, source_id in FILES:

    cur.execute("""
        INSERT INTO import_runs (source_id, started_at, status, notes)
        VALUES (%s, %s, %s, %s)
        RETURNING run_id
    """, (
        source_id,
        datetime.now(),
        "RUNNING",
        f"Importing accidents from {file_name}"
    ))

    run_id = cur.fetchone()[0]

    df = pd.read_csv(file_name, sep=";", low_memory=False)

    records = 0

    for _, row in df.iterrows():

        state_code = str(int(row["ULAND"])).zfill(2)
        district_code = str(int(row["UKREIS"])).zfill(2)
        municipality_code = str(int(row["UGEMEINDE"])).zfill(3)
        ags = state_code + district_code + municipality_code

        cur.execute("""
            SELECT region_id FROM regions
            WHERE ags = %s
        """, (ags,))

        result = cur.fetchone()
        region_id = result[0] if result else None

        road_condition = None
        if "IstStrassenzustand" in df.columns:
            road_condition = row["IstStrassenzustand"]
        elif "USTRZUSTAND" in df.columns:
            road_condition = row["USTRZUSTAND"]

        cur.execute("""
            INSERT INTO accidents (
                external_accident_id,
                region_id,
                source_id,
                year,
                month,
                hour,
                weekday,
                accident_category,
                accident_type,
                road_condition,
                light_condition,
                pedestrian_involved,
                bicycle_involved,
                motorcycle_involved,
                car_involved,
                goods_vehicle_involved,
                other_involved,
                longitude,
                latitude
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            str(row["UIDENTSTLAE"]),
            region_id,
            source_id,
            int(row["UJAHR"]),
            int(row["UMONAT"]),
            int(row["USTUNDE"]),
            int(row["UWOCHENTAG"]),
            int(row["UKATEGORIE"]),
            int(row["UART"]),
            int(road_condition) if not pd.isna(road_condition) else None,
            int(row["ULICHTVERH"]),
            bool(row["IstFuss"]),
            bool(row["IstRad"]),
            bool(row["IstKrad"]),
            bool(row["IstPKW"]),
            bool(row["IstGkfz"]),
            bool(row["IstSonstige"]),
            to_float(row["XGCSWGS84"]),
            to_float(row["YGCSWGS84"])
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
        "accidents",
        "rows_loaded",
        records,
        f"Accident rows loaded from {file_name}"
    ))

    total_loaded += records

conn.commit()
cur.close()
conn.close()

print(f"Loaded {total_loaded} accident records successfully.")