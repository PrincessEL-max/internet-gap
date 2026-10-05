import os
import geopandas as gpd
import pandas as pd

g = gpd.read_file("data/idn_adm2.geojson")[["shapeID", "geometry"]]
k = pd.read_csv("data/kab_final.csv")

cols = ["shapeID", "nama_geo", "penduduk", "kepadatan", "luas_km2",
        "d_mbps_mobile", "lat_ms_mobile", "tests_mobile",
        "d_mbps_fixed", "lat_ms_fixed",
        "Q_mobile", "D_mobile", "U_mobile", "rank_mobile",
        "kelas", "tier_kualitas", "status_prioritas",
        "muncul_di_7_skenario", "data_memadai_mobile"]

out = g.merge(k[cols], on="shapeID", how="inner")   # poligon non-administratif gugur
out["geometry"] = out.geometry.simplify(0.01, preserve_topology=True)
out.to_file("data/kab_peta.geojson", driver="GeoJSON")

print(len(out), "kab/kota")
print("Ukuran:", round(os.path.getsize("data/kab_peta.geojson") / 1e6, 1), "MB")