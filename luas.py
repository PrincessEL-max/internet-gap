import geopandas as gpd

kab = gpd.read_file("data/idn_adm2.geojson")
kab["luas_km2"] = kab.to_crs("EPSG:6933").area / 1e6
kab[["shapeID", "shapeName", "luas_km2"]].to_csv("data/kab_luas.csv", index=False)
print(len(kab), "kab/kota")