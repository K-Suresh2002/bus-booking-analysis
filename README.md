# Bus Booking Analysis

## Overview

This project analyzes simulated bus booking data using Python, SQLite, and SQL.

The project generates a bus booking dataset and performs business analysis using SQL queries involving joins, aggregations, CTEs, and window functions.

## Technologies Used

- Python
- SQLite
- SQL
- Git & GitHub

## Database Tables

The SQLite database contains three tables:

- `routes` - Stores bus route and fare information
- `schedules` - Stores travel dates and available seats
- `bookings` - Stores booking and cancellation information

## Analysis Performed

The project answers the following business questions:

1. Seat occupancy percentage by route
2. Confirmed bookings by weekday
3. Overall cancellation rate
4. Revenue by route
5. Monthly bookings with running total

## Key Results

- Total bookings: 28,713
- Overall cancellation rate: 7.7%
- Highest occupancy route: Hyderabad → Vijayawada
- Highest revenue route: Hyderabad → Bengaluru
- Total confirmed bookings analyzed by month using SQL window functions

## How to Run

Clone the repository:

```bash
git clone https://github.com/K-Suresh2002/bus-booking-analysis.git