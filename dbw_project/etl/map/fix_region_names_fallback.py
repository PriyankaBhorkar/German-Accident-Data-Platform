"""
fix_region_names_fallback.py
============================
Names the remaining `Unknown region%` regions that are FINER than the official
Gemeindeverzeichnis (mostly Hamburg/Berlin Ortsteile, e.g. 02001101, 11001234).
 
These 8-digit keys are city sub-districts that GV-ISys does not list as separate
municipalities, so they cannot match a municipality name directly. We resolve them
by rolling up to their official parent, in priority order:
    1. exact 8-digit municipality name   (already done by load_region_names.py)
    2. 5-digit district name              (LEFT(ags,5))
    3. 2-digit state name                 (LEFT(ags,2))   <- catches Hamburg/Berlin
 
NON-DESTRUCTIVE: only UPDATEs rows whose name still starts with 'Unknown region'.
Re-runnable. Does not touch accidents or the API.
 
Run:  python3 fix_region_names_fallback.py
"""
 
import openpyxl
import psycopg2
from datetime import datetime
 
DB_USER = "kshitijsmacbookpro"
GV_FILE = "31122023_Auszug_GV.xlsx"
GV_SHEET = "Onlineprodukt_Gemeinden31122023"
 
# --- build {ags: name} for states(10) and districts(40) from GV ---
wb = openpyxl.load_workbook(GV_FILE, read_only=True, data_only=True)
ws = wb[GV_SHEET]
 
district_name = {}   # 5-digit -> name
state_name = {}      # 2-digit -> name
 
for row in ws.iter_rows(min_row=7, values_only=True):
    sa = "" if row[0] is None else str(row[0]).strip()
    if sa not in ("10", "40"):
        continue
    land  = "" if row[2] is None else str(row[2]).strip()
    rb    = "" if row[3] is None else str(row[3]).strip()
    kreis = "" if row[4] is None else str(row[4]).strip()
    name  = None if row[7] is None else str(row[7]).strip()
    if not name:
        continue
    if sa == "10":
        state_name[land] = name
    else:
        district_name[land + rb + kreis] = name
 
print(f"Loaded {len(district_name)} district names, {len(state_name)} state names.")
 
# --- connect ---
conn = psycopg2.connect(host="localhost", database="dbw_project",
                        user=DB_USER, port="5432")
cur = conn.cursor()
 
cur.execute("SELECT ags FROM regions WHERE name LIKE 'Unknown region%'")
todo = [r[0] for r in cur.fetchall()]
 
by_district = by_state = still_unknown = 0
for ags in todo:
    d = ags[:5]
    s = ags[:2]
    if d in district_name:
        cur.execute("UPDATE regions SET name = %s WHERE ags = %s",
                    (f"{district_name[d]} (Teilgebiet)", ags))
        by_district += 1
    elif s in state_name:
        cur.execute("UPDATE regions SET name = %s WHERE ags = %s",
                    (f"{state_name[s]} (Teilgebiet)", ags))
        by_state += 1
    else:
        still_unknown += 1
 
# log a data-quality check describing what we did
cur.execute("""
    INSERT INTO data_quality_checks (run_id, table_name, issue_type, issue_count, description)
    VALUES (NULL, %s, %s, %s, %s)
""", (
    "regions",
    "subdistrict_keys_named_by_parent",
    by_district + by_state,
    "Sub-municipal accident keys (e.g. Hamburg/Berlin Ortsteile) named via their "
    "official GV-ISys parent district/state, as GV does not list them individually.",
))
 
conn.commit()
cur.close()
conn.close()
 
print(f"Named via district: {by_district}")
print(f"Named via state:    {by_state}")
print(f"Still unknown:      {still_unknown}")
 