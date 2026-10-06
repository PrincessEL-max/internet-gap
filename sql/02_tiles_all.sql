CREATE OR REPLACE TABLE telco.tiles_all AS
SELECT 'mobile' AS tipe, tests, d_mbps, u_mbps, avg_lat_ms, lon, lat
FROM telco.id_mobile
UNION ALL
SELECT 'fixed' AS tipe, tests, d_mbps, u_mbps, avg_lat_ms, lon, lat
FROM telco.id_fixed;