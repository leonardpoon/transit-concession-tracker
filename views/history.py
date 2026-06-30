from datetime import date

from config import MONTHS, DEFAULT_CONCESSION_THRESHOLD
from db.queries import get_months_with_data, get_monthly_summary, get_active_period
from utils import clear, draw_table, header


def all_history():
    clear()
    header()
    print("\tAll History")
    print("-" * 40)

    months = get_months_with_data()

    if not months:
        print("\tNo data yet.")
        input("\n\tPress Enter to go back...")
        return

    rows = []
    for year, month in months:
        s     = get_monthly_summary(year, month)
        total = float(s["total"]      or 0)
        trips = int(s["trip_count"]   or 0)
        buses = int(s["bus_count"]    or 0)
        trains = int(s["train_count"] or 0)

        # Each month judged against whichever concession threshold was
        # actually active then, not a single fixed amount.
        period    = get_active_period(date(year, month, 1))
        threshold = float(period["threshold_amount"]) if period else DEFAULT_CONCESSION_THRESHOLD
        diff      = total - threshold

        if diff >= 0:
            diff_str = f"+${diff:.2f}"
        else:
            diff_str = f"-${abs(diff):.2f}"

        if buses > trains:
            favoured = "Bus"
        elif trains > buses:
            favoured = "Train"
        else:
            favoured = "Tied"

        rows.append([
            f"{MONTHS[month]} {year}",
            f"${total:.2f}",
            diff_str,
            str(trips),
            str(buses),
            str(trains),
            favoured,
        ])

    draw_table(
        ["Month", "Total", "Profit", "Total Trips", "Bus", "Train", "Favoured"],
        rows,
    )

    input("\n\tPress Enter to go back...")