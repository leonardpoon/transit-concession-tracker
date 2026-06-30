import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date as date_type
import sys
import os

sys.path.append(os.path.dirname(__file__))

from db.connection import get_connection
from db.queries import get_lifetime_summary, get_all_periods
from config import MONTHS, DEFAULT_CONCESSION_THRESHOLD
from utils import get_current_cycle


st.set_page_config(
    page_title="Transit Tracker Dashboard",
    page_icon="🚌",
    layout="wide",
)


# ── Concession period helpers ───────────────────────────────
# Cycle logic itself now lives in utils.get_current_cycle (shared with the
# CLI app), so the dashboard no longer keeps its own duplicate copy.

@st.cache_data(ttl=60)
def load_periods():
    return get_all_periods()


def threshold_for_date(d, periods):
    """Find (threshold, label) for whichever concession period covers date d."""
    for p in periods:  # get_all_periods() is already ordered start_date DESC
        if p["start_date"] <= d and (p["end_date"] is None or p["end_date"] >= d):
            return float(p["threshold_amount"]), p["label"]
    return DEFAULT_CONCESSION_THRESHOLD, None


# ── Data loading ───────────────────────────────────────────
@st.cache_data(ttl=60)
def load_all_trips():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, mode_of_transport, starting_location, "
        "ending_location, total_price, date "
        "FROM trips ORDER BY date ASC"
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    df = pd.DataFrame(rows)
    df["date"]        = pd.to_datetime(df["date"])
    df["year"]        = df["date"].dt.year
    df["month"]       = df["date"].dt.month
    df["month_name"]  = df["date"].dt.strftime("%b %Y")
    df["day"]         = df["date"].dt.date
    df["total_price"] = df["total_price"].astype(float)
    return df


@st.cache_data(ttl=60)
def load_lifetime_summary():
    return get_lifetime_summary()


# ── Header ─────────────────────────────────────────────────
st.title("🚌 Transit Tracker Dashboard")
st.caption("Personal Transit Tracker")

try:
    df = load_all_trips()
    lifetime = load_lifetime_summary()
    periods = load_periods()
except Exception as e:
    st.error(f"Cannot connect to MySQL: {e}")
    st.stop()

if df.empty:
    st.warning("No trip data found. Log some trips first!")
    st.stop()


# ── Sidebar ────────────────────────────────────────────────
st.sidebar.header("Filters")

years         = sorted(df["year"].unique(), reverse=True)
year_options  = ["All"] + [str(y) for y in years]
selected_year = st.sidebar.selectbox("Year", year_options)

selected_month_num = None

if selected_year == "All":
    df_year            = df.copy()
    selected_month_name = "All"
else:
    df_year = df[df["year"] == int(selected_year)]
    months_available    = sorted(df_year["month"].unique())
    month_names         = [MONTHS[m] for m in months_available]
    selected_month_name = st.sidebar.selectbox("Month", ["All"] + month_names)

    if selected_month_name != "All":
        selected_month_num = months_available[
            month_names.index(selected_month_name)
        ]
        df_year = df_year[df_year["month"] == selected_month_num]


df_filtered = df_year


# ── Current cycle panel ────────────────────────────────────
cycle_start, cycle_end, cycle_threshold, cycle_label = get_current_cycle()
cycle_str = (
    f"{cycle_start.strftime('%d %b')} — {cycle_end.strftime('%d %b %Y')}"
)

df_cycle = df[
    (df["date"].dt.date >= cycle_start) &
    (df["date"].dt.date <= cycle_end)
]

cycle_total   = df_cycle["total_price"].sum()
cycle_savings = cycle_total - cycle_threshold
cycle_pct     = min(cycle_total / cycle_threshold, 1.0) if cycle_threshold else 0

st.subheader(f"Current Cycle: {cycle_str}" + (f"  ({cycle_label})" if cycle_label else ""))
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Cycle Total",   f"${cycle_total:.2f}")
col2.metric(f"vs ${cycle_threshold:.2f} target", f"${cycle_savings:+.2f}",
            delta_color="normal" if cycle_savings >= 0 else "inverse")
col3.metric("Cycle Trips",   len(df_cycle))
col4.metric("Bus Trips",     len(df_cycle[df_cycle["mode_of_transport"] == "Bus"]))
col5.metric("Train Trips",   len(df_cycle[df_cycle["mode_of_transport"] == "Train"]))
st.progress(cycle_pct, text=f"${cycle_total:.2f} / ${cycle_threshold:.2f}")

st.divider()


