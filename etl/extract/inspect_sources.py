import pandas as pd

files = [
    "accident_per_location_2023.csv",
    "accident_per_location_2021_in_Schleswig-Holstein.csv",
    "accidents_with_persons_per_month.csv",
    "accident_per_10000_per_city.csv"
]

for file in files:

    print("\n==============================")
    print(f"FILE: {file}")
    print("==============================")

    df = pd.read_csv(file, sep=";", low_memory=False)

    print("\nFIRST 5 ROWS:")
    print(df.head())

    print("\nCOLUMNS:")
    print(df.columns)

    print("\nROW COUNT:")
    print(len(df))