"""
Bus Booking Analysis (SQL + Python)
Generates a SIMULATED bus-booking dataset in SQLite, then answers business
questions with SQL (joins, aggregations, CTEs, window functions).
Data is simulated (seed=42). To use real data, point the queries at your own MySQL DB.
Run:  python bus_booking_analysis.py
"""
import sqlite3, random
from datetime import date, timedelta

random.seed(42)
con = sqlite3.connect("bus_bookings.db")
cur = con.cursor()
cur.executescript("""
DROP TABLE IF EXISTS bookings; DROP TABLE IF EXISTS schedules; DROP TABLE IF EXISTS routes;
CREATE TABLE routes(route_id INTEGER PRIMARY KEY, origin TEXT, destination TEXT, fare INTEGER);
CREATE TABLE schedules(schedule_id INTEGER PRIMARY KEY, route_id INTEGER, travel_date TEXT, seats INTEGER,
                       FOREIGN KEY(route_id) REFERENCES routes(route_id));
CREATE TABLE bookings(booking_id INTEGER PRIMARY KEY, schedule_id INTEGER, seat_no INTEGER, status TEXT,
                      booked_on TEXT, UNIQUE(schedule_id, seat_no),
                      FOREIGN KEY(schedule_id) REFERENCES schedules(schedule_id));
""")
cities = [("Hyderabad","Vijayawada",650),("Hyderabad","Bengaluru",950),("Hyderabad","Chennai",1100),
          ("Hyderabad","Warangal",300),("Vijayawada","Chennai",700),("Bengaluru","Chennai",550),
          ("Hyderabad","Pune",1200),("Vijayawada","Bengaluru",900)]
cur.executemany("INSERT INTO routes(origin,destination,fare) VALUES(?,?,?)", cities)
start = date(2025,1,1); sid = 0
for r in range(1,9):
    for d in range(0,180):
        sid += 1
        cur.execute("INSERT INTO schedules VALUES(?,?,?,?)",(sid,r,(start+timedelta(d)).isoformat(),40))
popularity = {1:.8,2:.7,3:.55,4:.6,5:.45,6:.5,7:.4,8:.35}
for s in range(1,sid+1):
    r = cur.execute("SELECT route_id,travel_date FROM schedules WHERE schedule_id=?",(s,)).fetchone()
    wd = date.fromisoformat(r[1]).weekday()
    p = popularity[r[0]] * (1.25 if wd in (4,5,6) else 1.0)
    for seat in random.sample(range(1,41), min(40, int(40*min(p,1)*random.uniform(.6,1.1)))):
        status = "CANCELLED" if random.random() < .08 else "CONFIRMED"
        booked = date.fromisoformat(r[1]) - timedelta(random.randint(1,14))
        cur.execute("INSERT INTO bookings(schedule_id,seat_no,status,booked_on) VALUES(?,?,?,?)",
                    (s,seat,status,booked.isoformat()))
con.commit()

def run(title, sql):
    print(f"\n=== {title} ===")
    rows = cur.execute(sql).fetchall()
    for row in rows: print(row)

print("Total bookings:", cur.execute("SELECT COUNT(*) FROM bookings").fetchone()[0])


run("Seat occupancy % by route", """
SELECT r.origin||' -> '||r.destination AS route,
       ROUND(100.0*COUNT(b.booking_id)/(COUNT(DISTINCT s.schedule_id)*40),1) AS occupancy_pct
FROM routes r JOIN schedules s ON s.route_id=r.route_id
LEFT JOIN bookings b ON b.schedule_id=s.schedule_id AND b.status='CONFIRMED'
GROUP BY r.route_id ORDER BY occupancy_pct DESC""")

run("Confirmed bookings by weekday (0=Sun)", """
SELECT strftime('%w', s.travel_date) AS weekday_sun0, COUNT(*) AS bookings
FROM bookings b JOIN schedules s ON s.schedule_id=b.schedule_id
WHERE b.status='CONFIRMED' GROUP BY 1 ORDER BY bookings DESC""")

run("Cancellation rate overall", """
SELECT ROUND(100.0*SUM(status='CANCELLED')/COUNT(*),1) AS cancel_pct FROM bookings""")

run("Revenue by route (confirmed)", """
SELECT r.origin||' -> '||r.destination AS route, SUM(r.fare) AS revenue
FROM bookings b JOIN schedules s ON s.schedule_id=b.schedule_id
JOIN routes r ON r.route_id=s.route_id WHERE b.status='CONFIRMED'
GROUP BY r.route_id ORDER BY revenue DESC LIMIT 3""")

run("Monthly bookings with running total (window function)", """
WITH m AS (SELECT strftime('%Y-%m', s.travel_date) AS month, COUNT(*) AS n
           FROM bookings b JOIN schedules s ON s.schedule_id=b.schedule_id
           WHERE b.status='CONFIRMED' GROUP BY 1)
SELECT month, n, SUM(n) OVER (ORDER BY month) AS running_total FROM m""")
con.close()