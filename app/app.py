import pandas as pd
import streamlit as st
import plotly.express as px

# Page settings
st.set_page_config(page_title="Energy Burden Dashboard", layout="wide")

st.title("Energy Burden Trends in the United States")
st.write(
    """
    This dashboard shows trends in energy-related CPI measures,
    unemployment, and related indicators to support future analysis
    of energy burden among U.S. households.
    """
)

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("data/bls_monthly.csv", parse_dates=["date"])

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")

series_options = df["series_name"].unique()
selected_series = st.sidebar.multiselect(
    "Select data series:",
    options=series_options,
    default=list(series_options[:2])
)

filtered = df[df["series_name"].isin(selected_series)]

# Line chart
fig = px.line(
    filtered,
    x="date",
    y="value",
    color="series_name",
    title="Monthly Trends"
)

st.plotly_chart(fig, use_container_width=True)

# Show data table
with st.expander("View underlying data"):
    st.dataframe(filtered.sort_values("date", ascending=False))
