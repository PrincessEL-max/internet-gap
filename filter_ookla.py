import duckdb, urllib.request

def exists(u):
    try:
        urllib.request.urlopen(urllib.request.Request(u, method="HEAD"))
        return True
    except Exception:
        return False

Q = [(1,"01"),(2,"04"),(3,"07"),(4,"10")]
con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")

for typ in ["mobile", "fixed"]:
    urls = [f"https://ookla-open-data.s3.amazonaws.com/parquet/performance/type={typ}/year={y}/quarter={q}/{y}-{m}-01_performance_{typ}_tiles.parquet"
            for y in (2025, 2026) for q, m in Q]
    urls = [u for u in urls if exists(u)][-4:]   # 4 kuartal terbaru yang ada
    print(typ, urls)
    con.execute(f"""
    COPY (
      SELECT tests,
             avg_d_kbps/1000.0 AS d_mbps, avg_u_kbps/1000.0 AS u_mbps, avg_lat_ms,
             CAST(regexp_extract(tile,'POLYGON\\(\\(([-0-9.]+) ([-0-9.]+)',1) AS DOUBLE) AS lon,
             CAST(regexp_extract(tile,'POLYGON\\(\\(([-0-9.]+) ([-0-9.]+)',2) AS DOUBLE) AS lat
      FROM read_parquet({urls})
      WHERE lon BETWEEN 95 AND 141.5 AND lat BETWEEN -11.5 AND 6.5 AND tests >= 5
    ) TO 'data/id_{typ}.parquet' (FORMAT PARQUET)
    """)