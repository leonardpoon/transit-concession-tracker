from db.connection import get_connection

def insert_trip(mode_of_transport, starting_location, ending_location, total_price, date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO trips (mode_of_transport, starting_location, ending_location, total_price, date) "
        "VALUES (%s, %s, %s, %s, %s)",
        (mode_of_transport, starting_location.strip(), ending_location.strip(), total_price, date)
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
        "SELECT id, mode_of_transport, starting_location, ending_location, total_price, date "
        "FROM trips "
        "WHERE YEAR(date) = %s AND MONTH(date) = %s "
        "ORDER BY date DESC, id DESC",
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
        "  COALESCE(SUM(total_price), 0)                           AS total, "
        "  COUNT(*)                                         AS trip_count, "
        "  SUM(CASE WHEN mode_of_transport = 'Bus'   THEN 1 ELSE 0 END) AS bus_count, "
        "  SUM(CASE WHEN mode_of_transport = 'Train' THEN 1 ELSE 0 END) AS train_count "
        "FROM trips "
        "WHERE YEAR(date) = %s AND MONTH(date) = %s",
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
        "  SELECT starting_location AS location FROM trips "
        "  UNION "
        "  SELECT ending_location AS location FROM trips"
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
        "SELECT date, "
        "COUNT(*) AS trip_count, "
        "SUM(total_price) AS total_price "
        "FROM trips "
        "GROUP BY date "
        "ORDER BY date DESC "
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
        "SELECT mode_of_transport, starting_location, ending_location, total_price "
        "FROM trips "
        "WHERE date = %s "
        "ORDER BY id ASC",
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
        "INSERT INTO trips (mode_of_transport, starting_location, ending_location, total_price, date) "
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
        "SELECT mode_of_transport, starting_location, ending_location, total_price "
        "FROM trips "
        "GROUP BY mode_of_transport, starting_location, ending_location, total_price "
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
        "SELECT DISTINCT YEAR(date) AS y, MONTH(date) AS m "
        "FROM trips ORDER BY y DESC, m DESC"
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def search_trips(query = "", mode = "", start_date = "", end_date = ""):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    conditions = []
    params = []

    if query:
        conditions.append("(starting_location LIKE %s OR ending_location LIKE %s)")
        params += [f"%{query}%", f"%{query}%"]
    if mode and mode != "all":
        conditions.append("mode_of_transport = %s")
        params.append(mode)
    if start_date:
        conditions.append("date >= %s")
        params.append(start_date)
    if end_date:
        conditions.append("date <= %s")
        params.append(end_date)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    cursor.execute(
        f"SELECT id, mode_of_transport, starting_location, ending_location, total_price, date "
        f"FROM trips {where} "
        f"ORDER BY id DESC, id ASC LIMIT 100",
        params,
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def update_trip(trip_id, mode_of_transport, starting_location, ending_location, total_price, date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE trips "
        "SET mode_of_transport = %s, starting_location = %s, ending_location = %s, "
        "total_price = %s, date = %s "
        "WHERE id =  %s",
        (mode_of_transport, starting_location, ending_location, total_price, date, trip_id)
    )

    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    return affected > 0


def get_all_trips():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, mode_of_transport, starting_location, ending_location, total_price, date "
        "FROM trips "
        "ORDER BY id ASC"
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_cycle_summary(start_date, end_date):
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    cursor.execute(
        "SELECT "
        " COALESCE(SUM(total_price), 0) AS total, "
        " COUNT(*) AS trip_count, "
        " SUM(CASE WHEN mode_of_transport = 'Bus' THEN 1 ELSE 0 END) AS bus_count, "
        " SUM(CASE WHEN mode_of_transport = 'Train' THEN 1 ELSE 0 END) AS train_count "
        "FROM trips "
        "WHERE date >= %s AND date <= %s",
        (start_date, end_date)
    )

    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def get_trips_by_cycle(start_date, end_date):
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    cursor.execute(
        "SELECT id, mode_of_transport, starting_location, ending_location, "
        "total_price, date "
        "FROM trips "
        "WHERE date >= %s AND date <= %s "
        "ORDER BY date DESC, id DESC",
        (start_date, end_date)
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows