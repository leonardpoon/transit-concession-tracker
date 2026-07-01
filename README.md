# Transit Tracker
A personal public transport concession tracker for Singapore.
Tracks daily bus and train trips, calculates monthly spending
against the concession threshold active for each period, and visualises trends
via an interactive dashboard.

---

## Features
- Log single trips, full days, or repeat past days in bulk
- Monthly and yearly summaries with concession tracking
- Search and edit past trips
- Import directly from Excel (.xlsm / .xlsx)
- Export to CSV
- Interactive web dashboard with charts and year-over-year analysis
- Dynamic concession periods, including threshold and billing cycle dates

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
pip install -r requirements.txt

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

## Deployment
See `DEPLOYMENT.md` for running the CLI from any computer with TiDB as the
shared backend.

---

## Updating concession prices
Use `Manage Concession Periods` from the main menu.

When the concession price changes from `$81` to `$122`, add a new period with
the new effective start date and threshold `122`. The app automatically closes
the previously active period the day before the new start date, so older trip
data and historical summaries keep using the old threshold.

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
