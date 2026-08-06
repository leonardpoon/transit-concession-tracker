from datetime import date, timedelta

from config import MONTHS
from db.queries import delete_trip, get_cycle_summary, get_trips_by_cycle
from utils import (
    check_escape, clear, confirm_prompt, draw_table, format_date_display,
    format_trip_id, get_current_cycle, header, resolve_trip_id
)


def monthly_summary():
    cycle_start, cycle_end, threshold, label = get_current_cycle()

    while True:
        clear()
        header()

        summary = get_cycle_summary(cycle_start, cycle_end)
        total   = float(summary["total"]       or 0)
        trips   = int(summary["trip_count"]    or 0)
        buses   = int(summary["bus_count"]     or 0)
        trains  = int(summary["train_count"]   or 0)
        diff    = total - threshold

        cycle_str = (
            f"{cycle_start.strftime('%d %b')} - "
            f"{cycle_end.strftime('%d %b %Y')}"
        )

        print(f"\tCycle: {cycle_str}" + (f"  ({label})" if label else ""))
        print("-" * 40)
        print(f"\tTotal spent : ${total:.2f} / ${threshold:.2f}")

        if diff >= 0:
            print(f"\tSavings :\t +${diff:.2f}\t(concession Profited!)")
        else:
            print(f"\tRemaining :\t ${abs(diff):.2f} to break even")

        print(f"\tTotal trips :\t {trips}")
        print(f"\tBus trips   :\t {buses}")
        print(f"\tTrain trips :\t {trains}")

        if buses > trains:
            print(f"\tFavoured  :\t Bus")
        elif trains > buses:
            print(f"\tFavoured  :\t Train")
        else:
            print(f"\tFavoured  :\t Tied")

        print()

        rows = get_trips_by_cycle(cycle_start, cycle_end)
        if not rows:
            print("\tNo trips this month.")
        else:
            table_rows = []
            for row in rows:
                table_rows.append([
                    format_trip_id(row),
                    row["mode_of_transport"],
                    row["starting_location"],
                    row["ending_location"],
                    f"${float(row['total_price']):.2f}",
                    format_date_display(row["date"]),
                ])
            draw_table(["ID", "Mode of Transport", "Starting Location", "Ending Location", "Total Price", "Date"], table_rows)

        print()
        print("\t[P] Prev month\t[N] Next month\t[D] Delete trip\t[B] Back")
        print()
        choice = check_escape(input("\tChoice: ").strip().lower())

        if choice == "b" or choice == "":
            break
        elif choice == "p":
            cycle_start, cycle_end, threshold, label = get_current_cycle(cycle_start - timedelta(days=1))
        elif choice == "n":
            if cycle_end >= date.today():
                input("\tAlready on current cycle. Press Enter...")
                continue
            cycle_start, cycle_end, threshold, label = get_current_cycle(cycle_end + timedelta(days=1))
        elif choice == "d":
            if not rows:
                input("\tNo trips to delete. Press Enter...")
                continue

            trip_id_input = check_escape(
                input("\tEnter trip ID to delete (or press Enter to cancel): ").strip()
            )
            if trip_id_input == "":
                continue

            trip_id = resolve_trip_id(rows, trip_id_input)
            if trip_id is None:
                input("\tTrip not found in this cycle. Press Enter...")
                continue

            selected = next(r for r in rows if r["id"] == trip_id)
            if confirm_prompt(f"\tDelete {format_trip_id(selected)}? (yes/no): "):
                if delete_trip(trip_id):
                    input("\tTrip deleted. Press Enter...")
                else:
                    input("\tCould not delete trip. Press Enter...")
