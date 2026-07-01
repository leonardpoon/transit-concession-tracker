from datetime import datetime, date

from config import CURRENT_CONCESSION_THRESHOLD, DEFAULT_CYCLE_RESET_DAY
from utils import (
    header, clear, draw_table, confirm_prompt, check_escape,
    EscapeToMenu, format_date_display,
)
from db.queries import get_all_periods, add_concession_period, update_period

_NOCHANGE = object()


def manage_periods():
    """Menu option: view, add, or edit concession periods."""
    try:
        while True:
            clear()
            header()
            print("\tManage Concession Periods")
            print("\t" + "-" * 40)
            print("\t[1] View all periods")
            print("\t[2] Add new period")
            print("\t[3] Edit a period")
            print("\t[e] Back to main menu")
            print()
            choice = check_escape(input("\tChoice: "))

            if choice == "1":
                _view_periods()
            elif choice == "2":
                _add_period()
            elif choice == "3":
                _edit_period()

            input("\n\tPress Enter to continue...")
    except EscapeToMenu:
        return


def _view_periods():
    periods = get_all_periods()
    headers = ["ID", "Start", "End", "Reset Day", "Threshold", "Label"]
    rows = []
    for p in periods:
        end_str = format_date_display(p["end_date"]) if p["end_date"] else "(active)"
        rows.append([
            p["id"],
            format_date_display(p["start_date"]),
            end_str,
            p["cycle_reset_day"],
            f"${float(p['threshold_amount']):.2f}",
            p["label"] or "",
        ])
    draw_table(headers, rows)
    return periods


def _prompt_date(message, default=None):
    while True:
        raw = check_escape(input(message)).strip()
        if raw == "" and default is not None:
            return default
        try:
            return datetime.strptime(raw, "%d-%m-%Y").date()
        except ValueError:
            print(f"\tInvalid format. Use DD-MM-YYYY e.g. {date.today().strftime('%d-%m-%Y')}")


def _add_period():
    print("\n\tAdd New Concession Period")
    print("\tType e at any prompt to cancel.\n")

    today_str = date.today().strftime("%d-%m-%Y")
    start = _prompt_date(f"\tStart date (DD-MM-YYYY) [default today {today_str}]: ",
                          default=date.today())

    reset_day_raw = check_escape(
        input(f"\tCycle reset day (1-28) [default {DEFAULT_CYCLE_RESET_DAY}]: ")
    ).strip()
    try:
        reset_day = int(reset_day_raw) if reset_day_raw else DEFAULT_CYCLE_RESET_DAY
        if not (1 <= reset_day <= 28):
            raise ValueError
    except ValueError:
        print("\tInvalid reset day, must be between 1 and 28.")
        return

    threshold_raw = check_escape(
        input(f"\tConcession threshold ($) [default {CURRENT_CONCESSION_THRESHOLD:.2f}]: ")
    ).strip()
    try:
        threshold = float(threshold_raw) if threshold_raw else CURRENT_CONCESSION_THRESHOLD
        if threshold <= 0:
            raise ValueError
    except ValueError:
        print("\tInvalid amount, must be greater than 0.")
        return

    label = check_escape(input("\tLabel (optional, e.g. 'Adult concession'): ")).strip() or None

    print(f"\n\tNew period: starts {format_date_display(start)}, "
          f"resets day {reset_day}, threshold ${threshold:.2f}"
          + (f", label '{label}'" if label else ""))
    print("\tThis will close out whatever period is currently active.")

    if confirm_prompt():
        try:
            add_concession_period(start, reset_day, threshold, label)
            print("\tPeriod added.")
        except ValueError as e:
            print(f"\tCould not add period: {e}")
    else:
        print("\tCancelled.")


def _edit_period():
    periods = _view_periods()
    id_raw = check_escape(input("\n\tEnter period ID to edit: ")).strip()
    try:
        period_id = int(id_raw)
    except ValueError:
        print("\tInvalid ID.")
        return

    match = next((p for p in periods if p["id"] == period_id), None)
    if not match:
        print("\tPeriod not found.")
        return

    print(f"\n\tEditing period {period_id}. Press Enter to keep current value.\n")

    updates = {}

    start_raw = check_escape(
        input(f"\tStart date [{format_date_display(match['start_date'])}]: ")
    ).strip()
    if start_raw:
        try:
            updates["start_date"] = datetime.strptime(start_raw, "%d-%m-%Y").date()
        except ValueError:
            print("\tInvalid start date.")
            return

    end_current = format_date_display(match["end_date"]) if match["end_date"] else "(active)"
    end_raw = check_escape(
        input(f"\tEnd date [{end_current}] (type 'none' to reopen as active): ")
    ).strip()
    if end_raw.lower() == "none":
        updates["end_date"] = None
    elif end_raw:
        try:
            updates["end_date"] = datetime.strptime(end_raw, "%d-%m-%Y").date()
        except ValueError:
            print("\tInvalid end date.")
            return
    # else: leave key absent entirely -> unchanged

    reset_raw = check_escape(
        input(f"\tCycle reset day [{match['cycle_reset_day']}]: ")
    ).strip()
    if reset_raw:
        try:
            reset_day = int(reset_raw)
            if not (1 <= reset_day <= 28):
                raise ValueError
            updates["cycle_reset_day"] = reset_day
        except ValueError:
            print("\tInvalid reset day, must be between 1 and 28.")
            return

    threshold_raw = check_escape(
        input(f"\tThreshold [${float(match['threshold_amount']):.2f}]: ")
    ).strip()
    if threshold_raw:
        try:
            threshold = float(threshold_raw)
            if threshold <= 0:
                raise ValueError
            updates["threshold_amount"] = threshold
        except ValueError:
            print("\tInvalid amount, must be greater than 0.")
            return

    label_raw = check_escape(
        input(f"\tLabel [{match['label'] or ''}]: ")
    ).strip()
    if label_raw:
        updates["label"] = label_raw

    if not updates:
        print("\tNo changes made.")
        return

    if confirm_prompt("\tSave changes? (yes/no): "):
        try:
            update_period(period_id, **updates)
            print("\tPeriod updated.")
        except ValueError as e:
            print(f"\tCould not update period: {e}")
    else:
        print("\tCancelled.")
