from datetime import datetime
from db.queries import get_recent_days, get_trips_by_date, insert_trips_bulk
from utils import clear, collect_dates, draw_table, format_date_display, header, confirm_prompt, check_escape

def repeat_days():
    clear()
    header()
    print("\tRepeat a Past Day")
    print("-" * 40)

    recent = get_recent_days()

    if not recent:
        print("\n\tNo past days found.")
        input("\tPress Enter to go back...")
        return
    
    print()
    rows = []
    for i, day in enumerate(recent, 1):
        rows.append([
            f"[{i}]",
            format_date_display(day["trip_date"]),
            str(int(day["trip_count"])),
            f"${float(day['total_price']):.2f}",
        ])
    draw_table(["", "Date", "Trips", "Total Price"], rows)

    print()
    choice = check_escape(input("\tPick a day [1-{}]: ".format(len(recent))).strip())

    if not choice.isdigit() or not (1 <= int(choice) <= len(recent)):
        print("\tInvalid choice.")
        input("\tPress Enter to go back...")
        return
    
    selected = recent[int(choice) - 1]
    selected_date = str(selected["trip_date"])

    clear()
    header()
    print(f"\tSelected: {format_date_display(selected_date)}")
    print("-" * 40)

    trips = get_trips_by_date(selected_date)

    rows = []
    for t in trips:
        rows.append([
            t["mode_of_transport"],
            t["starting_location"],
            t["ending_location"],
            f"${float(t['total_price']):.2f}",
        ])

    draw_table(["Mode of Transport", "Starting Location", "Ending Location", "Total Price"], rows)

    total_per_day = sum(float(t["total_price"]) for t in trips)
    print(f"\n]\t{len(trips)} trips\t|\t${total_per_day:.2f} per day")

    print()
    print("\tCopy to which dates?")
    dates = collect_dates()

    if not dates:
        input("\tNo dates entered. Press Enter to go back...")
        return
    
    clear()
    header()
    print("\tConfirm Repeat")
    print("-" * 40)
    print()

    confirm_rows = []
    for d in dates:
        confirm_rows.append([
            format_date_display(d),
            str(len(trips)),
            f"${total_per_day:.2f}",
        ])
    draw_table(["Date", "Trips", "Total"], confirm_rows)

    grand_total = total_per_day * len(dates)
    total_trips = len(trips) * len(dates)
    print(f"\n\t{total_trips} trips across {len(dates)} days\t|\t${grand_total:.2f} total")
    print()
    if not confirm_prompt("\tSave all? (yes/no): "):
        input("\tCancelled. Press Enter to go back...")
        return
    
    bulk = []
    for d in dates:
        for t in trips:
            bulk.append((
                t["mode_of_transport"],
                t["starting_location"],
                t["ending_location"],
                float(t["total_price"]),
                d,
            ))

    count = insert_trips_bulk(bulk)
    print(f"\n\t✓ {count} trips saved across {len(dates)} days")
    input("\tPress Enter to go back...")