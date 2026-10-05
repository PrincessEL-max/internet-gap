import pandas as pd

df = pd.read_csv("data/bps.csv", sep=None, engine="python", encoding="utf-8-sig")
print(df.head())
print(df.dtypes)
print(len(df), "baris")
df.to_csv("data/bps_clean.csv", index=False, encoding="utf-8")