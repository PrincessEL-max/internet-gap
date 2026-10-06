CREATE OR REPLACE TABLE telco.kab_speed AS
SELECT t.tipe, k.shapeID, k.shapeName,
  SAFE_DIVIDE(SUM(t.d_mbps * t.tests), SUM(t.tests)) AS d_mbps,
  SAFE_DIVIDE(SUM(t.u_mbps * t.tests), SUM(t.tests)) AS u_mbps,
  SAFE_DIVIDE(SUM(t.avg_lat_ms * t.tests), SUM(t.tests)) AS lat_ms,
  SUM(t.tests) AS tests,
  COUNT(*) AS n_tiles
FROM telco.tiles_all t
JOIN telco.kab_geo k
  ON ST_WITHIN(ST_GEOGPOINT(t.lon, t.lat), k.geog)
GROUP BY t.tipe, k.shapeID, k.shapeName;