import duckdb

for t in ["mobile", "fixed"]:
    r = duckdb.sql(f"""
        SELECT COUNT(*) AS baris, SUM(tests) AS total_tes,
               ROUND(MIN(lon),1) AS lon_min, ROUND(MAX(lon),1) AS lon_max,
               ROUND(MIN(lat),1) AS lat_min, ROUND(MAX(lat),1) AS lat_max,
               ROUND(AVG(d_mbps),1) AS rata_unduh_mbps
        FROM 'data/id_{t}.parquet'
    """).fetchall()
    print(t, r)