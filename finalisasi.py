import pandas as pd, numpy as np

m = pd.read_csv("data/kab_index.csv")
t = pd.read_csv("data/top20_mobile.csv")[["nama_geo", "muncul_di_7_skenario"]]

m = m.merge(t, on="nama_geo", how="left")
m["muncul_di_7_skenario"] = m.muncul_di_7_skenario.fillna(0).astype(int)

m["tier_kualitas"] = pd.cut(m.Q_mobile, [0, 0.25, 0.5, 1],
    labels=["Rendah", "Menengah-bawah", "Menengah-atas/baik"], include_lowest=True)
m["status_prioritas"] = np.select(
    [m.muncul_di_7_skenario == 7, m.muncul_di_7_skenario >= 1],
    ["Inti", "Pendukung"], default="-")

m.to_csv("data/kab_final.csv", index=False)
print(pd.crosstab(m.status_prioritas, m.tier_kualitas))
print("\nPrioritas Inti & Pendukung:")
print(m[m.status_prioritas != "-"].sort_values("rank_mobile")
      [["rank_mobile", "nama_geo", "tier_kualitas", "status_prioritas",
        "kelas"]].to_string(index=False))