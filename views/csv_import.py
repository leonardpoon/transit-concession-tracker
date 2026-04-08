import csv
from datetime import datetime
from pathlib import Path

from db.queries import insert_trips_bulk
from utils import clear, confirm_prompt, draw_table, header, check_escape

DATE_FORMATS = [
    "%d-%m-%Y",
    "%Y-%m-%sd",
    "%d/%m/%Y",
    "%d/%m/%y",
    "%d-%b-%Y",
    "%d-%b-%y",
]

def _parse_date(raw):
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {raw!r}")

def _parse_fare(raw):
    return float(raw.strip().replace("$", "").replace(",", ""))

def csv_import():
    clear()
    header()
    print("\tImport from CSV")
    print("-" * 40)
    print()
    print("\tExpected CSV column headers:")
    print("\tMode of Transport, Starting Location, Ending Location, Total Price, Date")
    print()
    print("\tSupported date formats:")
    print("]\tDD-MM-YYYY, YYYY-MM-DD, DD/MM/YYYY, DD-MMM-YYYY")
    print()

    path_input = check_escape(input("\tEnter full path to CSV file: ").strip())
    if path_input == "":
        input("\tNo path entered. Press Enter to go back...")
        return
    
    path = Path(path_input)

    if not path.exists():
        print(f"\n\tFile not found: {path}")
        input("\tPress Enter to go back...")
        return
    
    if path.suffix.lower() != ".csv":
        print("\tOnly CSV files are supported.")
        print("\tIn Excel: File → Save As → Choose 'CSV (Comma delimited) (*.csv)'")
        input("\tPress Enter to go back...")
        return
    
    valid_trips = []
    skipped = []

    try:
        with open(path, newline = "", encoding = "utf-8") as f:
            reader = csv.DictReader(f)

            for i, row in enumerate(reader, 1):
                try:
                    mode = row.get("Mode of Transport", "").strip()
                    origin = row.get("Starting Location", "").strip()
                    destination = row.get("Ending Location", "").strip()
                    fare_raw = _parse_fare(row.get("Total Price", ""))
                    date_raw = _parse_date(row.get("Date", ""))

                    if not all([mode, origin, destination, fare_raw, date_raw]):
                        skipped.append((i, "Missing fields"))
                        continue

                    if mode not in ("Bus", "Train"):
                        skipped.append((i, f"Invalid mode; {mode!r}"))
                        continue

                    fare = _parse_fare(fare_raw)
                    trip_date = _parse_date(date_raw)

                    valid_trips.append((mode, origin, destination, fare, trip_date))

                except Exception as e:
                    skipped.append((i, str(e)))

    except Exception as e:
        print(f"\n\tCould not read file: {e}")
        input("\tPress Enter to go back...")
        return
    
    clear()
    header()
    print("\tImport Preview")
    print("-" * 40)

    if not valid_trips:
        print("\n\tNo valid trips found in file.")
        if skipped:
            print(f"\t{len(skipped)} rows had errors")
            for row_num, reason in skipped[:5]:
                print(f"\tRow{row_num}: {reason}")
        input("\tPress Enter to go back...")
        return
    
    preview = valid_trips[:5]
    rows = []
    for t in preview:
        rows.append([t[0], t[1], t[2], f"${t[3]:.2f}", t[4]])
    draw_table(["Mode of Transport", "Starting Location", "Ending Location", "Total Price", "Date"], rows)

    if len(valid_trips) > 5:
        print(f"\n\t ... and {len(valid_trips) - 5} more trips")
    
    print(f"\n\tReady to import: {len(valid_trips)} trips")

    if skipped:
        print(f"\tSkipped: {len(skipped)} rows")
        show = check_escape(input("\tShow skipped rows? (yes/no): ").strip().lower())
        if show in ("yes", "y"):
            for row_num, reason in skipped:
                print(f"\tRow{row_num}: {reason}")
            print()

    print()
    if not confirm_prompt("\tImport all valid trips? (yes/no): "):
        input("\tCancelled. Press Enter to go back...")
        return
    
    count = insert_trips_bulk(valid_trips)
    print(f"\n\t✓ {count} trips imported successfully!")
    input("\tPress Enter to go back...")