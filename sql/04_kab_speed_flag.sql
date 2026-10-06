CREATE OR REPLACE TABLE telco.kab_speed_flag AS
SELECT *, tests >= 100 AS data_cukup
FROM telco.kab_speed;