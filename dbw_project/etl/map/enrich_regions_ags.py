import psycopg2

DB_USER = "kshitijsmacbookpro"
FILE = "GV100AD_31052026.txt"

conn = psycopg2.connect(
    host="localhost",
    database="dbw_project",
    user=DB_USER,
    port="5432"
)

cur = conn.cursor()

updated = 0

with open(FILE, "r", encoding="utf-8") as f:
    for line in f:

        # type 6 = municipality row
        if not line.startswith("6"):
            continue

        ags = line[10:18]
        name = line[22:84].strip()

        cur.execute("""
            UPDATE regions
            SET name = %s,
                level = 'municipality'
            WHERE ags = %s
        """, (name, ags))

        updated += cur.rowcount

conn.commit()
cur.close()
conn.close()

print(f"Updated {updated} region names safely.")