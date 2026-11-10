import streamlit as st
import duckdb


# -------------------------
# PAGE SETUP
# -------------------------

st.set_page_config(
    page_title="Building Energy Intelligence",
    layout="wide"
)


# -------------------------
# DATA SETUP
# -------------------------

connection = duckdb.connect()

connection.execute("""
    CREATE OR REPLACE VIEW electricity_readings AS
    SELECT *
    FROM read_parquet('data/processed/electricity_long_*.parquet')
""")

connection.execute("""
    CREATE OR REPLACE VIEW building_dimension AS
    SELECT *
    FROM read_csv_auto('data/processed/building_dimension.csv')
""")

connection.execute("""
    CREATE OR REPLACE VIEW weather AS
    SELECT *
    FROM read_parquet('data/processed/weather_hourly.parquet')
""")


# -------------------------
# LOAD DASHBOARD QUERIES
# -------------------------

with open("sql/dashboard_building_type.sql") as file:
    building_type_query = file.read()

building_type_df = connection.execute(
    building_type_query
).fetchdf()


with open("sql/dashboard_anomalies.sql") as file:
    anomaly_query = file.read()

anomaly_df = connection.execute(
    anomaly_query
).fetchdf()


with open("sql/dashboard_building_detail.sql") as file:
    building_detail_query = file.read()

building_detail_df = connection.execute(
    building_detail_query
).fetchdf()


# -------------------------
# KPI VALUES
# -------------------------

result = connection.execute("""
    SELECT COUNT(DISTINCT meter)
    FROM building_dimension
""").fetchone()

meters = result[0]

anomaly_results = len(
    anomaly_df["meter"].unique()
)

unique_site = len(
    building_detail_df["site_id"].unique()
)


# -------------------------
# DASHBOARD HEADER
# -------------------------

st.title("Building Energy Intelligence")

st.write(
    "Explore building energy performance, "
    "peer-based anomalies and weather relationships"
)


# -------------------------
# TOP KPIs
# -------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Buildings analysed",
        value=meters
    )

with col2:
    st.metric(
        label="Anomalies flagged",
        value=anomaly_results
    )

with col3:
    st.metric(
        label="Sites with weather data",
        value=unique_site
    )

st.subheader("Portfolio overview")



# -------------------------
# OVERVIEW
# -------------------------

st.subheader("Average electricity by building type")

st.bar_chart(
    building_type_df,
    x="primaryspaceusage",
    y="average_electricity",
    horizontal=True,
    sort="-average_electricity"
)


st.subheader("Top 10 anomalies by relative intensity ratio")

st.bar_chart(
    anomaly_df.head(10),
    x="meter",
    y="relative_intensity_ratio",
    horizontal=True
)


# -------------------------
# BUILDING SELECTION
# -------------------------

st.subheader("Building explorer")

selected_building = st.selectbox(
    options=building_detail_df["meter"].unique(),
    label="Select a building"
)

st.subheader("Building details")

selected_df = building_detail_df[
    building_detail_df["meter"] == selected_building
]


# -------------------------
# BUILDING INFORMATION
# -------------------------

sqm = selected_df.iloc[0]["sqm"]

sub_primaryspaceusage = selected_df.iloc[0][
    "sub_primaryspaceusage"
]

primaryspaceusage = selected_df.iloc[0][
    "primaryspaceusage"
]


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Floor area (sqm)",
        value=round(sqm, 2)
    )

with col2:
    st.metric(
        label="Sub-type",
        value=sub_primaryspaceusage
    )

with col3:
    st.metric(
        label="Building type",
        value=primaryspaceusage
    )



# -------------------------
# ANOMALY STATUS
# -------------------------

selected_anomaly_df = anomaly_df[
    anomaly_df["meter"] == selected_building
]

if selected_anomaly_df.empty:

    st.subheader(
        "Anomaly status: Not flagged"
    )

else:

    st.subheader(
        "Anomaly status: Flagged for review"
    )

    relative_intensity_ratio = (
        selected_anomaly_df.iloc[0][
            "relative_intensity_ratio"
        ]
    )

    anomaly_sqm = selected_anomaly_df.iloc[0]["sqm"]

    peer_count = selected_anomaly_df.iloc[0][
        "peer_count"
    ]


    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Relative intensity vs peers",
            value=round(
                relative_intensity_ratio,
                2
            )
        )

    with col2:
        st.metric(
            label="Floor area (sqm)",
            value=round(
                anomaly_sqm,
                2
            )
        )

    with col3:
        st.metric(
            label="Peer group size",
            value=int(peer_count)
        )


# -------------------------
# BUILDING CHARTS
# -------------------------

col1, col2 = st.columns(2)

with col1:

    st.write("Daily electricity trend")

    st.line_chart(
        selected_df,
        x="date",
        y="daily_average_electricity"
    )


with col2:

    st.write("Electricity vs temperature")

    st.scatter_chart(
        selected_df,
        x="daily_average_temperature",
        y="daily_average_electricity"
    )