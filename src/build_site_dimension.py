import csv

import pandas as pd

metadata_df = pd.read_csv("data/raw/metadata.txt")

missing_coords = metadata_df["lat"].isna() | metadata_df["lng"].isna()

print (metadata_df.loc[missing_coords, "site_id"].unique())

subject_df = metadata_df[["site_id", "lat", "lng"]]

subject_df = subject_df.dropna()

subject_df = subject_df.drop_duplicates()

print (subject_df)
print (subject_df.shape)
print (subject_df.duplicated().sum())
print(subject_df["site_id"].nunique())

site_df = metadata_df[["site_id", "lat", "lng", "timezone"]]

site_df = site_df.dropna(subset=["lat", "lng"])
site_df = site_df.drop_duplicates()

print(site_df.shape)
print(site_df["site_id"].nunique())

site_df.to_csv("data/processed/site_dimension.csv", index=False)

print ([site_df["site_id"]])

print (site_df[site_df["site_id"] == "Lamb"])

