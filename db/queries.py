from db.connection import get_connection

def insert_trip(mode, origin, destination, fare, trip_date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO trips (mode, origin, destination, fare, trip_date) "
        "VALUES (%s, %s, %s, %s, %s)",
        (mode, origin.strip(), destination.strip(), fare, trip_date)
    )

    conn.commit()
    trip_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return trip_id

def get_trips_by_month(year, month):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute(
        "SELECT id, mode, origin, destination, fare, trip_date "
        "FROM trips "
        "WHERE YEAR(trip_date) = %s AND MONTH(trip_date) = %s "
        "ORDER BY trip_date DESC",
        (year, month)
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_monthly_summary(year, month):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT "
        "  COALESCE(SUM(fare), 0)                           AS total, "
        "  COUNT(*)                                         AS trip_count, "
        "  SUM(CASE WHEN mode = 'Bus'   THEN 1 ELSE 0 END) AS bus_count, "
        "  SUM(CASE WHEN mode = 'Train' THEN 1 ELSE 0 END) AS train_count "
        "FROM trips "
        "WHERE YEAR(trip_date) = %s AND MONTH(trip_date) = %s",
        (year, month)
    )

    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def get_all_locations():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT DISTINCT location FROM ("
        "  SELECT origin AS location FROM trips "
        "  UNION "
        "  SELECT destination AS location FROM trips"
        ") sub ORDER BY location"
    )

    locations = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return locations

def delete_trip(trip_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM trips WHERE id = %s", (trip_id,))
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    return affected > 0

def get_recent_days(limit=5):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT trip_date, "
        "COUNT(*) AS trip_count, "
        "SUMM(fare) AS total_fare "
        "FROM trips "
        "GROUP BY trip_date "
        "ORDER BY trip_date DESC "
        "LIMIT %s",
        (limit,)
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_trips_by_date(trip_date):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT mode, origin, destination, fare "
        "FROM trips "
        "WHERE trip_date = %s "
        "ORDER BY created_at DESC",
        (trip_date,)
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def insert_trips_bulk(trips):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executemany(
        "INSERT INTO trips (mode, origin, destination, fare, trip_date) "
        "VALUES (%s, %s, %s, %s, %s)",
        trips
    )

    conn.commit()
    count = cursor.rowcount
    cursor.close()
    conn.close()
    return count

def get_recent_routes(limit=5):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT mode, origin, destination, fare "
        "FROM trips "
        "GROUP BY mode, origin, destination, fare "
        "ORDER BY MAX(created_at) DESC "
        "LIMIT %s",
        (limit,)
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_months_with_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT DISTINCT YEAR(trip_date) AS y, MONTH(trip_date) AS m "
        "FROM trips ORDER BY y DESC, m DESC"
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows