import duckdb, os, subprocess, urllib.request

def exists(u):
    try:
        urllib.request.urlopen(urllib.request.Request(u, method="HEAD"))
        return True
    except Exception:
        return False

def valid(path):
    try:
        duckdb.connect().execute(f"SELECT COUNT(*) FROM read_parquet('{path}')").fetchone()
        return True
    except Exception:
        return False

def download(u, dest):
    while True:   # ulangi sampai berhasil; -C - melanjutkan unduhan yang terputus
        r = subprocess.run(["curl.exe", "-L", "-C", "-", "--retry", "10",
                            "--retry-delay", "5", "-o", dest, u])
        if r.returncode == 0:
            return
        print("Terputus, mencoba lagi...")

Q = [(1,"01"),(2,"04"),(3,"07"),(4,"10")]
os.makedirs("raw", exist_ok=True)
con = duckdb.connect()

for typ in ["mobile", "fixed"]:
    out = f"data/id_{typ}.parquet"
    if os.path.exists(out) and valid(out):
        print(typ, "sudah selesai, dilewati")
        continue

    urls = [f"https://ookla-open-data.s3.amazonaws.com/parquet/performance/type={typ}/year={y}/quarter={q}/{y}-{m}-01_performance_{typ}_tiles.parquet"
            for y in (2025, 2026) for q, m in Q]
    urls = [u for u in urls if exists(u)][-4:]

    local = []
    for u in urls:
        dest = "raw/" + u.split("/")[-1]
        print("Mengunduh", dest)
        download(u, dest)
        local.append(dest)

    print(typ, "menyaring data Indonesia...")
    con.execute(f"""
    COPY (
      SELECT tests,
             avg_d_kbps/1000.0 AS d_mbps, avg_u_kbps/1000.0 AS u_mbps, avg_lat_ms,
             CAST(regexp_extract(tile,'POLYGON\\(\\(([-0-9.]+) ([-0-9.]+)',1) AS DOUBLE) AS lon,
             CAST(regexp_extract(tile,'POLYGON\\(\\(([-0-9.]+) ([-0-9.]+)',2) AS DOUBLE) AS lat
      FROM read_parquet({local})
      WHERE lon BETWEEN 95 AND 141.5 AND lat BETWEEN -11.5 AND 6.5 AND tests >= 5
    ) TO '{out}' (FORMAT PARQUET)
    """)
    print(typ, "selesai")