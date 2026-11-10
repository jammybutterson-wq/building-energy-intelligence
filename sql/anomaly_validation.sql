WITH CTE AS (
    SELECT
        DATE_TRUNC('month', timestamp) AS month,
        AVG(electricity) AS average_electricity,
        building_dimension.sqm,
        electricity_readings.meter,
        AVG(electricity) / building_dimension.sqm AS monthly_electricity_per_sqm
    FROM electricity_readings
    JOIN building_dimension
        ON electricity_readings.meter = building_dimension.meter
    WHERE sub_primaryspaceusage IN (
        'Fire Station',
        'Fire Station, Fire Stations'
    )
    GROUP BY
        electricity_readings.meter,
        month,
        building_dimension.sqm
),

CTE2 AS (
    SELECT
        month,
        MEDIAN(monthly_electricity_per_sqm) AS typical_fire_station_intensity
    FROM CTE
    GROUP BY month
)

SELECT
    CTE.month,
    CTE.monthly_electricity_per_sqm,
    CTE2.typical_fire_station_intensity,
    CTE.monthly_electricity_per_sqm
        / CTE2.typical_fire_station_intensity AS relative_intensity_ratio
FROM CTE
JOIN CTE2
    ON CTE.month = CTE2.month
WHERE CTE.meter = 'Rat_public_Wilbur'
ORDER BY CTE.month;