# python src/load_data.py

import pandas as pd


def load_data(filepath):
    df = pd.read_csv(filepath)
    return df


# --------------------
# Load data
# --------------------

df = load_data("data/raw/electricity_cleaned.txt")
metadata_df = load_data("data/raw/metadata.txt")


# --------------------
# Remove completely empty meter columns
# --------------------

missing_values = df.isna().sum()

empty_columns = missing_values[
    missing_values == len(df)
].index

df = df.drop(columns=empty_columns)


# --------------------
# Validate timestamp
# --------------------

df["timestamp"] = pd.to_datetime(df["timestamp"])

duplicate_count = df["timestamp"].duplicated().sum()

time_gaps = df["timestamp"].diff().dropna()

incorrect_time_gaps = (
    time_gaps != pd.Timedelta(hours=1)
).sum()

print(f"Duplicate timestamps: {duplicate_count}")
print(f"Incorrect hourly gaps: {incorrect_time_gaps}")


# --------------------
# Create meter quality report
# --------------------

meter_columns = df.columns.drop("timestamp")

meter_results = []

for meter in meter_columns:

    meter_data = df[meter]

    # Basic statistics
    valid_count = meter_data.count()
    average_valid_reading = meter_data.mean()
    minimum_valid_reading = meter_data.min()
    maximum_valid_reading = meter_data.max()

    missing_percentage = (
        (len(meter_data) - valid_count)
        / len(meter_data)
        * 100
    )

    # Active period
    valid_readings = meter_data.dropna()

    first_valid_index = valid_readings.index.min()
    last_valid_index = valid_readings.index.max()

    active_meter_data = meter_data.loc[
        first_valid_index:last_valid_index
    ]

    first_valid_timestamp = df.loc[
        first_valid_index,
        "timestamp"
    ]

    last_valid_timestamp = df.loc[
        last_valid_index,
        "timestamp"
    ]

    # Active-period coverage
    possible_readings = (
        last_valid_index
        - first_valid_index
        + 1
    )

    active_coverage = (
        valid_count
        / possible_readings
        * 100
    )

    # Longest internal missing gap
    current_gap = 0
    longest_gap = 0

    for is_missing in active_meter_data.isna():

        if is_missing:
            current_gap += 1
            longest_gap = max(
                longest_gap,
                current_gap
            )

        else:
            current_gap = 0

    # Store meter results
    meter_result = {
        "meter": meter,
        "valid_count": valid_count,
        "missing_percentage": missing_percentage,
        "longest_gap": longest_gap,
        "average": average_valid_reading,
        "min": minimum_valid_reading,
        "max": maximum_valid_reading,
        "first_valid_timestamp": first_valid_timestamp,
        "last_valid_timestamp": last_valid_timestamp,
        "active_coverage": active_coverage,
    }

    meter_results.append(meter_result)


# --------------------
# Convert results to DataFrame
# --------------------

quality_df = pd.DataFrame(meter_results)


# --------------------
# Quality classification
# --------------------

# Good:
# >= 95% active coverage
# AND no internal gap longer than 7 days

good_condition = (
    (quality_df["active_coverage"] >= 95)
    &
    (quality_df["longest_gap"] <= 168)
)

# Poor:
# < 80% active-period coverage

poor_condition = (
    quality_df["active_coverage"] < 80
)

# Everything starts as Review
quality_df["quality_status"] = "Review"

quality_df.loc[
    good_condition,
    "quality_status"
] = "Good"

quality_df.loc[
    poor_condition,
    "quality_status"
] = "Poor"


# --------------------
# Warning flags
# --------------------

# Internal missing gap longer than 30 days
quality_df["large_gap_flag"] = (
    quality_df["longest_gap"] > 720
)

# Less than 30 days of valid hourly readings
quality_df["short_history_flag"] = (
    quality_df["valid_count"] < 720
)


# --------------------
# Analysis eligibility
# --------------------

# Keep Good/Review meters with enough history.
# Large gaps remain as warnings rather than automatic exclusions.

quality_df["analysis_eligible"] = (
    (quality_df["quality_status"] != "Poor")
    &
    (~quality_df["short_history_flag"])
)


# --------------------
# Sanity checks
# --------------------

print("\nQuality status:")
print(
    quality_df["quality_status"].value_counts()
)

print("\nWarning flags:")
print(
    quality_df[
        [
            "large_gap_flag",
            "short_history_flag"
        ]
    ].sum()
)

print("\nAnalysis eligibility:")
print(
    quality_df["analysis_eligible"].value_counts()
)


# --------------------
# Save quality report
# --------------------

quality_df.to_csv(
    "data/processed/meter_quality_report.csv",
    index=False
)


# --------------------
# Prepare analysis data
# --------------------

eligible_meters = quality_df[
    quality_df["analysis_eligible"]
]["meter"].tolist()

analysis_columns = ["timestamp"] + eligible_meters

analysis_df = df[
    analysis_columns
].copy()


# --------------------
# Write electricity fact files
# --------------------

for start in range(
    0,
    len(eligible_meters),
    100
):

    chunk_meters = eligible_meters[
        start:start + 100
    ]

    chunk_columns = [
        "timestamp"
    ] + chunk_meters

    chunk_df = analysis_df[
        chunk_columns
    ].copy()

    chunk_long = chunk_df.melt(
        id_vars="timestamp",
        var_name="meter",
        value_name="electricity"
    )

    chunk_long = chunk_long.dropna(
        subset=["electricity"]
    )

    output_file = (
        f"data/processed/"
        f"electricity_long_{start:04d}.parquet"
    )

    chunk_long.to_parquet(
        output_file,
        index=False
    )


# --------------------
# Create building dimension
# --------------------

eligible_quality_df = quality_df[
    quality_df["analysis_eligible"]
].copy()

joined_df = eligible_quality_df.merge(
    metadata_df,
    how="left",
    left_on="meter",
    right_on="building_id"
)

building_dimension_df = joined_df[
    [
        "meter",
        "site_id",
        "primaryspaceusage",
        "sub_primaryspaceusage",
        "sqm",
        "timezone"
    ]
].copy()


# --------------------
# Save building dimension
# --------------------

building_dimension_df.to_csv(
    "data/processed/building_dimension.csv",
    index=False
)

