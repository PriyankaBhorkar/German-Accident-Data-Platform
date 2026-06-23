"""
load_region_names.py
=====================
Third integrated source: official region names + population from the
Destatis Gemeindeverzeichnis (GV-ISys) annual extract.
 
This file is NON-DESTRUCTIVE. It only:
  - INSERTs one new `sources` row (reused on re-run, no duplicates)
  - opens/closes one `import_runs` row + logs one `data_quality_checks` row
  - UPDATEs name/level on regions that ALREADY exist (matched by ags)
  - (optional) adds a POPULATION_TOTAL indicator + values
  - (optional) fills parent_region_id to make the region hierarchy real
 
It never drops tables, never touches `accidents`, never re-runs accident ETL.
 
Requirements:  pip install openpyxl psycopg2-binary
Run:           python3 load_region_names.py
"""
 
import openpyxl
import psycopg2
from datetime import datetime
 
# =========================
# CONFIG
# =========================
 
DB_USER = "kshitijsmacbookpro"          # same as your other scripts
GV_FILE = "31122023_Auszug_GV.xlsx"     # put this file next to the script
GV_SHEET = "Onlineprodukt_Gemeinden31122023"
 
INCLUDE_POPULATION = True   # bonus: load municipality population as an indicator
SET_PARENTS = True          # bonus: fill parent_region_id (municipality->district->state)
 
GV_SOURCE_NAME = "Gemeindeverzeichnis GV-ISys (annual extract 31.12.2023)"
 
# =========================
# 1. PARSE THE GV EXCEL FILE
# =========================
# Layout (verified): data starts at row 7.
#   col 0  Satzart   -> 10 = state, 40 = district (Kreis), 60 = municipality
#   cols 2..6        -> Land(2), RB(1), Kreis(2), VB(4), Gem(3)
#   col 7  name      -> official region name
#   col 9  population (only present on Satzart 60 municipality rows)
# AGS = Land + RB + Kreis [+ Gem]; the VB block is NOT part of the 8-digit AGS.
 
print(f"Reading {GV_FILE} ...")
wb = openpyxl.load_workbook(GV_FILE, read_only=True, data_only=True)
ws = wb[GV_SHEET]
 
# ags -> (name, level)
gv_names = {}
# ags -> population (municipality level only)
gv_population = {}
 
for row in ws.iter_rows(min_row=7, values_only=True):
    satzart = "" if row[0] is None else str(row[0]).strip()
    if satzart not in ("10", "40", "60"):
        continue  # skip blank/footnote rows safely
 
    land  = "" if row[2] is None else str(row[2]).strip()
    rb    = "" if row[3] is None else str(row[3]).strip()
    kreis = "" if row[4] is None else str(row[4]).strip()
    gem   = "" if row[6] is None else str(row[6]).strip()
    name  = None if row[7] is None else str(row[7]).strip()
 
    if satzart == "10":
        ags, level = land, "state"
    elif satzart == "40":
        ags, level = land + rb + kreis, "district"
    else:  # 60
        ags, level = land + rb + kreis + gem, "municipality"
 
    if not name:
        continue
    gv_names[ags] = (name, level)
 
    if satzart == "60" and row[9] is not None:
        try:
            gv_population[ags] = int(row[9])
        except (TypeError, ValueError):
            pass
 
print(f"Parsed {len(gv_names)} official names "
      f"({len(gv_population)} municipality populations).")
 
# =========================
# 2. CONNECT TO DATABASE
# =========================
 
conn = psycopg2.connect(
    host="localhost",
    database="dbw_project",
    user=DB_USER,
    port="5432",
)
cur = conn.cursor()
 
# =========================
# 3. REGISTER THE SOURCE (idempotent)
# =========================
 
cur.execute("SELECT source_id FROM sources WHERE name = %s", (GV_SOURCE_NAME,))
existing = cur.fetchone()
if existing:
    source_id = existing[0]
