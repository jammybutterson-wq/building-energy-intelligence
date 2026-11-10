WITH CTE1 AS (
    SELECT
        building_dimension.meter,
        building_dimension.primaryspaceusage,
        AVG(electricity) AS average_electricity
    FROM building_dimension
    JOIN electricity_readings
        ON building_dimension.meter = electricity_readings.meter
    WHERE building_dimension.primaryspaceusage IS NOT NULL
    GROUP BY
        building_dimension.meter,
        building_dimension.primaryspaceusage
)
SELECT
    CTE1.primaryspaceusage,
    AVG(CTE1.average_electricity) AS average_electricity
FROM CTE1
GROUP BY CTE1.primaryspaceusage
ORDER BY average_electricity DESC;