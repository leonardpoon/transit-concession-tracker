from config import CONCESSION_THRESHOLD, MONTHS
from db.queries import get_months_with_data, get_monthly_summary
from utils import clear, draw_table, header


def all_history():
    clear()
    header()
    print("  All History")
    print("-" * 40)

    months = get_months_with_data()

    if not months:
        print("  No data yet.")
        input("\n  Press Enter to go back...")
        return

    rows = []
    for year, month in months:
        s     = get_monthly_summary(year, month)
        total = float(s["total"]      or 0)
        trips = int(s["trip_count"]   or 0)
        buses = int(s["bus_count"]    or 0)
        trains = int(s["train_count"] or 0)
        diff  = total - CONCESSION_THRESHOLD

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
        ["Month", "Total", "vs $81", "Trips", "Bus", "Train", "Favoured"],
        rows,
    )

    input("\n  Press Enter to go back...")