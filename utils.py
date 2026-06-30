import os
import difflib
from datetime import date, timedelta

from config import DEFAULT_CONCESSION_THRESHOLD, MONTHS
from db.queries import get_monthly_summary, get_cycle_summary, get_recent_trips, get_active_period

def clear():
    os.system('cls')

def header():
    print("=" * 40)
    print("\tTransit Tracker\t")
    print("=" * 40)

def show_monthly_status():
    cycle_start, cycle_end, threshold, label = get_current_cycle()
    summary = get_cycle_summary(cycle_start, cycle_end)
    total = float(summary["total"] or 0)
    diff = total - threshold

    cycle_str = (
        f"{cycle_start.strftime('%d %b')} - {cycle_end.strftime('%d %b %Y')}"
    )

    print(f"\tCycle: {cycle_str}" + (f"  ({label})" if label else ""))
    print(f"\t${total:.2f} / ${threshold:.2f}")

    if diff >= 0:
        print(f"\tConcession covered! Saved ${diff:.2f}")
    else:
        print(f"\tNeed ${abs(diff):.2f} more to break even!")
    print()

def show_recent_trips():
    trips = get_recent_trips(5)
    if not trips:
        return
    
    print("\tRecent Trips:")
    print("\t" + "-" * 40)
    for t in trips:
        date_str = format_date_display(t["date"])
        mode = t["mode_of_transport"]
        origin = t["starting_location"][:22].ljust(22)
        dest = t["ending_location"][:22].ljust(22)
        price = t["total_price"]
        print(f"\t{date_str}\t{mode:<5}\t{origin:<22} → {dest:<22}\t${price:.2f}")
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
    print("\tEnter dates one per line (DD-MM-YYYY).")
    print("\tPress Enter twice when done.")
    print()

    dates = []
    while True:
        entry = input("\t> ").strip()
        if entry == "":
            if dates:
                break
            else:
                print("\tPlease enter at least one date.")
            continue
        try:
            from datetime import datetime
            dt = datetime.strptime(entry, "%d-%m-%Y")
            mysql_date = dt.strftime("%Y-%m-%d")
            dates.append(mysql_date)
            print(f"\t✓ Added {format_date_display(mysql_date)}")
        except ValueError:
            print(f"\tInvalid format. Use DD-MM-YYYY e.g. {datetime.now().strftime('%d-%m-%Y')}")

    return dates

def confirm_prompt(message="\tConfirm? (yes/no): "):
    while True:
        answer = input(message).strip().lower()
        if answer in ("yes", "y", ""):
            return True
        elif answer in ("no", "n"):
            return False
        else:
            print("\tPlease type yes or no.")


def find_similar_location(name, locations, threshold = 0.8):
    matches = difflib.get_close_matches(name, locations, n = 1, cutoff = threshold)
    if matches:
        return matches[0]
    return None

class EscapeToMenu(BaseException):
    pass

def check_escape(value):
    if value.strip().lower() in ("e", "exit", "quit", "q"):
        raise EscapeToMenu()
    return value

def get_current_cycle(check_date=None):
    if check_date is None:
        check_date = date.today()

    period = get_active_period(check_date)

    if period:
        reset_day = period["cycle_reset_day"]
        threshold = float(period["threshold_amount"])
        label = period.get("label")
    else:
        # Legacy fallback - shouldn't trigger once concession_periods is seeded
        reset_day = 3
        threshold = DEFAULT_CONCESSION_THRESHOLD
        label = None

    if check_date.day < reset_day:
        if check_date.month == 1:
            cycle_start = date(check_date.year - 1, 12, reset_day)
        else:
            cycle_start = date(check_date.year, check_date.month - 1, reset_day)
    else:
        cycle_start = date(check_date.year, check_date.month, reset_day)

    if cycle_start.month == 12:
        next_month, next_year = 1, cycle_start.year + 1
    else:
        next_month, next_year = cycle_start.month + 1, cycle_start.year
    cycle_end = date(next_year, next_month, reset_day) - timedelta(days=1)

    return cycle_start, cycle_end, threshold, label