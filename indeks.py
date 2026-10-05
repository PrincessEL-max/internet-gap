import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

m = pd.read_csv("data/kab_master.csv")

# ---------- 1. EDA ----------
cols = ["d_mbps_mobile", "lat_ms_mobile", "d_mbps_fixed", "lat_ms_fixed",
        "penduduk", "kepadatan"]
print(m[cols].describe().round(1))
print("\nKorelasi Spearman:")
print(m[cols].corr(method="spearman").round(2))

os.makedirs("img", exist_ok=True)
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].hist(m.d_mbps_mobile.dropna(), bins=40)
ax[0].set_title("Unduh mobile per kab/kota (Mbps)")
ax[1].scatter(np.log10(m.kepadatan), m.d_mbps_mobile, s=10, alpha=0.6)
ax[1].set_xlabel("log10 kepadatan (jiwa/km²)")
ax[1].set_ylabel("Unduh mobile (Mbps)")
plt.tight_layout()
plt.savefig("img/eda.png", dpi=150)

# ---------- 2. Underserved Index ----------
# Q = kualitas (0-1, tinggi = bagus), D = permintaan (0-1), U = D * (1 - Q)
def build(m, t, w_s=0.5, w_p=0.5, thr=100):
    d = m[m[f"tests_{t}"] >= thr].copy()
    r = lambda s: s.rank(pct=True)
    d["Q"] = w_s * r(d[f"d_mbps_{t}"]) + (1 - w_s) * (1 - r(d[f"lat_ms_{t}"]))
    d["D"] = w_p * r(d.penduduk) + (1 - w_p) * r(d.kepadatan)
    d["U"] = d.D * (1 - d.Q)
    d["rank"] = d.U.rank(ascending=False, method="min").astype(int)
    return d[["shapeID", "Q", "D", "U", "rank"]]

# ---------- 3. Uji sensitivitas (mobile) ----------
base = build(m, "mobile")
top_base = set(base.nsmallest(20, "rank").shapeID)
skenario = {
    "baseline (50/50, ambang 100)": {},
    "kecepatan 70 / latensi 30": dict(w_s=0.7),
    "kecepatan 30 / latensi 70": dict(w_s=0.3),
    "penduduk 70 / kepadatan 30": dict(w_p=0.7),
    "penduduk 30 / kepadatan 70": dict(w_p=0.3),
    "ambang tes 50": dict(thr=50),
    "ambang tes 200": dict(thr=200),
}
rows = []
for nama, kw in skenario.items():
    s = build(m, "mobile", **kw)
    c = base.merge(s, on="shapeID", suffixes=("_b", "_s"))
    rho = c.U_b.corr(c.U_s, method="spearman")
    irisan = len(top_base & set(s.nsmallest(20, "rank").shapeID))
    rows.append((nama, len(s), round(rho, 3), irisan))
print("\nUji sensitivitas:")
print(pd.DataFrame(rows, columns=["skenario", "n_daerah",
      "spearman_vs_baseline", "irisan_top20"]).to_string(index=False))

# ---------- 4. Gabung hasil baseline & simpan ----------
for t in ["mobile", "fixed"]:
    b = build(m, t).rename(columns={"Q": f"Q_{t}", "D": f"D_{t}",
                                    "U": f"U_{t}", "rank": f"rank_{t}"})
    m = m.merge(b, on="shapeID", how="left")

med = m.kepadatan.median()
m["kelas"] = np.where(m.kepadatan >= med,
                      "Padat: upgrade kapasitas", "Jarang: perluasan cakupan")
m["data_memadai_mobile"] = m.tests_mobile >= 100
m.to_csv("data/kab_index.csv", index=False)

print("\nTop 20 prioritas (mobile):")
top = m.nsmallest(20, "rank_mobile")[["nama_geo", "penduduk", "kepadatan",
      "d_mbps_mobile", "lat_ms_mobile", "U_mobile", "kelas"]]
print(top.round(2).to_string(index=False))

print("\nData tipis (<100 tes), penduduk terbesar:")
tipis = m[~m.data_memadai_mobile].sort_values("penduduk", ascending=False)
print(tipis[["nama_geo", "penduduk", "kepadatan", "tests_mobile"]]
      .head(10).to_string(index=False))
print("\nTersimpan: data/kab_index.csv dan img/eda.png")