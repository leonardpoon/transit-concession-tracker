import mysql.connector
from config import DB_CONFIG

def init_schema():
    base = {k: v for k, v in DB_CONFIG.items() if k != 'database'}
    db_name = DB_CONFIG['database']

    conn = mysql.connector.connect(**base)
    cursor = conn.cursor()

    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
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

    conn.commit()
    cursor.close()
    conn.close()

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)