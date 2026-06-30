"""
Quick connection test for TiDB Cloud.
Run from your project root: python test_connection.py
"""

import sys
from config import DB_CONFIG

print("Attempting connection with:")
safe_config = {k: v for k, v in DB_CONFIG.items() if k != 'password'}
safe_config['password'] = '***' if DB_CONFIG.get('password') else '(empty!)'
for k, v in safe_config.items():
    print(f"  {k}: {v}")
print()

try:
    import mysql.connector
except ImportError:
    print("mysql-connector-python isn't installed. Run:")
    print("  pip install mysql-connector-python")
    sys.exit(1)

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()[0]
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    print("Connected successfully.")
    print(f"Server version: {version}")
    print(f"Tables found: {tables if tables else '(none yet)'}")

except mysql.connector.Error as e:
    print(f"Connection failed: {e}")
    print()
    msg = str(e).lower()
    if "access denied" in msg:
        print("Hint: check DB_USER includes your cluster prefix (e.g. 'abc123.root',")
        print("not just 'root'), and DB_PASSWORD matches exactly - copy/paste from")
        print("the TiDB Cloud console rather than retyping it.")
    elif "ssl" in msg or "certificate" in msg:
        print("Hint: SSL/certificate issue. Confirm DB_SSL=true is set in .env,")
        print("and that 'certifi' is installed (pip install certifi) so config.py")
        print("can fall back to its CA bundle automatically.")
    elif "unknown database" in msg:
        print("Hint: DB_NAME doesn't exist on this cluster yet. Run setup.sql")
        print("against it first, or call init_schema() to create it.")
    elif "can't connect" in msg or "timed out" in msg or "timeout" in msg:
        print("Hint: check DB_HOST and DB_PORT (should be 4000 for TiDB), and")
        print("confirm your network/firewall allows outbound connections on that port.")
    sys.exit(1)

except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)