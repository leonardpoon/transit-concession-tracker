import os
from datetime import date

from config import CONCESSION_THRESHOLD, MONTHS
from db.queries import get_monthly_summary

def clear():
    os.system('cls')

def header():
    print("=" * 40)
    print("  Transit Tracker  ")
    print("=" * 40)

def show_monthly_status():
    today = date.today()
    summary = get_monthly_summary(today.year, today.month)
    total = float(summary["total"] or 0)
    diff = total - CONCESSION_THRESHOLD

    print(f"\t{MONTHS[today.month]} {today.year}")
    print(f"\t${total:.2f} / ${CONCESSION_THRESHOLD:.2f}")

    if diff >= 0 :
        print(f"\tConcession Covered! Saved {diff:.2f}")
    else:
        print(f"\tNeed ${abs(diff):.2f} more to break even")
    print()

def draw_table(headers, rows):

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    separator = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
    top        = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
    bottom     = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"

    header_row = "│" + "│".join(
        f" {h:<{col_widths[i]}} " for i, h in enumerate(headers)
    ) + "│"

    print(top)
    print(header_row)
    print(separator)

    if not rows:
        empty_msg = "No data found"
        total_width = sum(col_widths) + (3 * len(col_widths)) + 1
        print("│" + empty_msg.center(total_width - 2) + "│")
    else:
        for row in rows:
            print("│" + "│".join(
                f" {str(cell):<{col_widths[i]}} "
                for i, cell in enumerate(row)
            ) + "│")

    print(bottom)

def format_date_display(trip_date):
    from datetime import datetime, date
    if isinstance(trip_date, date):
        dt = trip_date
    else:
        dt = datetime.strptime(str(trip_date), "%Y-%m-%d").date()
    return dt.strftime("%a %d-%m-%Y")


def collect_dates():
    print()
    print("  Enter dates one per line (DD-MM-YYYY).")
    print("  Press Enter twice when done.")
    print()

    dates = []
    while True:
        entry = input("  > ").strip()
        if entry == "":
            if dates:
                break
            else:
                print("  Please enter at least one date.")
            continue
        try:
            from datetime import datetime
            dt = datetime.strptime(entry, "%d-%m-%Y")
            mysql_date = dt.strftime("%Y-%m-%d")
            dates.append(mysql_date)
            print(f"  ✓ Added {format_date_display(mysql_date)}")
        except ValueError:
            print("  Invalid format. Use DD-MM-YYYY e.g. 07-04-2026")

    return dates