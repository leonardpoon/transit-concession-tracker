from datetime import date, datetime
from db.queries import get_all_locations, insert_trips_bulk
from utils import clear, draw_table, format_date_display, header, confirm_prompt, find_similar_location

def log_day():
    clear()
    header()
    print("\t Log Full Day")
    print("-" * 40)

    today = date.today()
    today_display = today.strftime("%d-%m-%Y")
    date_input = input(f"\n\tDate (DD-MM-YYYY) [Press Enter for today's date {today_display}]: ").strip()

    if date_input == "":
        trip_date = str(today)

    else:
        try:
            dt = datetime.strptime(date_input, "%d-%m-%Y")
            trip_date = dt.strftime("%Y-%m-%d")
        except ValueError:
            print("\tInvalid date. Use DD-MM-YYYY e.g. 01-12-2026")
            input("\tPress Enter to go back...")
            return
        
    trips = []
    locations = get_all_locations()
    
    while True:
        clear()
        header()
        print(f"\tLog Full Day - {format_date_display(trip_date)}")
        print("-" * 40)

        if trips:
            print()
            rows = []
            for i, t in enumerate(trips, 1):
                rows.append([
                    str(i),
                    t[0],
                    t[1],
                    t[2],
                    f"${t[3]:.2f}"
                    ])
            draw_table(["#", "Mode", "From", "To", "Fare"], rows)
            total = sum(t[3] for t in trips)
            print(f"\n\tRunning Total: ${total:.2f}")
        else:
            print("\n\tNo trips logged yet.")

        print()
        print("\t[A] Add Trip\t[D] Delete Last\t[S] Save Day\t[C] Cancel")
        print()
        choice = input("\tChoice: ").strip().upper()

        if choice == "A":
            trip = _add_trip(locations)
            if trip:
                trips.append(trip)
                locations = get_all_locations()

        elif choice == "D":
            if trips:
                removed = trips.pop()
                print(f"\n\t✓ Removed: {removed[0]} | {removed[1]} → {removed[2]}")
                input("\tPress Enter to continue...")
            else:
                input("\tNo trips to delete. Press Enter to continue...")

        elif choice == "S":
            if not trips:
                input("\tNo trips to save. Press Enter to continue...")
                continue

            clear()
            header()
            print(f"\tConfirm Save - {format_date_display(trip_date)}")
            print("-" * 40)
            rows = []
            for i, t in enumerate(trips, 1):
                rows.append([
                    str(i),
                    t[0],
                    t[1],
                    t[2],
                    f"${t[3]:.2f}",
                ])
            draw_table(["#", "Mode", "From", "To", "Fare"], rows)

            total = sum(t[3] for t in trips)
            print(f"\n\t{len(trips)} trips\t|\tTotal: ${total:.2f}")
            print()

            if confirm_prompt("\tSave all? (yes/no): "):
                bulk = [(t[0], t[1], t[2], t[3], trip_date) for t in trips]
                count = insert_trips_bulk(bulk)
                print(f"\n\t✓ {count} trips saved for {format_date_display(trip_date)}")
                input("\tPress Enter to go back...")
                return
            else:
                input("\tCancelled. Press Enter to continue editing...")

        elif choice == "C":
            if trips:
                if confirm_prompt("\tDiscard all changes? (yes/no): "):
                    return
            else:
                return
            
def _add_trip(locations):
    print()

    while True:
        mode = input("\tMode of Transport (Bus/Train): ").strip().upper()
        if mode == "BUS":
            mode = "Bus"
            break
        elif mode == "TRAIN":
            mode = "Train"
            break
        else:
            print("\tPlease enter Bus or Train.")

    origin = input("\tStarting Location: ").strip()
    if origin == "":
        print("\tStarting Location cannot be empty.")
        return None
    if origin not in locations:
        similar = find_similar_location(origin, locations)
        if similar:
            if not confirm_prompt(f"\tDid you mean '{similar}'? (yes/no): "):
                if not confirm_prompt(f"\t'{origin}' as a new location? (yes/no): "):
                    return None
        
    destination = input("\tEnding Location: ").strip()
    if destination == "":
        print("\tEnding Location cannot be empty.")
        return None
    if destination not in locations:
        similar = find_similar_location(destination, locations)
        if similar:
            if not confirm_prompt(f"\tDid you mean '{similar}'? (yes/no): "):
                if not confirm_prompt(f"\t'{destination}' as a new location? (yes/no): "):
                    return None

    while True:
        try:
            fare = float(input("\tFare ($): ").strip())
            if fare < 0:
                raise ValueError
            break
        except ValueError:
            print("\tPlease enter a valid non-negative number for fare.")
    print(f"\t✓ Added: {mode} | {origin} → {destination} | ${fare:.2f}")
    return (mode, origin, destination, fare)
    