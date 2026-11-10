# Building Energy Intelligence

## Overview

Building Energy Intelligence is an analytics application that combines building electricity meter data, building metadata and weather data. It helps identify consumption trends, unusual energy behaviour and relationships between electricity use, building characteristics and temperature.

## Problem

Large volumes of electricity meter data across many buildings can be difficult to analyse and interpret using raw readings alone. Without a clear way to compare buildings and visualise consumption, trends and unusual behaviour can easily be missed. This makes it harder to identify buildings that may warrant further investigation, compare similar buildings, understand which building types consume the most electricity, and observe how consumption changes over time.

## Solution

I built an energy analytics application that connects electricity meter readings with building metadata, allowing meters to be analysed by building type and sub-type. The raw data first went through a quality-assessment process to identify missing data, long gaps and meters with insufficient reliable readings, with unsuitable meters excluded from further analysis.

SQL was then used to join and aggregate the processed datasets, analyse consumption patterns and compare buildings against similar peer groups to identify unusually high electricity intensity. Weather data was added to provide additional context when investigating changes in electricity use.

The Streamlit dashboard brings these results together, providing portfolio-level KPIs, building-type comparisons, anomaly rankings and individual building drill-downs.

## Tech Stack

- **Python** — used as the main programming language for data processing, analysis and application development.
- **pandas** — used to load, inspect, clean and transform the raw electricity and metadata files into structured DataFrames.
- **DuckDB / SQL** — used to query, join and aggregate the processed datasets and create the analysis used by the dashboard.
- **Parquet** — used to store the processed electricity and weather datasets in an efficient columnar format that can be queried quickly by DuckDB.
- **Streamlit** — used to build the interactive web dashboard and building explorer.
- **Open-Meteo API** — used to retrieve historical temperature and precipitation data corresponding to the electricity dataset.
- **Git / GitHub** — used for version control and to store and present the project repository.

## Data Pipeline

The project began with raw electricity meter data containing thousands of meter columns and hourly readings. The data was inspected and cleaned before analysis, including checks for missing readings, long gaps, active coverage and meters with very limited usable history. Completely empty or unreliable meters were excluded, while meters with sufficient usable data were retained.

The electricity dataset was then reshaped from wide format into long format, where each row represents a meter reading at a particular timestamp. This structure made the data much easier to query, aggregate and join using SQL.

The processed electricity data and historical weather data were stored as Parquet files for efficient analytical querying. DuckDB then created views over these processed files, allowing the Streamlit application to run SQL queries directly against the prepared datasets.

## Anomaly Detection

Data-quality checks were first used to make sure meters had enough reliable readings to be included in the analysis. Missing data, active coverage, long gaps and very short histories were assessed before unreliable meters were excluded.

For anomaly detection, each building's average electricity use was adjusted for building size by calculating electricity use per square metre. Buildings were then compared against the median intensity of other buildings with the same primary building type.

A building was flagged when its relative intensity was at least three times the peer median and the comparison group contained at least 20 buildings.

A flagged building is not automatically considered inefficient. It simply indicates unusually high electricity intensity compared with similar buildings and should be investigated further before any conclusion is made.

## Weather Analysis

Historical temperature and precipitation data was retrieved using the Open-Meteo API for sites where location information was available. Latitude, longitude and timezone information from the building metadata were used to request the relevant weather records, which were then linked back to buildings using their site IDs.

Electricity and weather data were aggregated to daily level before being joined using both date and site ID. This provided a clearer way to compare changes in electricity use with changes in temperature while avoiding issues that can arise when matching hourly timestamps across different time zones.

The analysis showed that some electricity patterns varied with temperature. For example, `Rat_public_Wilbur` showed higher average electricity use during hotter and colder conditions, but its electricity intensity remained substantially higher than comparable fire stations across temperature bands.

This suggests weather may influence consumption but does not fully explain the building's unusually high usage. The relationship should be treated as correlation rather than proof that weather directly caused the changes in electricity use.

## Dashboard

When a user opens the Streamlit dashboard, they immediately see key portfolio-level information including the total number of buildings analysed, anomalies flagged and sites with weather data. The dashboard also provides an overview of average electricity use by building type and highlights the highest-ranked anomalies.

Users can then select an individual building to explore in more detail. For each building, the dashboard displays its floor area, primary building type and sub-type, along with its anomaly status.

It also shows the building's daily electricity trend and the relationship between electricity use and temperature.

## Key Findings

- **1,512 buildings** passed the data-quality process and were included in the main analysis.
- **129 buildings** were flagged for further investigation based on unusually high electricity intensity relative to comparable buildings.
- **Healthcare buildings** had the highest average electricity use of the building types analysed.
- `Rat_public_Wilbur`, a fire station, showed higher average electricity use during hotter and colder conditions, suggesting some relationship between temperature and consumption.
- However, `Rat_public_Wilbur` remained substantially above comparable fire stations across temperature bands, meaning weather alone did not explain its unusually high electricity intensity.
- Weather data therefore provided additional context for investigating consumption patterns rather than providing proof of why an anomaly occurred.

## Project Structure

- `app.py` — contains the Streamlit application code used to load the prepared data, run dashboard queries and display the interactive dashboard.
- `data/raw/` — contains the original electricity meter data and building metadata used as the starting point for the project.
- `data/processed/` — contains cleaned and transformed datasets, including building and site information, meter-quality results, weather data and the electricity dataset stored across multiple Parquet files.
- `src/` — contains the Python scripts used to load, inspect, clean, reshape and prepare the raw data, build supporting datasets and retrieve weather data.
- `sql/` — contains the SQL queries used for exploration, anomaly analysis and preparing the datasets displayed in the dashboard. Several queries use CTEs to organise multi-stage analysis.
- `requirements.txt` — lists the Python libraries required to run the project.
- `README.md` — provides an overview of the project, methodology, findings and instructions for running it.

## How to Run

1. Clone the repository and navigate into the project folder.
2. Create a Python virtual environment.
3. Activate the virtual environment.
4. Install the required dependencies using `requirements.txt`.
5. Launch the Streamlit application with `streamlit run app.py`.

## Limitations

- Anomaly flags are based on analytical heuristics and do not prove that a building is inefficient.
- Relationships between weather and electricity consumption represent correlation and should not be interpreted as proof of causation.
- Weather analysis was limited to sites with usable location information, so not every site in the electricity dataset could be included.
- Missing readings, gaps and other data-quality issues may influence the results despite the quality-filtering process.
- Comparing buildings within the same building type provides useful peer context, but does not account for every operational factor that may affect electricity consumption.