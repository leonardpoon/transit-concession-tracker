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

# change according to the concession price purchased by the user
CONCESSION_THRESHOLD = 81.00

APP_TITLE = "Transit Tracker"

MONTHS = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