# ── Lifetime summary ───────────────────────────────────────
st.subheader("Lifetime Summary")

total_spent   = float(lifetime["total_spent"] or 0)
total_trips   = int(lifetime["total_trips"]   or 0)
bus_count     = int(lifetime["bus_count"]      or 0)
train_count   = int(lifetime["train_count"]    or 0)
first_trip    = lifetime["first_trip"]
last_trip     = lifetime["last_trip"]

# Calculate months covered and total saved - each month judged against
# whichever concession threshold was actually active then. Note: this
# groups by calendar month (like the rest of the dashboard always has),
# not the 3rd/1st-to-2nd/end concession cycle - if a price change lands
# mid-month, the 1st-of-month lookup below may not perfectly match the
# cycle that was actually active for trips later in that month.
monthly_totals = (
    df.groupby(["year", "month"])["total_price"]
    .sum()
    .reset_index()
)
monthly_totals["threshold"] = monthly_totals.apply(
    lambda r: threshold_for_date(date_type(int(r["year"]), int(r["month"]), 1), periods)[0],
    axis=1,
)

months_tracked  = len(monthly_totals)
covered_mask    = monthly_totals["total_price"] >= monthly_totals["threshold"]
months_covered  = int(covered_mask.sum())
total_saved     = (
    monthly_totals.loc[covered_mask, "total_price"]
    - monthly_totals.loc[covered_mask, "threshold"]
).sum()
avg_per_month   = total_spent / months_tracked if months_tracked > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Spent",        f"${total_spent:.2f}")
col2.metric("Total Saved",        f"${total_saved:.2f}")
col3.metric("Months Covered",     f"{months_covered} / {months_tracked}")
col4.metric("Total Trips",        total_trips)
col5.metric("Avg per Month",      f"${avg_per_month:.2f}")

if first_trip and last_trip:
    st.caption(
        f"Tracking since **{first_trip.strftime('%d %b %Y')}** — "
        f"last trip **{last_trip.strftime('%d %b %Y')}**"
    )

st.divider()


# ── Selected period summary ────────────────────────────────
if selected_year == "All":
    period_label = "All Time"
elif selected_month_name == "All":
    period_label = str(selected_year)
else:
    period_label = f"{selected_month_name} {selected_year}"

st.subheader(f"Summary — {period_label}")

period_total  = df_filtered["total_price"].sum()
period_trips  = len(df_filtered)
period_buses  = len(df_filtered[df_filtered["mode_of_transport"] == "Bus"])
period_trains = len(df_filtered[df_filtered["mode_of_transport"] == "Train"])

if selected_year != "All" and selected_month_name != "All" and selected_month_num is not None:
    # Single specific month selected - exact threshold for that month.
    period_threshold, period_period_label = threshold_for_date(
        date_type(int(selected_year), int(selected_month_num), 1), periods
    )
    approx_note = None
else:
    # Selection spans multiple months/years where the threshold may have
    # changed - comparing a multi-month sum against one threshold isn't
    # fully meaningful anyway, so just use today's rate as a reference.
    period_threshold = cycle_threshold
    approx_note = "Selection spans multiple months - shown against today's threshold for reference."

period_savings = period_total - period_threshold

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Spent",   f"${period_total:.2f}")
col2.metric(f"vs ${period_threshold:.2f} target", f"${period_savings:+.2f}",
            delta_color="normal" if period_savings >= 0 else "inverse")
col3.metric("Total Trips",   period_trips)
col4.metric("Bus Trips",     period_buses)
col5.metric("Train Trips",   period_trains)
if approx_note:
    st.caption(approx_note)

st.divider()


# ── Monthly spending bar chart ─────────────────────────────
if selected_year == "All":
    st.subheader("Monthly Spending — All Years")
    monthly = (
        df.groupby(["year", "month"])["total_price"]
        .sum()
        .reset_index()
    )
    monthly["label"] = monthly.apply(
        lambda r: f"{MONTHS[int(r['month'])]} {int(r['year'])}", axis=1
    )
    monthly["threshold"] = monthly.apply(
        lambda r: threshold_for_date(date_type(int(r["year"]), int(r["month"]), 1), periods)[0],
        axis=1,
    )
    monthly = monthly.sort_values(["year", "month"])

    fig_monthly = px.bar(
        monthly,
        x="label",
        y="total_price",
        color="year",
        labels={"total_price": "Amount ($)", "label": "Month", "year": "Year"},
        height=400,
    )
    fig_monthly.add_trace(go.Scatter(
        x=monthly["label"],
        y=monthly["threshold"],
        mode="lines",
        line=dict(dash="dash", color="orange", shape="hv"),
        name="Threshold",
    ))
