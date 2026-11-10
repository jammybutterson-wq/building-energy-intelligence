import duckdb


connection = duckdb.connect()

connection.execute("""
    CREATE OR REPLACE VIEW electricity_readings AS
    SELECT *
    FROM read_parquet(
        'data/processed/electricity_long_*.parquet'
    )
""")

connection.execute("""
    CREATE OR REPLACE VIEW building_dimension AS
    SELECT *
    FROM read_csv_auto(
        'data/processed/building_dimension.csv'
    )
""")

connection.execute("""
    CREATE OR REPLACE VIEW weather AS
    SELECT *
    FROM read_parquet('data/processed/weather_hourly.parquet')
""")

with open("sql/explore.sql") as file:
    query = file.read()

result = connection.execute(query).fetchdf()

print(result)

connection.close()