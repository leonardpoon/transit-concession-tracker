import os
import shutil
import subprocess
import sys

from db.connection import init_schema
from views.log_trip import log_trip
from views.repeat_days import repeat_days
from views.log_day import log_day
from views.monthly import monthly_summary
from views.history import all_history
from views.csv_import import csv_import
from views.search import search
from views.edit_trip import edit_trip
from views.export import export
from views.manage_periods import manage_periods

from utils import clear, header, show_monthly_status, EscapeToMenu, show_recent_trips


def pause_before_exit():
    if getattr(sys, "frozen", False):
        try:
            input("\nPress Enter to close...")
        except EOFError:
            pass


def print_connection_error(error):
    print(f"\nCannot connect to MySQL/TiDB: {error}")
    print()
    print("Things to check:")
    print("  1. Your internet connection is active.")
    print("  2. TiDB Cloud allows your current public IP address.")
    print("  3. DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, and DB_NAME are correct.")
    print("  4. DB_SSL=true is set for TiDB Cloud.")
    print()

    msg = str(error).lower()
    if "10013" in msg:
        print("Windows reported socket error 10013.")
        print("This is usually a firewall, antivirus, VPN, or network policy blocking")
        print("the outbound connection to TiDB on port 4000.")
    elif "access denied" in msg:
        print("The database rejected the login. Recheck DB_USER and DB_PASSWORD.")
    elif "unknown database" in msg:
        print("The database name does not exist yet. Run setup.sql or start the app")
        print("with a user that has permission to create the database.")
    elif "timed out" in msg or "can't connect" in msg:
        print("The app could not reach TiDB. Check host, port, network, and TiDB")
        print("IP access list settings.")


def launch_dashboard():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    dashboard_path = os.path.join(app_dir, "dashboard.py")
    if not os.path.exists(dashboard_path):
        dashboard_path = os.path.join(os.path.dirname(app_dir), "dashboard.py")

    if not os.path.exists(dashboard_path):
        print("\nCould not find dashboard.py next to the app.")
        input("\nPress Enter to return to the menu...")
        return

    streamlit_cmd = shutil.which("streamlit")
    if streamlit_cmd:
        cmd = [streamlit_cmd, "run", dashboard_path]
    else:
        python_cmd = shutil.which("python") or shutil.which("py") or sys.executable
        cmd = [python_cmd, "-m", "streamlit", "run", dashboard_path]

    try:
        subprocess.Popen(cmd)
        print("\nDashboard is starting in your browser...")
    except Exception as e:
        print(f"\nCould not launch dashboard: {e}")
    input("\nPress Enter to return to the menu...")


def main_menu():
    while True:
        clear()
        header()
        show_monthly_status()
        show_recent_trips()
        print("\t[1] Log New Trip")
        print("\t[2] Log a Full Day")
        print("\t[3] Repeat a Past Day")
        print("\t[4] View This Month's Summary")
        print("\t[5] View All History")
        print("\t[6] Search Trips")
        print("\t[7] Edit a Trip")
        print("\t[8] Export to CSV")
        print("\t[9] Import from CSV")
        print("\t[10] Manage Concession Periods")
        print("\t[D] Launch Dashboard")
        print("\t[0] Exit")
        print()
        print("\t(Type 'e' at any prompt to return to this menu)")

        choice = input("\tEnter your choice: ").strip()

        try:
            if choice == "1":
                log_trip()
            elif choice == "2":
                log_day()
            elif choice == "3":
                repeat_days()
            elif choice == "4":
                monthly_summary()
            elif choice == "5":
                all_history()
            elif choice == "6":
                search()
            elif choice == "7":
                edit_trip()
            elif choice == "8":
                export()
            elif choice == "9":
                csv_import()
            elif choice == "10":
                manage_periods()
            elif choice.lower() == "d":
                launch_dashboard()
            elif choice == "0":
                print("\nGoodbye!")
                sys.exit(0)
            else:
                input("\tInvalid choice. Press Enter to try again.")
        except SystemExit:
            raise
        except EscapeToMenu:
            continue


if __name__ == "__main__":
    try:
        init_schema()
    except Exception as e:
        print_connection_error(e)
        pause_before_exit()
        sys.exit(1)

    if len(sys.argv) > 1 and sys.argv[1].lower() in ("dashboard", "--dashboard", "-d"):
        launch_dashboard()
        sys.exit(0)

    main_menu()
