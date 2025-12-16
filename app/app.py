import streamlit as st
import pandas as pd
import numpy as np

import plotly.graph_objects as go
from plotly.subplots import make_subplots



# Page settings
st.set_page_config(
    page_title="Energy Burden Trends in the United States",
    layout="wide"
)

st.title("Energy Burden Trends in the United States")



# Load data
@st.cache_data
def load_data(path="data/bls_monthly.csv"):
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()


# Remove household cost series
df = df[~df["category"].isin(["household_costs"])].copy()



# Calculations
def add_mom_yoy(group):
    group = group.sort_values("date").copy()
    group["mom_pct"] = group["value"].pct_change() * 100
    group["yoy_pct"] = group["value"].pct_change(12) * 100
    return group

df = df.groupby("series_name", group_keys=False).apply(add_mom_yoy)

# Latest observation per series
latest = df.sort_values("date").groupby("series_name").tail(1)



# Layout: LEFT = controls + indicators, RIGHT = charts
left_col, right_col = st.columns([1, 3])


# --------------------------------------------
# LEFT COLUMN — DATE SLIDER + INDICATORS
# --------------------------------------------
with left_col:

    # --------- Date Slider ---------
    st.subheader("Date Range")

    min_date = df["date"].min()
    max_date = df["date"].max()

    start_date, end_date = st.slider(
        "Select date range",
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        value=(min_date.to_pydatetime(), max_date.to_pydatetime()),
    )

    st.divider()

    # --------- Most Recent Indicators ---------
    st.subheader("Most Recent Indicators")

    for row in latest.itertuples(index=False):
        value = row.value
        mom = row.mom_pct
        yoy = row.yoy_pct
        units = row.units

        # Special labeling improvement for employment
        label = row.series_name
        if "Nonfarm" in row.series_name or "nonfarm" in row.series_name:
            label = f"Total Non-Farm Employment ({units})"

        st.metric(
            label=label,
            value=f"{value:.2f}",
            delta=None if pd.isna(mom) else f"{mom:.2f}% MoM",
        )

        st.caption("YoY: N/A" if pd.isna(yoy) else f"YoY: {yoy:.2f}%")



# Apply date filter
df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

energy_df = df[df["category"] == "energy_services"]
infl_unemp_df = df[df["category"].isin(["inflation_context", "unemployment"])]



# --------------------------------------------
# RIGHT COLUMN — STACKED CHARTS
# --------------------------------------------
with right_col:

   
    # Chart 1: Energy Services
    
    st.subheader("Energy Services Trends")

    fig_energy = go.Figure()

    for name in energy_df["series_name"].unique():
        s = energy_df[energy_df["series_name"] == name]
        fig_energy.add_trace(
            go.Scatter(
                x=s["date"],
                y=s["value"],
                mode="lines",
                name=name
            )
        )

    fig_energy.update_layout(
        xaxis_title="Date",
        yaxis_title="Index Level",
        hovermode="x unified"
    )

    st.plotly_chart(fig_energy, use_container_width=True)



   
    # Chart 2: Inflation  & Unemployment
   
    st.subheader("Inflation & Unemployment Trends")

    fig_combo = make_subplots(specs=[[{"secondary_y": True}]])

    for name in infl_unemp_df["series_name"].unique():
        s = infl_unemp_df[infl_unemp_df["series_name"] == name]
        is_unemp = s["category"].iloc[0] == "unemployment"

        fig_combo.add_trace(
            go.Scatter(
                x=s["date"],
                y=s["value"],
                mode="lines",
                name=name
            ),
            secondary_y=is_unemp
        )

    fig_combo.update_layout(
        xaxis_title="Date",
        hovermode="x unified"
    )

    fig_combo.update_yaxes(
        title_text="CPI Index",
        secondary_y=False
    )
    fig_combo.update_yaxes(
        title_text="Percent",
        secondary_y=True
    )

    st.plotly_chart(fig_combo, use_container_width=True)



# Explanation
st.divider()

st.write(
    """
    **Understanding this dashboard:**

    - The **Energy Services chart** shows trends in electricity and natural gas prices.
    - The **Inflation & Unemployment chart** shows how overall CPI and unemployment move over time.
    - The format allows you to visually compare changes in energy costs alongside broader economic conditions.

    The added **Total Non-Farm Employment** indicator helps provide context on labor market strength,
    supporting future study on how employment levels may relate to energy burden.
    """
)


# Footer
st.caption(
    "Source: U.S. Bureau of Labor Statistics (BLS). "
    "Data updated automatically via GitHub Actions."
)
