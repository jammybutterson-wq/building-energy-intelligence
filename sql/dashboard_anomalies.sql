WITH CTE1 AS (
SELECT
    building_dimension.meter,
    building_dimension.primaryspaceusage,
    building_dimension.sqm,
    AVG(electricity_readings.electricity) AS average_electricity,
    AVG(electricity_readings.electricity) / building_dimension.sqm AS electricity_per_sqm
FROM building_dimension
JOIN electricity_readings
    ON building_dimension.meter = electricity_readings.meter
GROUP BY
    building_dimension.meter,
    building_dimension.primaryspaceusage,
    building_dimension.sqm
    ),
    CTE2 AS(
SELECT CTE1.primaryspaceusage, MEDIAN(CTE1.electricity_per_sqm) AS median_electricity_per_sqm,
COUNT(*) AS peer_count
FROM CTE1
GROUP BY CTE1.primaryspaceusage
    )
SELECT 
    CTE1.meter,
    CTE1.primaryspaceusage,
    CTE1.sqm,
    CTE2.median_electricity_per_sqm,
    CTE1.electricity_per_sqm,
    CTE1.electricity_per_sqm / CTE2.median_electricity_per_sqm AS relative_intensity_ratio,
    cte2.peer_count
FROM CTE1
JOIN CTE2
    ON CTE1.primaryspaceusage = CTE2.primaryspaceusage
WHERE relative_intensity_ratio >= 3 AND
peer_count >= 20
ORDER BY relative_intensity_ratio DESC;    