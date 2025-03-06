import streamlit as st
import pandas as pd
import numpy as np

import comexstat_viz.fetch_data as cfd
import comexstat_viz.dashboard.plots as cvdp


DT_KEY = "dt"
VALUE_KEY = "net_weight_kg"
PRODUCT_CLASS_KEY = "class"
COUNTRY_CODE_KEY = "export_country_code"

ROLLING_AVG_WINDOW_IN_MONTHS = 12

LABEL_TO_COLOR_MAP = {
    "is_herbicide": "lightgreen",
    "is_fungicide": "rebeccapurple",
    "is_inseticide": "tomato",
    "is_domissanitario": "teal",
}

# Title and description
st.title("Brazil's Pesticide Importation")
st.write(
    """
    This dashboard provides an interactive view of Brazil's importation records for pesticides, 
    herbicides, and other agricultural chemicals from 1997 to 2024. 
    Explore trends, geographical distribution, and insights into imported products.
    """
)

#
##
### load data
##
#


@st.cache_data
def load_raw_data():
    return cfd.create_denfensivos_agricolas_df()


data = load_raw_data()


@st.cache_data
def melt_data(df: pd.DataFrame):
    return cfd.melt_and_group_by_classes_and_dt(df)


melted_grouped_data = melt_data(data)


@st.cache_data
def load_seasonal_decompose_data(df: pd.DataFrame):
    return cfd.seasonal_decompose_pesticide_import_data(df)


seasonal_data_object = load_seasonal_decompose_data(data)


#
##
### Filter options
##
#

st.sidebar.header("Filters")

min_date = np.array(data[DT_KEY].dt.to_pydatetime()).min()
max_date = np.array(data[DT_KEY].dt.to_pydatetime()).max()

selected_dates = st.sidebar.slider(
    "Select Date Range:",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),  # Default range
    format="MM/DD/YYYY",  # Customize date format if needed
)
start_dt, end_dt = selected_dates[0], selected_dates[1]

# Apply filters
filtered_data = data[(data[DT_KEY] >= start_dt) & (data[DT_KEY] <= end_dt)]
filtered_melted_grouped_data = melted_grouped_data[
    (melted_grouped_data[DT_KEY] >= start_dt) & (melted_grouped_data[DT_KEY] <= end_dt)
]
filtered_seasonal = seasonal_data_object.seasonal.loc[start_dt:end_dt]
filtered_residual = seasonal_data_object.resid.loc[start_dt:end_dt]
filtered_trend = seasonal_data_object.trend.loc[start_dt:end_dt]

if filtered_data.empty:
    st.warning("No data found for selected filters!")
    st.stop()


#
##
### Main visualization
##
#

### Sidebar
st.sidebar.header("Total Import:")
total_weight_in_kg = filtered_melted_grouped_data[VALUE_KEY].sum()
weight_in_units_of_blue_whales = int(total_weight_in_kg / 1e3 / 150 / 1e3) * int(1e3)  # TODO why i did this?
weight_in_units_of_loaded_747_planes = int(total_weight_in_kg / 1e3 / 400 / 1e3) * int(1e3)

if total_weight_in_kg > 1e9:
    display = (total_weight_in_kg / 1e9).round(1)
    st.sidebar.metric(label="Weight", value=f"{display} Billion kg")
else:
    display = (total_weight_in_kg / 1e6).round(1)
    st.sidebar.metric(label="Weight", value=f"{display} Million kg")
st.sidebar.text(f"That's equivalent to {weight_in_units_of_blue_whales} blue whales, or {weight_in_units_of_loaded_747_planes} loaded Boeing 747s")

## trend plot
st.subheader("Import Trends by Year")
fig_trend = cvdp.plot_trend_with_bar(
    data=filtered_melted_grouped_data,
    x_key=DT_KEY,
    y_key=VALUE_KEY,
    trend_arr=filtered_trend,
    color_key=PRODUCT_CLASS_KEY,
    color_map=LABEL_TO_COLOR_MAP,
)
st.plotly_chart(fig_trend)

st.write(
    """
    "Domissanitário" category refers to products destinated to household use
    """
)

## seasonal plot
st.subheader("Sazonality effect on imports")
fig_seasonal = cvdp.plot_seasonal_decompose(
    filtered_seasonal, 
    filtered_residual
)
st.plotly_chart(fig_seasonal)

## geographical plot
st.subheader("Exports by Country")
_filter_br_cond = filtered_data[COUNTRY_CODE_KEY] != "BRA"
sum_by_country_df = (
    filtered_data[_filter_br_cond]
    .groupby(COUNTRY_CODE_KEY)[VALUE_KEY]
    .sum()
    .reset_index()
)

fig_geo = cvdp.plot_choropleth(
    data=sum_by_country_df,
    country_code_key=COUNTRY_CODE_KEY,
    value_key=VALUE_KEY,
)
st.plotly_chart(fig_geo)

## product classes plot
sum_by_class_df = (
    filtered_melted_grouped_data.groupby(PRODUCT_CLASS_KEY)[VALUE_KEY]
    .sum()
    .reset_index()
)
st.subheader("Share of Imported Product Classes")
fig_products = cvdp.plot_bar_by_class(
    sum_by_class_df,
    x_key=PRODUCT_CLASS_KEY,
    y_key=VALUE_KEY,
    color_key=PRODUCT_CLASS_KEY,
    color_map=LABEL_TO_COLOR_MAP,
    title=None,
)
st.plotly_chart(fig_products)


# display raw data
st.subheader("Raw Data")
st.dataframe(filtered_data)


# download raw data
st.download_button(
    "Download Filtered Data",
    filtered_data.to_csv(index=False),
    file_name="filtered_data.csv",
)
