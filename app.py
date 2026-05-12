import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(layout="wide")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
df = pd.read_excel("Dashboard Raw OC.xlsx", engine="openpyxl")

# Clean + prepare
df['Total TEUs'] = pd.to_numeric(df['Total TEUs'], errors='coerce').fillna(0)
df['ATA/ETA'] = pd.to_datetime(df['ATA/ETA'], errors='coerce')
df['Month'] = df['ATA/ETA'].dt.to_period('M').astype(str)
df['Tradelane'] = df['First Load Country'] + " → " + df['Last Disch. Country']

# --------------------------------------------------
# SIDEBAR FILTER
# --------------------------------------------------
st.sidebar.header("Filters")

months = sorted(df['Month'].dropna().unique())

selected_months = st.sidebar.multiselect(
    "Select Month",
    options=months,
    default=months
)

filtered_df = df[df['Month'].isin(selected_months)]

# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------
page = st.sidebar.radio("Navigation", [
    "Executive Summary",
    "Top Customers",
    "Tradelane Analysis"
])

# --------------------------------------------------
# PAGE 1 - EXECUTIVE SUMMARY
# --------------------------------------------------
if page == "Executive Summary":

    st.title("📊 Global Ocean Container Overview")

    total = int(filtered_df['Total TEUs'].sum())
    imp = int(filtered_df[filtered_df['Job Direction'] == 'Import']['Total TEUs'].sum())
    exp = int(filtered_df[filtered_df['Job Direction'] == 'Export']['Total TEUs'].sum())
    other = int(filtered_df[filtered_df['Job Direction'] == 'Other']['Total TEUs'].sum())

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total TEUs", f"{total:,}")
    col2.metric("Import", f"{imp:,}")
    col3.metric("Export", f"{exp:,}")
    col4.metric("Crosstrade", f"{other:,}")

    st.markdown("---")

    monthly = filtered_df.groupby(
        ['Month', 'Job Direction']
    )['Total TEUs'].sum().reset_index()

    fig = px.bar(
        monthly,
        x="Month",
        y="Total TEUs",
        color="Job Direction",
        barmode="group"
    )

    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# PAGE 2 - TOP CUSTOMERS
# --------------------------------------------------
elif page == "Top Customers":

    st.title("🏆 Top Customers")

    cust = filtered_df.groupby(
        ['Consignee Name', 'Job Direction']
    )['Total TEUs'].sum().reset_index()

    fig = px.bar(
        cust.sort_values("Total TEUs", ascending=False).head(15),
        x="Total TEUs",
        y="Consignee Name",
        color="Job Direction",
        orientation="h"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Detailed Breakdown")

    table = cust.pivot_table(
        index="Consignee Name",
        columns="Job Direction",
        values="Total TEUs",
        aggfunc="sum"
    ).fillna(0)

    table['Total'] = table.sum(axis=1)

    st.dataframe(table.sort_values("Total", ascending=False).head(20))

# --------------------------------------------------
# PAGE 3 - TRADELANE ANALYSIS
# --------------------------------------------------
elif page == "Tradelane Analysis":

    st.title("🌍 Tradelane Analysis")

    direction = st.radio(
        "Select Trade Type",
        ["Import", "Export", "Other"]
    )

    lane = filtered_df[filtered_df['Job Direction'] == direction]

    lane_summary = lane.groupby('Tradelane')['Total TEUs'].sum().reset_index()

    fig = px.bar(
        lane_summary.sort_values("Total TEUs", ascending=True).tail(15),
        x="Total TEUs",
        y="Tradelane",
        orientation="h"
    )

    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.markdown("DSV Confidential Dashboard")
