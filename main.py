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
from config import MONTHS
from datetime import date

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
        print(f"\nCannot connect to MySQL: {e}")
        sys.exit(1)

    main_menu()