else:
    st.subheader(f"Monthly Spending — {selected_year}")
    monthly = (
        df[df["year"] == int(selected_year)]
        .groupby(["month", "month_name"])["total_price"]
        .sum()
        .reset_index()
        .sort_values("month")
    )
    monthly["threshold"] = monthly["month"].apply(
        lambda m: threshold_for_date(date_type(int(selected_year), int(m), 1), periods)[0]
    )

    fig_monthly = go.Figure()
    fig_monthly.add_trace(go.Bar(
        x=monthly["month_name"],
        y=monthly["total_price"],
        marker_color=[
            "#2ecc71" if v >= t else "#e74c3c"
            for v, t in zip(monthly["total_price"], monthly["threshold"])
        ],
        name="Spending",
    ))
    fig_monthly.add_trace(go.Scatter(
        x=monthly["month_name"],
        y=monthly["threshold"],
        mode="lines",
        line=dict(dash="dash", color="orange", shape="hv"),
        name="Threshold",
    ))
    fig_monthly.update_layout(
        xaxis_title="Month",
        yaxis_title="Amount ($)",
        showlegend=True,
        height=400,
    )

st.plotly_chart(fig_monthly, width='stretch')
st.caption("Dashed line shows the concession threshold active in each month.")
st.divider()


# ── Bus vs Train + Daily spending ─────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Bus vs Train")
    mode_counts = df_filtered["mode_of_transport"].value_counts()
    fig_pie = px.pie(
        values=mode_counts.values,
        names=mode_counts.index,
        color=mode_counts.index,
        color_discrete_map={"Bus": "#2ecc71", "Train": "#e74c3c"},
        hole=0.4,
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


# ── Top routes ─────────────────────────────────────────────
st.subheader(f"Top 10 Most Frequent Routes — {period_label}")
df_filtered["route"] = (
    df_filtered["starting_location"] + " → " + df_filtered["ending_location"]
)
top_routes = (
    df_filtered.groupby(["route", "mode_of_transport"])
    .agg(count=("route", "count"), avg_fare=("total_price", "mean"))
    .reset_index()
    .sort_values("count", ascending=False)
    .head(10)
)
fig_routes = px.bar(
    top_routes,
    x="count",
    y="route",
    color="mode_of_transport",
    orientation="h",
    color_discrete_map={"Bus": "#2ecc71", "Train": "#e74c3c"},
    labels={"count": "Trips", "route": "Route", "mode_of_transport": "Mode"},
)
fig_routes.update_layout(height=400, yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig_routes, width='stretch')

st.divider()


# ── Year over year ─────────────────────────────────────────
st.subheader("Year-over-Year Monthly Spending")
yoy = (
    df.groupby(["year", "month"])["total_price"]
    .sum()
    .reset_index()
)
fig_yoy = px.line(
    yoy,
    x="month",
    y="total_price",
    color="year",
    markers=True,
    labels={"total_price": "Amount ($)", "month": "Month", "year": "Year"},
)
# No single threshold line here on purpose - the threshold has changed
# over time (see caption below), so one flat line would misrepresent
# earlier months.
fig_yoy.update_xaxes(
    tickvals=list(range(1, 13)),
    ticktext=[MONTHS[m] for m in range(1, 13)],
)
fig_yoy.update_layout(height=400)
st.plotly_chart(fig_yoy, width='stretch')

period_summary_lines = []
for p in sorted(periods, key=lambda p: p["start_date"]):
    end_str = p["end_date"].strftime("%d %b %Y") if p["end_date"] else "now"
    line = f"${float(p['threshold_amount']):.2f} from {p['start_date'].strftime('%d %b %Y')} to {end_str}"
    if p["label"]:
        line += f" ({p['label']})"
    period_summary_lines.append(line)
st.caption("Concession threshold over time: " + " · ".join(period_summary_lines))

st.divider()


# ── Raw data ───────────────────────────────────────────────
with st.expander("View raw trip data"):
    st.dataframe(
        df_filtered[[
            "id", "mode_of_transport", "starting_location",
            "ending_location", "total_price", "date"
        ]].rename(columns={
            "id":                "ID",
            "mode_of_transport": "Mode of Transport",
            "starting_location": "From",
            "ending_location":   "To",
            "total_price":       "Price ($)",
            "date":              "Date",
        }),
        width='stretch',
        hide_index=True,
    )