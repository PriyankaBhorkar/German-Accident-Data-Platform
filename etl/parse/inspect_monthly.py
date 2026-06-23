file = "accidents_with_persons_per_month.csv"

with open(file, "r", encoding="utf-8") as f:

    for i in range(60):
        line = f.readline()
        print(f"{i}: {line}")