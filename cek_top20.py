import pandas as pd

m = pd.read_csv("data/kab_master.csv")

def build(m, t="mobile", w_s=0.5, w_p=0.5, thr=100):
    d = m[m[f"tests_{t}"] >= thr].copy()
    r = lambda s: s.rank(pct=True)
    d["Q"] = w_s * r(d[f"d_mbps_{t}"]) + (1 - w_s) * (1 - r(d[f"lat_ms_{t}"]))
    d["D"] = w_p * r(d.penduduk) + (1 - w_p) * r(d.kepadatan)
    d["U"] = d.D * (1 - d.Q)
    d["rank"] = d.U.rank(ascending=False, method="min").astype(int)
    return d

skenario = [{}, dict(w_s=.7), dict(w_s=.3), dict(w_p=.7), dict(w_p=.3),
            dict(thr=50), dict(thr=200)]
hitung = {}
for kw in skenario:
    for nama in build(m, **kw).nsmallest(20, "rank").nama_geo:
        hitung[nama] = hitung.get(nama, 0) + 1

top = build(m).nsmallest(20, "rank")
top["muncul_di_7_skenario"] = top.nama_geo.map(hitung)
cols = ["rank", "nama_geo", "penduduk", "d_mbps_mobile", "lat_ms_mobile",
        "Q", "D", "U", "muncul_di_7_skenario"]
print(top[cols].round(2).to_string(index=False))
top[cols].to_csv("data/top20_mobile.csv", index=False)