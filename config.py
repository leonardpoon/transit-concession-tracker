import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'transit_tracker'),
    'port': int(os.getenv('DB_PORT', 3306))
}

# TiDB Cloud requires TLS. Set DB_SSL=true in .env when pointing at TiDB.
if os.getenv('DB_SSL', 'false').lower() == 'true':
    DB_CONFIG['ssl_verify_cert'] = True
    ssl_ca_path = os.getenv('DB_SSL_CA')
    if not ssl_ca_path:
        # No explicit CA file given - fall back to certifi's bundled CA
        # store instead of relying on whatever the OS happens to trust.
        try:
            import certifi
            ssl_ca_path = certifi.where()
        except ImportError:
            ssl_ca_path = None  # pip install certifi to enable this fallback
    if ssl_ca_path:
        DB_CONFIG['ssl_ca'] = ssl_ca_path

# Legacy fallback only - used if a date falls outside every row in
# concession_periods (shouldn't happen once the table is seeded).
# The real threshold now comes from the active concession_periods row.
DEFAULT_CONCESSION_THRESHOLD = 81.00

APP_TITLE = "Transit Tracker"

MONTHS = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]