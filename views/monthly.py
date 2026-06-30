from datetime import date, timedelta

from config import MONTHS
from db.queries import delete_trip, get_cycle_summary, get_trips_by_cycle
from utils import clear, draw_table, format_date_display, header, check_escape, get_current_cycle


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
                    f"#{row['id']}",
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