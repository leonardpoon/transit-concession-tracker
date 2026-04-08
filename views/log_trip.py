from datetime import date, datetime

from db.queries import get_all_locations, get_recent_routes, insert_trip
from utils import clear, draw_table, format_date_display, header, confirm_prompt, find_similar_location, check_escape


def log_trip():
    clear()
    header()
    print("\tLog Single Trip")
    print("-" * 40)

    # Show recent routes
    recent = get_recent_routes()
    if recent:
        print()
        print("\tRecent routes:")
        rows = []
        for i, r in enumerate(recent, 1):
            rows.append([
                f"[{i}]",
                r["mode_of_transport"],
                r["starting_location"],
                r["ending_location"],
                f"${float(r['total_price']):.2f}",
            ])
        draw_table(["", "Mode of Transport", "Starting Location", "Ending Location", "Total Price"], rows)
        print("\t[M] Enter manually")
        print()

        choice = check_escape(input("\tChoice: ").strip().upper())

        if choice == "M":
            _manual_entry()
        elif choice.isdigit() and 1 <= int(choice) <= len(recent):
            _quick_log(recent[int(choice) - 1])
        else:
            print("  Invalid choice.")
            input("  Press Enter to go back...")
    else:
        _manual_entry()


def _quick_log(route):
    clear()
    header()
    print("\tQuick Log")
    print("-" * 40)
    print()
    draw_table(
        ["Mode of Transport", "Starting Location", "Ending Location", "Total Price"],
        [[
            route["mode_of_transport"],
            route["starting_location"],
            route["ending_location"],
            f"${float(route['total_price']):.2f}",
        ]]
    )

    trip_date = _get_date()
    if trip_date is None:
        return

    trip_id = insert_trip(
        route["mode_of_transport"],
        route["starting_location"],
        route["ending_location"],
        float(route["total_price"]),
        trip_date,
    )

    print()
    print(f"\t✓ Saved! Trip #{trip_id} on {format_date_display(trip_date)}")
    input("\n\tPress Enter to go back...")


def _manual_entry():
    clear()
    header()
    print("\tManual Entry")
    print("-" * 40)

    # Mode
    while True:
        mode = check_escape(input("\n\tMode of Transport (B = Bus, T = Train): ").strip().upper())
        if mode == "B":
            mode = "Bus"
            break
        elif mode == "T":
            mode = "Train"
            break
        else:
            print("\tPlease enter B or T")

    locations = get_all_locations()

    # Origin
    origin = check_escape(input("\tStarting Location: ").strip())
    if origin == "":
        print("\tStarting location cannot be empty.")
        input("\tPress Enter to go back...")
        return
    if origin not in locations:
        similar = find_similar_location(origin, locations)
        if similar:
            if not confirm_prompt(f"\tDid you mean '{similar}'? (yes/no): "):
                if not confirm_prompt(f"\t'{origin}' as a new location? (yes/no): "):
                    return None

    # Destination
    destination = check_escape(input("\tEnding Location: ").strip())
    if destination == "":
        print("\tEnding location cannot be empty.")
        input("\tPress Enter to go back...")
        return
    if destination not in locations:
        similar = find_similar_location(destination, locations)
        if similar:
            if not confirm_prompt(f"\tDid you mean '{similar}'? (yes/no): "):
                if not confirm_prompt(f"\t'{destination}' as a new location? (yes/no): "):
                    return None

    if origin.lower() == destination.lower():
        print("\tStart and end location cannot be the same.")
        input("\tPress Enter to go back...")
        return

    # Total Price
    while True:
        try:
            total_price = float(check_escape(input("\tFare ($): ").strip()))
            if total_price <= 0:
                raise ValueError
            break
        except ValueError:
            print("\tPlease enter a valid amount e.g. 1.50")

    # Date
    trip_date = _get_date()
    if trip_date is None:
        return

    trip_id = insert_trip(mode, origin, destination, total_price, trip_date)
    print()
    print(f"\t✓ Saved! Trip #{trip_id}")
    print(f"\t{mode} | {origin} → {destination}\t|\t${total_price:.2f}\t|\t{format_date_display(trip_date)}")
    input("\n\tPress Enter to go back...")


def _get_date():
    today = date.today()
    today_display = today.strftime("%d-%m-%Y")
    date_input = check_escape(input(f"\n\tDate (DD-MM-YYYY) [press Enter for today: {today_display}]: ").strip())

    if date_input == "":
        return str(today)

    try:
        dt = datetime.strptime(date_input, "%d-%m-%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        print(f"\tInvalid date. Use DD-MM-YYYY e.g. {datetime.now().strftime('%d-%m-%Y')}")
        input("\tPress Enter to go back...")
        return None