import csv
import ast
import pandas as pd
from tabulate import tabulate

rows = []

with open("quotes.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    headers = next(reader)
    for row in reader:
        for item in row:
            try:
                tup = ast.literal_eval(item)
                rows.append(
                    {"text": tup[0],
                     "author": tup[1],
                     "tags": ", ".join(tup[2])}
                )
            except Exception as e:
                print(f"Помилка при обробці: {item} → {e}")

df_clean = pd.DataFrame(rows)

print(tabulate(df_clean, headers="keys", tablefmt="psql"))

df_clean.to_csv("quotes_clean.csv", index=False)
