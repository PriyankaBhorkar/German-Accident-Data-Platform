import pandas as pd

# =========================
# FILE NAME
# =========================

file = "GV100AD_31052026.txt"

# =========================
# RAW LINE INSPECTION
# =========================

print("\n================ RAW LINES ================\n")

with open(file, "r", encoding="utf-8") as f:
    for i in range(10):
        line = f.readline()
        print(repr(line))

# =========================
# FIXED WIDTH IMPORT
# =========================

print("\n================ DATAFRAME ================\n")

df = pd.read_fwf(file)

print(df.head())

print("\n================ COLUMNS ================\n")

print(df.columns)

print("\n================ SHAPE ================\n")

print(df.shape)