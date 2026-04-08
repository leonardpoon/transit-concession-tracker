from datetime import date

from config import CONCESSION_THRESHOLD, MONTHS
from db.queries import delete_trip, get_monthly_summary, get_trips_by_month
from utils import clear, draw_table, format_date_display, header, check_escape


def monthly_summary():
    today = date.today()
    year, month = today.year, today.month

    while True:
        clear()
        header()

        summary = get_monthly_summary(year, month)
        total   = float(summary["total"]       or 0)
        trips   = int(summary["trip_count"]    or 0)
        buses   = int(summary["bus_count"]     or 0)
        trains  = int(summary["train_count"]   or 0)
        diff    = total - CONCESSION_THRESHOLD

        print(f"\t{MONTHS[month]} {year}")
        print("-" * 40)
        print(f"\tTotal spent : ${total:.2f} / ${CONCESSION_THRESHOLD:.2f}")

        if diff >= 0:
            print(f"\tSavings\t: +${diff:.2f}\t(concession covered!)")
        else:
            print(f"\tRemaining\t: ${abs(diff):.2f} to break even")

        print(f"\tTotal trips : {trips}")
        print(f"\tBus trips   : {buses}")
        print(f"\tTrain trips : {trains}")

        if buses > trains:
            print(f"\tFavoured\t: Bus")
        elif trains > buses:
            print(f"\tFavoured\t: Train")
        else:
            print(f"\tFavoured\t: Tied")

        print()

        rows = get_trips_by_month(year, month)
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
                    format_date_display(row["trip_date"]),
                ])
            draw_table(["ID", "Mode of Transport", "Starting Location", "Ending Location", "Total Price", "Date"], table_rows)

        print()
        print("\t[P] Prev month\t[N] Next month\t[D] Delete trip]\t[B] Back")
        print()
        choice = check_escape(input("\tChoice: ").strip().lower())

        if choice == "b" or choice == "":
            break
        elif choice == "p":
            if month == 1:
                month = 12
                year -= 1
            else:
                month -= 1
        elif choice == "n":
            if year == today.year and month == today.month:
                input("\tAlready on current month. Press Enter...")
            elif month == 12:
                month = 1
                year += 1
            else:
                month += 1
        elif choice == "d":
            trip_id = check_escape(input("\tEnter trip ID to delete (e.g. 3): ").strip())
            try:
                if delete_trip(int(trip_id)):
                    print(f"\t✓ Trip #{trip_id} deleted.")
                else:
                    print("\tTrip not found.")
            except ValueError:
                print("\tInvalid ID.")
            input("\tPress Enter to continue...")
        else:
            input("\tInvalid choice. Press Enter to try again...")