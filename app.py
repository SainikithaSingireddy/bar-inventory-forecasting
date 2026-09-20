import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Bar Inventory Forecasting",
    page_icon="🍸",
    layout="wide"
)

st.title("🍸 Hotel Bar Inventory Forecasting")
st.write(
    "Demand forecasting and inventory recommendation dashboard "
    "for hotel bar operations."
)

daily_data = pd.read_csv("data/processed/daily_bar_consumption.csv")
simulation_data = pd.read_csv("data/processed/inventory_simulation.csv")
metrics_data = pd.read_csv("data/processed/metrics_summary.csv")
stockout_data = pd.read_csv("data/processed/stockout_by_item.csv")
overstock_data = pd.read_csv("data/processed/overstock_summary.csv")

daily_data["Date"] = pd.to_datetime(daily_data["Date"])
simulation_data["Date"] = pd.to_datetime(simulation_data["Date"])

cutoff_date = pd.Timestamp("2023-10-23")

all_dates = pd.date_range(
    daily_data["Date"].min(),
    daily_data["Date"].max(),
    freq="D"
)

all_bars = daily_data["Bar Name"].unique()
all_brands = daily_data["Brand Name"].unique()

full_index = pd.MultiIndex.from_product(
    [all_dates, all_bars, all_brands],
    names=["Date", "Bar Name", "Brand Name"]
)

daily_complete = (
    daily_data
    .set_index(["Date", "Bar Name", "Brand Name"])
    .reindex(full_index, fill_value=0)
    .reset_index()
)

daily_complete = daily_complete.sort_values(
    ["Bar Name", "Brand Name", "Date"]
)

daily_complete["Lag_1"] = (
    daily_complete
    .groupby(["Bar Name", "Brand Name"])["Consumed (ml)"]
    .shift(1)
)

daily_complete["Lag_7"] = (
    daily_complete
    .groupby(["Bar Name", "Brand Name"])["Consumed (ml)"]
    .shift(7)
)

daily_complete["Lag_14"] = (
    daily_complete
    .groupby(["Bar Name", "Brand Name"])["Consumed (ml)"]
    .shift(14)
)

daily_complete["Rolling_7"] = (
    daily_complete
    .groupby(["Bar Name", "Brand Name"])["Consumed (ml)"]
    .transform(
        lambda x: x.shift(1).rolling(7).mean()
    )
)

daily_complete["Day_of_Week"] = daily_complete["Date"].dt.dayofweek

model_data = daily_complete.dropna().copy()

train_data = model_data[
    model_data["Date"] < cutoff_date
].copy()

train_stats = (
    train_data
    .groupby(["Bar Name", "Brand Name"])["Consumed (ml)"]
    .agg(["mean", "std"])
    .reset_index()
)

train_stats.columns = [
    "Bar Name",
    "Brand Name",
    "Average Daily Demand (ml)",
    "Demand Std (ml)"
]

lead_time_days = 3
z_value = 1.645

train_stats["Lead Time Demand (ml)"] = (
    train_stats["Average Daily Demand (ml)"] * lead_time_days
)

train_stats["Safety Stock (ml)"] = (
    z_value
    * train_stats["Demand Std (ml)"]
    * np.sqrt(lead_time_days)
)

train_stats["Recommended Par Level (ml)"] = (
    train_stats["Lead Time Demand (ml)"]
    + train_stats["Safety Stock (ml)"]
)

st.subheader("Project Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Bars", daily_data["Bar Name"].nunique())

with col2:
    st.metric("Brands", daily_data["Brand Name"].nunique())

with col3:
    total_litres = daily_data["Consumed (ml)"].sum() / 1000
    st.metric("Total Consumption", f"{total_litres:,.1f} L")

st.subheader("Consumption Analysis")

col1, col2 = st.columns(2)

with col1:
    selected_bar = st.selectbox(
        "Select Bar",
        sorted(daily_data["Bar Name"].unique())
    )

with col2:
    available_brands = sorted(
        daily_data[
            daily_data["Bar Name"] == selected_bar
        ]["Brand Name"].unique()
    )

    selected_brand = st.selectbox(
        "Select Brand",
        available_brands
    )

filtered_data = daily_data[
    (daily_data["Bar Name"] == selected_bar)
    & (daily_data["Brand Name"] == selected_brand)
]

st.write(
    f"Daily consumption for **{selected_brand}** at **{selected_bar}**"
)

st.line_chart(
    filtered_data.set_index("Date")["Consumed (ml)"]
)

st.subheader("Inventory Recommendation")

selected_item = simulation_data[
    (simulation_data["Bar Name"] == selected_bar)
    & (simulation_data["Brand Name"] == selected_brand)
]

selected_par = train_stats[
    (train_stats["Bar Name"] == selected_bar)
    & (train_stats["Brand Name"] == selected_brand)
]

if not selected_item.empty and not selected_par.empty:
    par_level = selected_par["Recommended Par Level (ml)"].iloc[0]
    average_inventory = selected_item["Inventory"].mean()
    stockout_days = (selected_item["Inventory"] == 0).sum()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Recommended Par",
            f"{par_level:,.0f} ml"
        )

    with col2:
        st.metric(
            "Average Simulated Inventory",
            f"{average_inventory:,.0f} ml"
        )

    with col3:
        st.metric(
            "Simulated Stockout Days",
            int(stockout_days)
        )

    st.write(
        "Par level is calculated using a 3-day lead time and "
        "95% service-level safety stock based on training-period "
        "demand variability."
    )

st.subheader("Forecasting & Inventory Results")

st.dataframe(
    metrics_data,
    use_container_width=True
)

st.subheader("Stockout Analysis")

st.write(
    "Items with the highest number of simulated stockout days "
    "during the backtest period."
)

st.dataframe(
    stockout_data.head(10),
    use_container_width=True
)

st.subheader("Potential Overstock Analysis")

st.write(
    "Items with the highest number of days where observed closing "
    "inventory exceeded the recommended par level."
)

st.dataframe(
    overstock_data.head(10),
    use_container_width=True
)