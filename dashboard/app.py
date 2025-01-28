import streamlit as st
import pandas as pd
import plotly.express as px

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

# Mock data loading (replace with actual data)
@st.cache_data
def load_data():
    return pd.DataFrame({
        "Year": [1997, 1998, 1999, 2000],
        "Month": ["Jan", "Feb", "Mar", "Apr"],
        "State": ["SP", "RJ", "MG", "RS"],
        "Product": ["Pesticide A", "Herbicide B", "Chemical C", "Pesticide D"],
        "Transport_Mode": ["Sea", "Air", "Sea", "Land"],
        "Value_USD": [50000, 30000, 20000, 40000],
        "Weight_kg": [1000, 800, 500, 700],
    })

data = load_data()

# Filter options
years = st.sidebar.multiselect("Select Year(s):", options=data["Year"].unique(), default=data["Year"].unique())
transport_modes = st.sidebar.multiselect(
    "Select Transport Mode(s):", options=data["Transport_Mode"].unique(), default=data["Transport_Mode"].unique()
)

# Apply filters
filtered_data = data[data["Year"].isin(years)]
filtered_data = filtered_data[filtered_data["Transport_Mode"].isin(transport_modes)]

# Main visualization
st.subheader("Import Trends by Year")
fig_trend = px.line(
    filtered_data,
    x="Year",
    y="Value_USD",
    color="Transport_Mode",
    title="Yearly Import Values by Transport Mode",
    markers=True,
)
st.plotly_chart(fig_trend)

# Geographical analysis
st.subheader("Imports by State")
fig_geo = px.bar(
    filtered_data,
    x="State",
    y="Value_USD",
    color="State",
    title="Total Import Value by State",
)
st.plotly_chart(fig_geo)

# Product breakdown
st.subheader("Top Imported Products")
fig_products = px.pie(
    filtered_data,
    names="Product",
    values="Value_USD",
    title="Share of Import Value by Product",
)
st.plotly_chart(fig_products)

# Display raw data
st.subheader("Raw Data")
st.dataframe(filtered_data)
