import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import sys
import os

sys.path.append(os.path.dirname(__file__))

from db.connection import get_connection
from config import CONCESSION_THRESHOLD, MONTHS


st.set_page_config(
    page_title = "Transit Tracker Dashboard",
    page_icon = "🚌",
    layout = "wide",
)

@st.cache_data(ttl = 60)
def load_all_trips():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, mode_of_transport, starting_location," 
        "ending_location, total_price, date " 
        "FROM trips ORDER BY date ASC"
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%b %Y")
    df["day"] = df["date"].dt.date
    df["total_price"] = df["total_price"].astype(float)
    return df

st.title("🚌 Transit Tracker Dashboard")
st.caption("Personal Transit Tracker")

try:
    df = load_all_trips()
except Exception as e:
    st.error(f"Cannot connect to MySQL: {e}")
    st.stop()

if df.empty:
    st.warning("No trip data found. Log some trips first!")
    st.stop()

st.sidebar.header("Filters")

years = sorted(df["year"].unique(), reverse=True)
selected_year = st.sidebar.selectbox("Year", years)

df_year = df[df["year"] == selected_year]

months_available = sorted(df_year["month"].unique())
month_names = [MONTHS[m] for m in months_available]
selected_month_name = st.sidebar.selectbox("Month", ["All"] + month_names)

if selected_month_name != "All":
    selected_month = months_available[month_names.index(selected_month_name)]
    df_filtered = df_year[df_year["month"] == selected_month]
else:
    df_filtered = df_year

st.subheader(f"Summary — {selected_month_name} {selected_year}")

total_spent = df_filtered["total_price"].sum()
total_trips = len(df_filtered)
bus_trips = len(df_filtered[df_filtered["mode_of_transport"] == "Bus"])
train_trips = len(df_filtered[df_filtered["mode_of_transport"] == "Train"])
savings = total_spent - CONCESSION_THRESHOLD

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Spent", f"\t${total_spent:.2f}")
col2.metric("Savings", f"\t${savings:.2f}", delta_color="normal" if savings >= 0 else "inverse")
col3.metric("Total Trips", total_trips)
col4.metric("Bus Trips", bus_trips)
col5.metric("Train Trips", train_trips)

st.divider()

st.subheader(f"Monthly Spending — {selected_year}")

monthly = (
    df_year.groupby(["month", "month_name"])["total_price"]
    .sum()
    .reset_index()
    .sort_values("month")
)

fig_monthly = go.Figure()

fig_monthly.add_trace(go.Bar(
    x=monthly["month_name"],
    y=monthly["total_price"],
    name="Total Spent",
    marker_color=[
        "#2ecc71" if v >= CONCESSION_THRESHOLD else "#e74c3c"
        for v in monthly["total_price"]
    ],
))

fig_monthly.add_hline(
    y=CONCESSION_THRESHOLD,
    line_dash="dash",
    line_color="orange",
    annotation_text=f"${CONCESSION_THRESHOLD:.2f} Concession Threshold",
    annotation_position="top right",
)

fig_monthly.update_layout(
    xaxis_title="Month",
    yaxis_title="Amount ($)",
    showlegend=False,
    height = 400,
)

st.plotly_chart(fig_monthly, width='stretch')
st.divider()

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Bus vs Train")
    mode_counts = df_filtered["mode_of_transport"].value_counts()
    fig_pie = px.pie(
        values = mode_counts.values,
        names = mode_counts.index,
        color = mode_counts.index,
        color_discrete_map={"Bus": "#2ecc71", "Train": "#e74c3c"},
        hole = 0.4
    )
    fig_pie.update_layout(height=350)
    st.plotly_chart(fig_pie, width='stretch')

with col_right:
    st.subheader("Daily Spending")
    daily = (
        df_filtered.groupby("day")["total_price"]
        .sum()
        .reset_index()
    )
    daily["day"] = pd.to_datetime(daily["day"])
    fig_daily = px.bar(
        daily,
        x="day",
        y="total_price",
        labels={"day": "Date", "total_price": "Amount ($)"},
        color_discrete_sequence=["#3498db"],
    )
    fig_daily.update_layout(height=350)
    st.plotly_chart(fig_daily, width='stretch')

st.divider()

st.subheader("Top 10 Most Frequent Routes")
df_filtered["route"] = (
    df_filtered["starting_location"] + " → " + df_filtered["ending_location"]
)

top_routes = (
    df_filtered.groupby(["route", "mode_of_transport"])
    .agg(count = ("route", "count"), avg_fare = ("total_price", "mean"))
    .reset_index()
    .sort_values("count", ascending=False)
    .head(10)
)

fig_routes = px.bar(
    top_routes,
    x="route",
    y="count",
    color="mode_of_transport",
    orientation="h",
    color_discrete_map={"Bus": "#2ecc71", "Train": "#e74c3c"},
    labels={"count": "Trips", "route": "Route", "mode_of_transport": "Mode"},
)
fig_routes.update_layout(height=400, yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig_routes, width='stretch')

st.divider()

st.subheader("Year-over-Year Monthly Spending")

yoy = (
    df.groupby(["year", "month"])["total_price"]
    .sum()
    .reset_index()
)

yoy["month_label"] = yoy["month"].apply(lambda m: MONTHS[m])

fig_yoy = px.line(
    yoy,
    x="month",
    y="total_price",
    color = "year",
    markers=True,
    labels = {"total_price": "Amount ($)", "month": "Month", "year": "Year"},
)

fig_yoy.add_hline(
    y=CONCESSION_THRESHOLD,
    line_dash="dash",
    line_color="orange",
    annotation_text=f"${CONCESSION_THRESHOLD:.2f} Threshold",
)

fig_yoy.update_xaxes(
    tickvals=list(range(1, 13)),
    ticktext=[MONTHS[m] for m in range(1, 13)],
)

fig_yoy.update_layout(height=400)
st.plotly_chart(fig_yoy, width='stretch')

st.divider()

with st.expander("View raw trip data"):
    st.dataframe(
        df_filtered[[
            "id", "mode_of_transport", "starting_location",
            "ending_location", "total_price", "date"
        ]].rename(columns={
            "id": "ID",
            "mode_of_transport": "Mode of Transport",
            "starting_location": "From",
            "ending_location": "To",
            "total_price": "Price ($)",
            "date": "Date",
        }),
        width='stretch',
        hide_index=True,
    )