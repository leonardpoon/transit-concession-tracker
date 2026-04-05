from datetime import date, datetime

from db.queries import get_all_locations, get_recent_routes, insert_trip
from utils import clear, draw_table, format_date_display, header


def log_trip():
    clear()
    header()
    print("  Log Single Trip")
    print("-" * 40)

    # Show recent routes
    recent = get_recent_routes()
    if recent:
        print()
        print("  Recent routes:")
        rows = []
        for i, r in enumerate(recent, 1):
            rows.append([
                f"[{i}]",
                r["mode"],
                r["origin"],
                r["destination"],
                f"${float(r['fare']):.2f}",
            ])
        draw_table(["", "Mode", "From", "To", "Fare"], rows)
        print("  [M] Enter manually")
        print()

        choice = input("  Choice: ").strip().upper()

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
    print("  Quick Log")
    print("-" * 40)
    print()
    draw_table(
        ["Mode", "From", "To", "Fare"],
        [[
            route["mode"],
            route["origin"],
            route["destination"],
            f"${float(route['fare']):.2f}",
        ]]
    )

    trip_date = _get_date()
    if trip_date is None:
        return

    trip_id = insert_trip(
        route["mode"],
        route["origin"],
        route["destination"],
        float(route["fare"]),
        trip_date,
    )

    print()
    print(f"  ✓ Saved! Trip #{trip_id} on {format_date_display(trip_date)}")
    input("\n  Press Enter to go back...")


def _manual_entry():
    clear()
    header()
    print("  Manual Entry")
    print("-" * 40)

    # Mode
    while True:
        mode = input("\n  Mode (B = Bus, T = Train): ").strip().upper()
        if mode == "B":
            mode = "Bus"
            break
        elif mode == "T":
            mode = "Train"
            break
        else:
            print("  Please enter B or T")

    locations = get_all_locations()

    # Origin
    origin = input("  From: ").strip()
    if origin == "":
        print("  Starting location cannot be empty.")
        input("  Press Enter to go back...")
        return
    if origin not in locations:
        confirm = input(f"  '{origin}' is new. Save anyway? (y/n): ").strip().lower()
        if confirm != "y":
            input("  Cancelled. Press Enter to go back...")
            return

    # Destination
    destination = input("  To: ").strip()
    if destination == "":
        print("  Ending location cannot be empty.")
        input("  Press Enter to go back...")
        return
    if destination not in locations:
        confirm = input(f"  '{destination}' is new. Save anyway? (y/n): ").strip().lower()
        if confirm != "y":
            input("  Cancelled. Press Enter to go back...")
            return

    if origin.lower() == destination.lower():
        print("  Start and end location cannot be the same.")
        input("  Press Enter to go back...")
        return

    # Fare
    while True:
        try:
            fare = float(input("  Fare ($): ").strip())
            if fare <= 0:
                raise ValueError
            break
        except ValueError:
            print("  Please enter a valid amount e.g. 1.50")

    # Date
    trip_date = _get_date()
    if trip_date is None:
        return

    trip_id = insert_trip(mode, origin, destination, fare, trip_date)
    print()
    print(f"  ✓ Saved! Trip #{trip_id}")
    print(f"  {mode} | {origin} → {destination} | ${fare:.2f} | {format_date_display(trip_date)}")
    input("\n  Press Enter to go back...")


def _get_date():
    today = date.today()
    today_display = today.strftime("%d-%m-%Y")
    date_input = input(f"\n  Date (DD-MM-YYYY) [press Enter for today: {today_display}]: ").strip()

    if date_input == "":
        return str(today)

    try:
        dt = datetime.strptime(date_input, "%d-%m-%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        print("  Invalid date. Use DD-MM-YYYY e.g. 07-04-2026")
        input("  Press Enter to go back...")
        return None