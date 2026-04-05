from datetime import datetime

from db.queries import search_trips
from utils import clear, confirm_prompt, draw_table, format_date_display, header

def search():
    while True:
        clear()
        header()
        print("\tSearch Trips")
        print("-" * 40)
        print()
        print("\tFilters (press Enter to skip any filter)")
        print()

        query = input("\tLocation keyword: ").strip()

        mode_input = input("\tMode (bus/train/all): ").strip().lower()
        if mode_input in ("bus", "b"):
            mode = "Bus"
        elif mode_input in ("train", "t"):
            mode = "Train"
        else:
            mode = "all"


        print()
        print("\tData range (DD-MM-YYYY, press Enter to skip)")
        start_raw = input("\tFrom date: ").strip()
        end_raw   = input("\tTo date  : ").strip()

        start_date = ""
        end_date = ""

        if start_raw:
            try:
                start_date = datetime.strptime(start_raw, "%d-%m-%Y").strftime("%Y-%m-%d")
            except ValueError:
                print("\tInvalid start date - skipping.")
        
        if end_raw:
            try:
                end_date = datetime.strptime(end_raw, "%d-%m-%Y").strftime("%Y-%m-%d")
            except ValueError:
                print("\tInvalid end date - skipping.")

        results = search_trips(query, mode, start_date, end_date)

        clear()
        header()
        print("\tSearch Results")
        print("-" * 40)

        if not results:
            print("\n\tNo trips found.")

        else:
            rows = []
            for r in results:
                rows.append([
                    f"#{r['id']}",
                    r["mode"],
                    r["origin"],
                    r["destination"],
                    f"${float(r['fare']):.2f}",
                    format_date_display(r["trip_date"]),
                ])
            draw_table(["ID", "Mode", "Origin", "Destination", "Fare", "Date"], rows)

            total = sum(float(r["fare"]) for r in results)
            print(f"\n\t{len(results)} trips found\t|\tTotal: ${total:.2f}")

        print()
        if not confirm_prompt("\tSearch again? (yes/no): "):
            break