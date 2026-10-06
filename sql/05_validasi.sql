-- jumlah kab/kota per tipe
SELECT tipe, COUNT(*) AS n_kab FROM telco.kab_speed GROUP BY tipe;

-- seberapa banyak daerah yang datanya tipis
SELECT tipe,
  COUNT(*) AS n_kab,
  COUNTIF(tests >= 50)  AS n_ge50,
  COUNTIF(tests >= 100) AS n_ge100,
  COUNTIF(tests >= 500) AS n_ge500
FROM telco.kab_speed
GROUP BY tipe;

-- 5 tercepat dan 5 terlambat (mobile)
(SELECT shapeName, ROUND(d_mbps,1) AS d_mbps, tests FROM telco.kab_speed
 WHERE tipe='mobile' ORDER BY d_mbps DESC LIMIT 5)
UNION ALL
(SELECT shapeName, ROUND(d_mbps,1), tests FROM telco.kab_speed
 WHERE tipe='mobile' ORDER BY d_mbps ASC LIMIT 5);