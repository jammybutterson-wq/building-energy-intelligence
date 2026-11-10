import requests
import pandas as pd


site_df = pd.read_csv("data/processed/site_dimension.csv")

start_date = "2016-01-01"
end_date = "2017-12-31"


def fetch_weather_data(latitude, longitude, timezone, start_date, end_date, site_id):

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,precipitation",
        "timezone": timezone
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    weather_df = pd.DataFrame(data["hourly"])

    weather_df["time"] = pd.to_datetime(weather_df["time"])
    weather_df["site_id"] = site_id

    return weather_df


weather_frames = []

for index, row in site_df.iterrows():

    weather = fetch_weather_data(
        row["lat"],
        row["lng"],
        row["timezone"],
        start_date,
        end_date,
        row["site_id"]
    )

    weather_frames.append(weather)



weather_df = pd.concat(weather_frames, ignore_index=True)

weather_df.to_parquet("data/processed/weather_hourly.parquet", index=False)

duplicate_site_hours = weather_df.duplicated(
    subset=["site_id", "time"]
).sum()

print(duplicate_site_hours)