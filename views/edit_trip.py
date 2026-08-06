from datetime import datetime

from db.queries import search_trips, update_trip
from utils import (
    clear, confirm_prompt, draw_table, format_date_display, format_trip_id,
    header, check_escape, resolve_trip_id
)

def edit_trip():
    while True:
        clear()
        header()
        print("\tEdit a Trip")
        print("-" * 40)
        print()

        print("\tSearch for the trip you want to edit.")
        print("\t(Press Enter to skip any filter)")
        print()

        query = check_escape(input("\tLocation keyword: ").strip())
        mode_input = check_escape(input("\tMode of Transport (bus/train/all): ").strip().lower())
        if mode_input in ("bus", "b"):
            mode = "Bus"
        elif mode_input in ("train", "t"):
            mode = "Train"
        else:
            mode = "all"

        results = search_trips(query, mode)

        if not results:
            print("\n\tNo trips found.")
            if not confirm_prompt("\tTry again? (yes/no): "):
                return
            continue

        clear()
        header()
        print("\tSelect a Trip to Edit")
        print("-" * 40)
        print()

        rows = []
        for r in results:
            rows.append([
                format_trip_id(r),
                r["mode_of_transport"],
                r["starting_location"],
                r["ending_location"],
                f"${float(r['total_price']):.2f}",
                format_date_display(r["date"]),
            ])
        draw_table(["ID", "Mode of Transport", "Starting Location", "Ending Location", "Total Price", "Date"], rows)

        print()
        trip_id_input = check_escape(input("\tEnter trip ID to edit (or press Enter to go back): ").strip())

        if trip_id_input == "":
            return
        
        trip_id = resolve_trip_id(results, trip_id_input)
        if trip_id is None:
            print("\tInvalid ID.")
            input("\tPress Enter to try again...")
            continue

        selected = next((r for r in results if r["id"] == trip_id), None)
        if not selected:
            print("\tTrip not found.")
            input("\tPress Enter to try again...")
            continue

        clear()
        header()
        print("\tEditing Trip")
        print("-" * 40)
        print()
        print("\tCurrent values shown in brackets.")
        print("\tPress Enter to keep the current value.")
        print()

        current_mode = selected["mode_of_transport"]
        while True:
            mode_input = check_escape(input(f"\tMode of Transport (bus/train) [{current_mode}]: ").strip().lower())
            if mode_input == "":
                new_mode = current_mode
                break
            elif mode_input in ("bus", "b"):
                new_mode = "Bus"
                break
            elif mode_input in ("train", "t"):
                new_mode = "Train"
                break
            else:
                print("\tPlease enter bus or train.")

        current_origin = selected["starting_location"]
        origin_input = check_escape(input(f"\tStarting Location [{current_origin}]: ").strip())
        new_origin = origin_input if origin_input != "" else current_origin

        current_dest = selected["ending_location"]
        dest_input = check_escape(input(f"\tEnding Location [{current_dest}]: ").strip())
        new_dest = dest_input if dest_input != "" else current_dest

        current_fare = float(selected["total_price"])
        while True:
            fare_input = check_escape(input(f"\tFare ($) [{current_fare:.2f}]: ").strip())
            if fare_input == "":
                new_fare = current_fare
                break
            try:
                new_fare = float(fare_input)
                if new_fare < 0:
                    print("\tFare cannot be negative.")
                    continue
                break
            except ValueError:
                print("\tPlease Enter a valid amount.")

        current_date = format_date_display(selected["date"])
        while True:
            date_input = check_escape(input(f"\tDate (DD-MM-YYYY) [{current_date}]: ").strip())
            if date_input == "":
                new_date = selected["date"]
                break
            try:
                new_date = datetime.strptime(date_input, "%d-%m-%Y").strftime("%Y-%m-%d")
                break
            except ValueError:
                print(f"\tInvalid date. use DD-MM-YYYY e.g. {datetime.now().strftime('%d-%m-%Y')}")

        clear()
        header()
        print("\tConfirm Changes")
        print("-" * 40)
        print()

        draw_table(
            ["", "Mode of Transport", "Starting Location", "Ending Location", "Total Price", "Date"],
            [
                ["Before", selected["mode_of_transport"], selected["starting_location"], selected["ending_location"], f"${current_fare:.2f}", current_date],
                ["After", new_mode, new_origin, new_dest, f"${new_fare:.2f}", format_date_display(new_date)],
            ]
        )

        print()
        if not confirm_prompt("\tSave changes? (yes/no): "):
            input("\tCancelled. Press Enter to go back...")
            return
        
        if update_trip(trip_id, new_mode, new_origin, new_dest, new_fare, new_date):
            print(f"\n\tTrip {format_trip_id(selected)} updated successfully!")
        else:
            print(f"\n\tCould not update trip {format_trip_id(selected)}.")

        input("\tPress Enter to go back...")
        return
