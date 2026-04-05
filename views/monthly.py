from datetime import date

from config import CONCESSION_THRESHOLD, MONTHS
from db.queries import delete_trip, get_monthly_summary, get_trips_by_month
from utils import clear, draw_table, format_date_display, header


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

        print(f"  {MONTHS[month]} {year}")
        print("-" * 40)
        print(f"  Total spent : ${total:.2f} / ${CONCESSION_THRESHOLD:.2f}")

        if diff >= 0:
            print(f"  Savings     : +${diff:.2f}  (concession covered!)")
        else:
            print(f"  Remaining   : ${abs(diff):.2f} to break even")

        print(f"  Total trips : {trips}")
        print(f"  Bus trips   : {buses}")
        print(f"  Train trips : {trains}")

        if buses > trains:
            print(f"  Favoured    : Bus")
        elif trains > buses:
            print(f"  Favoured    : Train")
        else:
            print(f"  Favoured    : Tied")

        print()

        rows = get_trips_by_month(year, month)
        if not rows:
            print("  No trips this month.")
        else:
            table_rows = []
            for row in rows:
                table_rows.append([
                    f"#{row['id']}",
                    row["mode"],
                    row["origin"],
                    row["destination"],
                    f"${float(row['fare']):.2f}",
                    format_date_display(row["trip_date"]),
                ])
            draw_table(["ID", "Mode", "From", "To", "Fare", "Date"], table_rows)

        print()
        print("  [P] Prev month   [N] Next month   [D] Delete trip   [B] Back")
        print()
        choice = input("  Choice: ").strip().upper()

        if choice == "B" or choice == "":
            break
        elif choice == "P":
            if month == 1:
                month = 12
                year -= 1
            else:
                month -= 1
        elif choice == "N":
            if year == today.year and month == today.month:
                input("  Already on current month. Press Enter...")
            elif month == 12:
                month = 1
                year += 1
            else:
                month += 1
        elif choice == "D":
            trip_id = input("  Enter trip ID to delete (e.g. 3): ").strip()
            try:
                if delete_trip(int(trip_id)):
                    print(f"  ✓ Trip #{trip_id} deleted.")
                else:
                    print("  Trip not found.")
            except ValueError:
                print("  Invalid ID.")
            input("  Press Enter to continue...")
        else:
            input("  Invalid choice. Press Enter to try again...")