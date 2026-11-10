WITH CTE1 AS (
    SELECT
        electricity_readings.meter,
        building_dimension.primaryspaceusage,
        building_dimension.sqm,
        AVG(electricity_readings.electricity) AS building_average,
        AVG(electricity_readings.electricity) / building_dimension.sqm
            AS electricity_per_sqm
    FROM building_dimension
    JOIN electricity_readings
        ON building_dimension.meter = electricity_readings.meter
    GROUP BY
        electricity_readings.meter,
        building_dimension.primaryspaceusage,
        building_dimension.sqm
),

CTE2 AS (
    SELECT
        primaryspaceusage,
        MEDIAN(electricity_per_sqm) AS peer_average_intensity,
        COUNT(*) AS peer_count
    FROM CTE1
    GROUP BY primaryspaceusage
),

CTE3 AS (
    SELECT
        CTE1.meter,
        CTE1.primaryspaceusage,
        CTE1.sqm,
        CTE1.building_average,
        CTE1.electricity_per_sqm,
        CTE2.peer_average_intensity,
        CTE2.peer_count,

        CTE1.electricity_per_sqm / CTE2.peer_average_intensity
            AS relative_intensity_ratio,

        CASE
            WHEN CTE1.electricity_per_sqm / CTE2.peer_average_intensity >= 3
                 AND CTE2.peer_count >= 20
            THEN 'High'
            ELSE 'Normal'
        END AS anomaly_flag

    FROM CTE1
    JOIN CTE2
        ON CTE1.primaryspaceusage = CTE2.primaryspaceusage
)

SELECT *
FROM CTE3
ORDER BY relative_intensity_ratio DESC;