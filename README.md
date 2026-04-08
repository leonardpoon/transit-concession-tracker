# Transit Tracker
A personal public transport concession tracker for Singapore.
Tracks daily bus and train trips, calculates monthly spending
against the $81 concession threshold, and visualises trends
via an interactive dashboard.

---

## Features
- Log single trips, full days, or repeat past days in bulk
- Monthly and yearly summaries with concession tracking
- Search and edit past trips
- Import directly from Excel (.xlsm / .xlsx)
- Export to CSV
- Interactive web dashboard with charts and year-over-year analysis

---

## Tech Stack
- Python 3.13
- MySQL
- Streamlit + Plotly (dashboard)

---

## Setup

### 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/transit-tracker.git
cd transit-tracker/transit-concession-tracker

### 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

### 3. Install dependencies
pip install mysql-connector-python python-dotenv openpyxl streamlit plotly pandas

### 4. Set up MySQL
Run the setup script in MySQL Workbench:
setup.sql

### 5. Configure environment
Copy .env.example to .env and fill in your MySQL credentials:
copy .env.example .env

### 6. Configure run.bat
Copy run.bat.example to run.bat and update the path to your venv.

### 7. Run
Double-click run.bat
Or: python main.py

---

## Dashboard
streamlit run dashboard.py

---

## Importing existing data
Supports direct import from Excel (.xlsm/.xlsx) files.
Expected sheet structure:
- Each monthly sheet has headers:
  Mode of Transport | Starting Location | Ending Location | Total Price | Date

---

## Project Structure
db/             Database connection and queries
views/          CMD interface screens
main.py         Entry point
dashboard.py    Streamlit web dashboard
setup.sql       MySQL setup script
config.py       App settings
utils.py        Shared helper functions