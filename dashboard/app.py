import sys
from pathlib import Path

project_path = Path().resolve().parent
sys.path.append(str(project_path))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import fetch_data as fd

DT_KEY = "dt"
VALUE_KEY = "net_weight_kg"
PRODUCT_CLASS_KEY = "class"
COUNTRY_CODE_KEY = "export_country_code"

ROLLING_AVG_WINDOW_IN_MONTHS = 12

# Title and description
st.title("Brazil Pesticide Importation Dashboard")
st.write(
    """
    This dashboard provides an interactive view of Brazil's importation records for pesticides, 
    herbicides, and other agricultural chemicals from 1997 to 2024. 
    Explore trends, geographical distribution, and insights into imported products.
    """
)

# Sidebar for user inputs
st.sidebar.header("Filters")


# load data
@st.cache_data
def load_data():
    return fd.create_denfensivos_agricolas_df()


data = load_data()


def melt_data(df: pd.DataFrame):
    return fd.melt_and_group_by_classes_and_dt(data)


melted_grouped_data = melt_data(data)

# Filter options
min_date = data[DT_KEY].dt.to_pydatetime().min()  # to_pydatetime is deprecated
max_date = data[DT_KEY].dt.to_pydatetime().max()

selected_dates = st.sidebar.slider(
    "Select Date Range:",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),  # Default range
    format="MM/DD/YYYY",  # Customize date format if needed
)
# Apply filters
filtered_data = data[
    (data[DT_KEY] >= selected_dates[0]) & (data[DT_KEY] <= selected_dates[1])
]
filtered_melted_grouped_data = melted_grouped_data[
    (melted_grouped_data[DT_KEY] >= selected_dates[0])
    & (melted_grouped_data[DT_KEY] <= selected_dates[1])
]
if filtered_data.empty:
    st.warning("No data found for selected filters!")
    st.stop()

### Main visualization

## moving avg as trend
sum_df = filtered_melted_grouped_data[[DT_KEY, VALUE_KEY]].groupby(DT_KEY).sum()
sum_df = sum_df.sort_index()
moving_avg_df = sum_df.rolling(window=ROLLING_AVG_WINDOW_IN_MONTHS).mean()
moving_avg_sr = moving_avg_df["net_weight_kg"]

## plot
st.subheader("Import Trends by Year")
fig_trend = px.bar(
    filtered_melted_grouped_data, x=DT_KEY, y=VALUE_KEY, color=PRODUCT_CLASS_KEY
)

# add trendline
fig_trend.add_trace(
    go.Scatter(
        x=moving_avg_sr.index,  # Use the same x-axis values as the bar plot
        y=moving_avg_sr.values,  # Use the same y-axis values or a different column for the line
        mode="lines",  # Display as a line with markers
        name="12m Rolling Avg.",  # Name for the legend
        line=dict(color="saddlebrown", width=2.5),  # Customize the line color and width
    )
)

# layout
fig_trend.update_layout(
    xaxis_title="Date",
    yaxis_title="Net Weight (kg)",
    colorway=px.colors.qualitative.Dark24
)

st.plotly_chart(fig_trend)

# # Geographical plot
sum_by_country_df = (
    filtered_data.groupby(COUNTRY_CODE_KEY)[VALUE_KEY].sum().reset_index()
)
sum_by_country_df = sum_by_country_df[sum_by_country_df[COUNTRY_CODE_KEY] != "BRA"]
st.subheader("Exports by Country")
fig_geo = px.choropleth(
    sum_by_country_df,
    locations=COUNTRY_CODE_KEY,
    locationmode="ISO-3",
    color=VALUE_KEY,
    hover_name=COUNTRY_CODE_KEY,
    color_continuous_scale="Plasma",
    range_color=(sum_by_country_df[VALUE_KEY].min(), sum_by_country_df[VALUE_KEY].max()),
    title="Export Net Weight per Country",
)
st.plotly_chart(fig_geo)

# # Product classes
sum_by_class_df = (
    filtered_melted_grouped_data.groupby(PRODUCT_CLASS_KEY)[VALUE_KEY]
    .sum()
    .reset_index()
)
st.subheader("Share of Imported Product Classes")
fig_products = px.bar(
    sum_by_class_df,
    x=PRODUCT_CLASS_KEY,
    y=VALUE_KEY,
    color=PRODUCT_CLASS_KEY,
    title="Share of Imports by Product Class",
)
st.plotly_chart(fig_products)

# display raw data
st.subheader("Raw Data")
st.dataframe(filtered_data)

# download raw data
st.sidebar.download_button(
    "Download Filtered Data",
    filtered_data.to_csv(index=False),
    file_name="filtered_data.csv"
)
