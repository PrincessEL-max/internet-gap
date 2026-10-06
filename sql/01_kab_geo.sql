CREATE OR REPLACE TABLE telco.kab_geo AS
SELECT
  string_field_0 AS shapeID,
  string_field_1 AS shapeName,
  ST_GEOGFROMTEXT(string_field_2, make_valid => TRUE) AS geog
FROM telco.kab_wkt
WHERE string_field_0 != 'shapeID';