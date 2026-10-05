import geopandas as gpd

kab = gpd.read_file("data/idn_adm2.geojson")[["shapeID", "shapeName", "geometry"]]
kab["wkt"] = kab.geometry.simplify(0.001).to_wkt()
kab.drop(columns="geometry").to_csv("data/kab_wkt.csv", index=False)
print("selesai")