import mysql.connector
from config import DB_CONFIG, DEFAULT_CONCESSION_THRESHOLD, DEFAULT_CYCLE_RESET_DAY

def init_schema():
    base = {k: v for k, v in DB_CONFIG.items() if k != 'database'}
    db_name = DB_CONFIG['database']

    conn = mysql.connector.connect(**base)
    cursor = conn.cursor()

    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
    cursor.execute(f"USE `{db_name}`")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INT AUTO_INCREMENT PRIMARY KEY,
            mode_of_transport ENUM('Bus', 'Train') NOT NULL,
            starting_location VARCHAR(255) NOT NULL,
            ending_location VARCHAR(255) NOT NULL,
            total_price DECIMAL(10, 2) NOT NULL,
            date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS concession_periods (
            id INT AUTO_INCREMENT PRIMARY KEY,
            start_date DATE NOT NULL,
            end_date DATE NULL,
            cycle_reset_day INT NOT NULL,
            threshold_amount DECIMAL(10, 2) NOT NULL,
            label VARCHAR(255) NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("ALTER TABLE concession_periods MODIFY end_date DATE NULL")
    cursor.execute("ALTER TABLE concession_periods MODIFY label VARCHAR(255) NULL")

    cursor.execute("SELECT COUNT(*) FROM concession_periods")
    period_count = cursor.fetchone()[0]
    if period_count == 0:
        cursor.execute("SELECT COALESCE(MIN(date), CURRENT_DATE()) FROM trips")
        seed_start = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO concession_periods "
            "(start_date, end_date, cycle_reset_day, threshold_amount, label) "
            "VALUES (%s, NULL, %s, %s, %s)",
            (
                seed_start,
                DEFAULT_CYCLE_RESET_DAY,
                DEFAULT_CONCESSION_THRESHOLD,
                "Legacy concession",
            ),
        )

    conn.commit()
    cursor.close()
    conn.close()

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)