else:
    cur.execute("""
        INSERT INTO sources (name, source_type, url, license, retrieval_date, description)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING source_id
    """, (
        GV_SOURCE_NAME,
        "XLSX",
        "https://www.destatis.de/DE/Themen/Laender-Regionen/Regionales/Gemeindeverzeichnis/",
        "dl-by-de/2.0",
        datetime.now().date(),
        "Official German municipality register (AGS, names, area, population)",
    ))
    source_id = cur.fetchone()[0]
 
# =========================
# 4. OPEN IMPORT RUN
# =========================
 
cur.execute("""
    INSERT INTO import_runs (source_id, started_at, status, notes)
    VALUES (%s, %s, %s, %s)
    RETURNING run_id
""", (source_id, datetime.now(), "RUNNING", "Updating region names from GV-ISys"))
run_id = cur.fetchone()[0]
 
# =========================
# 5. UPDATE REGION NAMES (existing rows only)
# =========================
 
cur.execute("SELECT ags FROM regions")
db_ags = [r[0] for r in cur.fetchall()]
 
updated = 0
unmatched = []
for ags in db_ags:
    if ags in gv_names:
        name, level = gv_names[ags]
        cur.execute(
            "UPDATE regions SET name = %s, level = %s WHERE ags = %s",
            (name, level, ags),
        )
        updated += 1
    else:
        unmatched.append(ags)
 
print(f"Region names updated: {updated}   not matched: {len(unmatched)}")
 
# =========================
# 6. (OPTIONAL) POPULATION INDICATOR
# =========================
 
if INCLUDE_POPULATION:
    cur.execute("""
        INSERT INTO indicators (code, name, unit, source_id)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (code) DO NOTHING
    """, ("POPULATION_TOTAL", "Total population", "inhabitants", source_id))
 
    cur.execute("SELECT indicator_id FROM indicators WHERE code = 'POPULATION_TOTAL'")
    pop_indicator_id = cur.fetchone()[0]
 
    # clear only this indicator's values so re-runs stay clean
    cur.execute("DELETE FROM indicator_values WHERE indicator_id = %s", (pop_indicator_id,))
 
    pop_loaded = 0
    for ags in db_ags:
        if ags in gv_population:
            cur.execute("SELECT region_id FROM regions WHERE ags = %s", (ags,))
            region_id = cur.fetchone()[0]
            cur.execute("""
                INSERT INTO indicator_values (indicator_id, region_id, year, value)
                VALUES (%s, %s, %s, %s)
            """, (pop_indicator_id, region_id, 2023, gv_population[ags]))
            pop_loaded += 1
    print(f"Population values loaded: {pop_loaded}")
 
# =========================
# 7. (OPTIONAL) PARENT HIERARCHY
# =========================
# municipality(8) -> parent district(5) ; district(5) -> parent state(2)
 
if SET_PARENTS:
    cur.execute("""
        UPDATE regions child
        SET parent_region_id = parent.region_id
        FROM regions parent
        WHERE LENGTH(child.ags) = 8
          AND parent.ags = LEFT(child.ags, 5)
    """)
    cur.execute("""
        UPDATE regions child
        SET parent_region_id = parent.region_id
        FROM regions parent
        WHERE LENGTH(child.ags) = 5
          AND parent.ags = LEFT(child.ags, 2)
    """)
    print("parent_region_id filled for districts and municipalities.")
 
# =========================
# 8. CLOSE IMPORT RUN + QUALITY LOG
# =========================
 
cur.execute("""
    UPDATE import_runs
    SET finished_at = %s, records_imported = %s, status = %s
    WHERE run_id = %s
""", (datetime.now(), updated, "SUCCESS", run_id))
 
cur.execute("""
    INSERT INTO data_quality_checks (run_id, table_name, issue_type, issue_count, description)
    VALUES (%s, %s, %s, %s, %s)
""", (
    run_id,
    "regions",
    "regions_without_official_name",
    len(unmatched),
    "Region AGS keys present in accidents but absent from GV-ISys 2023 "
    "(e.g. boundary/merger changes between source years).",
))
 
conn.commit()
cur.close()
conn.close()
 
print(f"\nDone. Updated {updated} region names; {len(unmatched)} left unmatched "
      f"(logged as a data-quality check).")