import sys

from db.connection import init_schema
from views.log_trip import log_trip
from views.monthly import monthly_summary
from views.history import all_history
from utils import clear, header, show_monthly_status
from config import MONTHS
from datetime import date

def main_menu():
    while True:
        clear()
        header()
        show_monthly_status()
        print("\t[1] Log New Trip")
        print("\t[2] View This Month's Summary")
        print("\t[3] View All History")
        print("\t[4] Exit")
        print()

        choice = input("\tEnter your choice: ").strip()

        if choice == "1":
            log_trip()
        elif choice == "2":
            monthly_summary()
        elif choice == "3":
            all_history()
        elif choice == "4":
            print("\nGoodbye!")
            sys.exit()
        else:
            input("\tInvalid choice. Press Enter to try again.")

if __name__ == "__main__":
    try:
        init_schema()
    except Exception as e:
        print(f"\nCannot connect to MySQL: {e}")
        sys.exit(1)

    main_menu()