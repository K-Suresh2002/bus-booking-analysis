import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(
    page_title="Bus Booking Analysis",
    page_icon="🚌",
    layout="wide"
)

st.title("🚌 Bus Booking Analysis Dashboard")
st.write("Interactive analysis of simulated bus booking data using Python, SQL and SQLite.")

# Create / load database
conn = sqlite3.connect("bus_bookings.db")

# KPI calculations
total_bookings = pd.read_sql_query(
    "SELECT COUNT(*) AS total FROM bookings",
    conn
).iloc[0]["total"]

confirmed_bookings = pd.read_sql_query(
    "SELECT COUNT(*) AS total FROM bookings WHERE status='CONFIRMED'",
    conn
).iloc[0]["total"]

cancelled_bookings = pd.read_sql_query(
    "SELECT COUNT(*) AS total FROM bookings WHERE status='CANCELLED'",
    conn
).iloc[0]["total"]

cancel_rate = round((cancelled_bookings / total_bookings) * 100, 1)

# KPI cards
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Bookings", f"{total_bookings:,}")
col2.metric("Confirmed Bookings", f"{confirmed_bookings:,}")
col3.metric("Cancelled Bookings", f"{cancelled_bookings:,}")
col4.metric("Cancellation Rate", f"{cancel_rate}%")

st.divider()

# Route occupancy
st.subheader("📊 Seat Occupancy by Route")

occupancy_query = """
SELECT
    r.origin || ' → ' || r.destination AS route,
    ROUND(
        100.0 * COUNT(b.booking_id) /
        (COUNT(DISTINCT s.schedule_id) * 40),
        1
    ) AS occupancy_pct
FROM routes r
JOIN schedules s
    ON s.route_id = r.route_id
LEFT JOIN bookings b
    ON b.schedule_id = s.schedule_id
    AND b.status = 'CONFIRMED'
GROUP BY r.route_id
ORDER BY occupancy_pct DESC
"""

occupancy = pd.read_sql_query(occupancy_query, conn)

st.bar_chart(
    occupancy.set_index("route")["occupancy_pct"]
)

st.dataframe(
    occupancy,
    use_container_width=True,
    hide_index=True
)

# Revenue
st.subheader("💰 Revenue by Route")

revenue_query = """
SELECT
    r.origin || ' → ' || r.destination AS route,
    SUM(r.fare) AS revenue
FROM bookings b
JOIN schedules s
    ON s.schedule_id = b.schedule_id
JOIN routes r
    ON r.route_id = s.route_id
WHERE b.status = 'CONFIRMED'
GROUP BY r.route_id
ORDER BY revenue DESC
"""

revenue = pd.read_sql_query(revenue_query, conn)

st.bar_chart(
    revenue.set_index("route")["revenue"]
)

st.dataframe(
    revenue,
    use_container_width=True,
    hide_index=True
)

# Weekday bookings
st.subheader("📅 Confirmed Bookings by Weekday")

weekday_query = """
SELECT
    CASE strftime('%w', s.travel_date)
        WHEN '0' THEN 'Sunday'
        WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday'
        WHEN '6' THEN 'Saturday'
    END AS weekday,
    COUNT(*) AS bookings
FROM bookings b
JOIN schedules s
    ON s.schedule_id = b.schedule_id
WHERE b.status = 'CONFIRMED'
GROUP BY strftime('%w', s.travel_date)
ORDER BY strftime('%w', s.travel_date)
"""

weekday = pd.read_sql_query(weekday_query, conn)

st.bar_chart(
    weekday.set_index("weekday")["bookings"]
)

# Monthly trend
st.subheader("📈 Monthly Booking Trend")

monthly_query = """
WITH monthly AS (
    SELECT
        strftime('%Y-%m', s.travel_date) AS month,
        COUNT(*) AS bookings
    FROM bookings b
    JOIN schedules s
        ON s.schedule_id = b.schedule_id
    WHERE b.status = 'CONFIRMED'
    GROUP BY 1
)
SELECT
    month,
    bookings,
    SUM(bookings) OVER (
        ORDER BY month
    ) AS running_total
FROM monthly
"""

monthly = pd.read_sql_query(monthly_query, conn)

st.line_chart(
    monthly.set_index("month")[["bookings", "running_total"]]
)

st.subheader("Monthly Data")
st.dataframe(
    monthly,
    use_container_width=True,
    hide_index=True
)

conn.close()

st.divider()

st.caption(
    "Dataset is simulated using Python with random seed 42. "
    "Analysis uses SQLite SQL queries."
)