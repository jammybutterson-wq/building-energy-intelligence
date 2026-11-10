WITH daily_electricity AS (
    SELECT
        DATE_TRUNC('day', electricity_readings.timestamp) AS date,
        electricity_readings.meter,
        building_dimension.site_id,
        building_dimension.sqm,
        building_dimension.primaryspaceusage,
        building_dimension.sub_primaryspaceusage,
        AVG(electricity_readings.electricity) AS daily_average_electricity
    FROM electricity_readings
    JOIN building_dimension
        ON electricity_readings.meter = building_dimension.meter
    GROUP BY
        date,
        electricity_readings.meter,
        building_dimension.site_id,
        building_dimension.sqm,
        building_dimension.primaryspaceusage,
        building_dimension.sub_primaryspaceusage
),

daily_weather AS (
    SELECT
        DATE_TRUNC('day', weather.time) AS date,
        weather.site_id,
        SUM(weather.precipitation) AS daily_total_precipitation,
        AVG(weather.temperature_2m) AS daily_average_temperature
    FROM weather
    GROUP BY
        date,
        weather.site_id
)

SELECT
    daily_electricity.date,
    daily_electricity.meter,
    daily_electricity.site_id,
    daily_electricity.sqm,
    daily_electricity.primaryspaceusage,
    daily_electricity.sub_primaryspaceusage,
    daily_electricity.daily_average_electricity,
    daily_weather.daily_average_temperature,
    daily_weather.daily_total_precipitation
FROM daily_electricity
JOIN daily_weather
    ON daily_electricity.date = daily_weather.date
    AND daily_electricity.site_id = daily_weather.site_id
ORDER BY
    daily_electricity.meter,
    daily_electricity.date;