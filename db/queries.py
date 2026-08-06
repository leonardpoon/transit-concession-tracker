from db.connection import get_connection
from datetime import date, timedelta

_NOCHANGE = object()


def _trip_display_id_map(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM trips ORDER BY date ASC, id ASC")
    display_ids = {row[0]: i for i, row in enumerate(cursor.fetchall(), 1)}
    cursor.close()
    return display_ids


def _attach_display_ids(conn, rows):
    display_ids = _trip_display_id_map(conn)
    for row in rows:
        row["display_id"] = display_ids.get(row["id"], row["id"])
    return rows


def get_trip_display_id(trip_id):
    conn = get_connection()
    display_ids = _trip_display_id_map(conn)
    conn.close()
    return display_ids.get(trip_id, trip_id)


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
    _attach_display_ids(conn, rows)
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
        f"ORDER BY date DESC, id DESC LIMIT 100",
        params,
    )

    rows = cursor.fetchall()
    _attach_display_ids(conn, rows)
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
        "ORDER BY date ASC, id ASC"
    )

    rows = cursor.fetchall()
    _attach_display_ids(conn, rows)
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
    _attach_display_ids(conn, rows)
    cursor.close()
    conn.close()
    return rows

def get_lifetime_summary():
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    cursor.execute(
        "SELECT "
        " COALESCE(SUM(total_price), 0) AS total_spent, "
        " COUNT(*) AS total_trips, "
        " SUM(CASE WHEN mode_of_transport = 'Bus' THEN 1 ELSE 0 END) AS bus_count, "
        " SUM(CASE WHEN mode_of_transport = 'Train' THEN 1 ELSE 0 END) AS train_count, "
        " MIN(date) AS first_trip, "
        " MAX(date) AS last_trip "
        "FROM trips"
    )

    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_recent_trips(limit = 5):
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    cursor.execute(
        "SELECT id, mode_of_transport, starting_location, ending_location, total_price, date "
        "FROM trips "
        "ORDER BY id DESC "
        "LIMIT %s",
        (limit,)
    )

    rows = cursor.fetchall()
    _attach_display_ids(conn, rows)
    cursor.close()
    conn.close()
    return rows

def get_active_period(check_date = None):
    if check_date is None:
        check_date = date.today()

    conn = get_connection()
    cursor = conn.cursor(dictionary = True)
    cursor.execute(
        "SELECT * FROM concession_periods "
        "WHERE start_date <= %s AND (end_date IS NULL OR end_date >= %s) "
        "ORDER BY start_date DESC "
        "LIMIT 1",
        (check_date, check_date)
    )

    period = cursor.fetchone()
    cursor.close()
    conn.close()
    return period

def get_all_periods():
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)
    cursor.execute("SELECT * FROM concession_periods ORDER BY start_date DESC")
    periods = cursor.fetchall()
    cursor.close()
    conn.close()
    return periods

def _ranges_overlap(start_a, end_a, start_b, end_b):
    end_a = end_a or date.max
    end_b = end_b or date.max
    return start_a <= end_b and start_b <= end_a

def _validate_period_range(cursor, start_date, end_date, exclude_id = None):
    if end_date is not None and end_date < start_date:
        raise ValueError("End date cannot be before start date.")

    params = []
    where = ""
    if exclude_id is not None:
        where = "WHERE id <> %s"
        params.append(exclude_id)

    cursor.execute(
        f"SELECT id, start_date, end_date FROM concession_periods {where}",
        params,
    )
    for existing_id, existing_start, existing_end in cursor.fetchall():
        if _ranges_overlap(start_date, end_date, existing_start, existing_end):
            raise ValueError(
                "Period overlaps with existing period "
                f"#{existing_id} ({existing_start} to {existing_end or 'active'})."
            )

def add_concession_period(start_date, cycle_reset_day, threshold_amount, label = None):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, start_date, end_date FROM concession_periods WHERE end_date IS NULL")
        open_period = cursor.fetchone()
        if open_period:
            close_date = start_date - timedelta(days = 1)
            if close_date < open_period[1]:
                raise ValueError(
                    "New period's start date is before the currently open "
                    "period's start date. Invalid range."
                )
            cursor.execute(
                "UPDATE concession_periods SET end_date = %s WHERE id = %s",
                (close_date, open_period[0])
            )

        _validate_period_range(cursor, start_date, None, exclude_id = open_period[0] if open_period else None)

        cursor.execute(
            "INSERT INTO concession_periods "
            "(start_date, end_date, cycle_reset_day, threshold_amount, label) "
            "VALUES (%s, NULL, %s, %s, %s)",
            (start_date, cycle_reset_day, threshold_amount, label)
        )

        conn.commit()
        new_id = cursor.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
    return new_id

def update_period(period_id, start_date = _NOCHANGE, end_date = _NOCHANGE, cycle_reset_day = _NOCHANGE, threshold_amount = _NOCHANGE, label = _NOCHANGE):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT start_date, end_date FROM concession_periods WHERE id = %s",
            (period_id,),
        )
        current = cursor.fetchone()
        if current is None:
            raise ValueError("Period not found.")

        new_start = current[0] if start_date is _NOCHANGE else start_date
        new_end = current[1] if end_date is _NOCHANGE else end_date
        _validate_period_range(cursor, new_start, new_end, exclude_id = period_id)

        fields, values = [], []
        for col, val in [
            ("start_date", start_date),
            ("end_date", end_date),
            ("cycle_reset_day", cycle_reset_day),
            ("threshold_amount", threshold_amount),
            ("label", label)
        ]:
            if val is not _NOCHANGE:
                fields.append(f"{col} = %s")
                values.append(val)

        if not fields:
            return

        values.append(period_id)
        cursor.execute(
            f"UPDATE concession_periods SET {', '.join(fields)} WHERE id = %s",
            values
        )

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
