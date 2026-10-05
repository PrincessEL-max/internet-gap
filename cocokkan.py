import pandas as pd, re
from rapidfuzz import process, fuzz

bps = pd.read_csv("data/bps_clean.csv")
poly = pd.read_csv("data/kab_luas.csv")
spd = pd.read_csv("data/kab_speed_flag.csv")

def norm(s):
    s = str(s).lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = s.replace("kota administrasi", "kota")
    s = re.sub(r"\bkabupaten\b|\bkab\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()

# koreksi manual: nama BPS -> shapeName di GeoJSON
OVERRIDE = {"Kotabaru": "Kota Baru", "Karangasem": "Karang Asem"}
BUANG = ["Danau", "Danau Toba", "Hutan", "Waduk Cirata", "Wadung Kedungombo"]

poly = poly[~poly.shapeName.isin(BUANG)].reset_index(drop=True)
poly["key"] = poly.shapeName.map(norm)
by_name = poly.set_index("shapeName")

rows = []
for _, r in bps.iterrows():
    if r.kabupaten_kota in OVERRIDE:
        nama_geo, skor = OVERRIDE[r.kabupaten_kota], 100.0
        sid = by_name.loc[nama_geo, "shapeID"]
    else:
        _, skor, idx = process.extractOne(norm(r.kabupaten_kota), poly.key.tolist(),
                                          scorer=fuzz.token_sort_ratio)
        nama_geo, sid = poly.iloc[idx].shapeName, poly.iloc[idx].shapeID
    rows.append((r.kabupaten_kota, r.penduduk, sid, nama_geo, round(skor, 1)))

m = pd.DataFrame(rows, columns=["nama_bps", "penduduk", "shapeID", "nama_geo", "skor"])

print("Baris:", len(m), "| shapeID unik:", m.shapeID.nunique(), "| poligon tersisa:", len(poly))
print("Total penduduk:", f"{m.penduduk.sum():,}")
print("\nPasangan dengan skor < 100 (cek dengan mata):")
print(m[m.skor < 100].sort_values("skor").to_string(index=False))

# tabel induk: penduduk + luas + kecepatan (mobile & fixed berdampingan)
master = m.merge(poly[["shapeID", "luas_km2"]], on="shapeID")
master["kepadatan"] = master.penduduk / master.luas_km2

wide = spd.pivot(index="shapeID", columns="tipe",
                 values=["d_mbps", "u_mbps", "lat_ms", "tests", "data_cukup"])
wide.columns = [f"{a}_{b}" for a, b in wide.columns]
master = master.merge(wide.reset_index(), on="shapeID", how="left")

print("\nPunya data mobile:", master.d_mbps_mobile.notna().sum(),
      "| cukup:", (master.data_cukup_mobile == True).sum())
print("Punya data fixed :", master.d_mbps_fixed.notna().sum(),
      "| cukup:", (master.data_cukup_fixed == True).sum())

master.to_csv("data/kab_master.csv", index=False)
print("\nTersimpan: data/kab_master.csv")