from datetime import datetime
from pathlib import Path

from db.queries import insert_trips_bulk
from utils import check_escape, clear, confirm_prompt, draw_table, format_date_display, header, EscapeToMenu


def csv_import():
    clear()
    header()
    print("\tImport from Excel")
    print("-" * 40)
    print()
    print("\tThis imports directly from your .xlsm or .xlsx file.")
    print("\tEach monthly sheet will be imported automatically.")
    print()

    path_input = check_escape(
        input("\tEnter full path to Excel file: ").strip().strip('"')
    )

    if path_input == "":
        input("\tNo path entered. Press Enter to go back...")
        return

    path = Path(path_input)

    if not path.exists():
        print(f"\n\tFile not found: {path}")
        input("\tPress Enter to go back...")
        return

    if path.suffix.lower() not in (".xlsm", ".xlsx"):
        print(f"\tOnly .xlsm and .xlsx files are supported.")
        input("\tPress Enter to go back...")
        return

    try:
        from openpyxl import load_workbook
        wb = load_workbook(path, read_only=True, data_only=True)
    except Exception as e:
        print(f"\n\tCould not open file: {e}")
        input("\tPress Enter to go back...")
        return

    skip_sheets = {"data entry", "summary", "overview", "dashboard"}
    data_sheets = [s for s in wb.sheetnames if s.lower() not in skip_sheets]

    if not data_sheets:
        print("\n\tNo monthly sheets found.")
        input("\tPress Enter to go back...")
        return

    print(f"\n\tFound {len(data_sheets)} sheet(s): {', '.join(data_sheets)}")
    print()

    valid_trips = []
    skipped     = []

    for sheet_name in data_sheets:
        ws   = wb[sheet_name]
        rows = list(ws.iter_rows(values_only=True))

        if not rows:
            continue

        header_row = None
        data_start = 0
        for i, row in enumerate(rows):
            if row[0] == "Mode of Transport":
                header_row = row
                data_start = i + 1
                break

        if header_row is None:
            skipped.append((sheet_name, "Header row not found"))
            continue

        for i, row in enumerate(rows[data_start:], 1):
            try:
                mode        = row[0]
                origin      = row[1]
                destination = row[2]
                price       = row[3]
                date        = row[4]

                if not mode or not origin or not destination:
                    continue
                if mode not in ("Bus", "Train"):
                    continue

                origin      = str(origin).strip()
                destination = str(destination).strip()
                price       = 0.0 if str(price).strip() == "-" else float(price)

                if isinstance(date, datetime):
                    date_str = date.strftime("%Y-%m-%d")
                else:
                    date_str = datetime.strptime(
                        str(date).strip(), "%Y-%m-%d"
                    ).strftime("%Y-%m-%d")

                valid_trips.append((mode, origin, destination, price, date_str))

            except Exception as e:
                skipped.append((f"{sheet_name} row {i}", str(e)))

    # All sheets parsed — now preview and confirm
    if not valid_trips:
        print("\n\tNo valid trips found.")
        if skipped:
            for loc, reason in skipped[:5]:
                print(f"\t  {loc}: {reason}")
        input("\n\tPress Enter to go back...")
        return

    clear()
    header()
    print("\tImport Preview")
    print("-" * 40)
    print()

    preview_rows = []
    for t in valid_trips[:5]:
        preview_rows.append([
            t[0], t[1], t[2],
            f"${t[3]:.2f}",
            format_date_display(t[4]),
        ])
    draw_table(["Mode", "From", "To", "Price", "Date"], preview_rows)

    if len(valid_trips) > 5:
        print(f"\n\t... and {len(valid_trips) - 5} more trips")

    print(f"\n\tReady to import: {len(valid_trips)} trips")

    if skipped:
        print(f"\tSkipped: {len(skipped)} rows")
        try:
            if confirm_prompt("\tShow skipped rows? (yes/no): "):
                for loc, reason in skipped:
                    print(f"\t  {loc}: {reason}")
                print()
        except EscapeToMenu:
            raise

    print()
    if not confirm_prompt("\tImport all valid trips? (yes/no): "):
        input("\tCancelled. Press Enter to go back...")
        return

    count = insert_trips_bulk(valid_trips)
    print(f"\n\t✓ {count} trips imported successfully!")
    input("\tPress Enter to go back...")