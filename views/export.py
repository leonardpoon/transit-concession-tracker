import csv
from datetime import datetime, date
from pathlib import Path

from db.queries import get_all_trips, search_trips
from utils import check_escape, clear, confirm_prompt, draw_table, header, EscapeToMenu

def export():
    clear()
    header()
    print("\tExport to CSV")
    print("-" * 40)
    print()
    print("\tWhat do you want to export?")
    print()
    print("\t[1] All Trips")
    print("\t[2] Specific Month")
    print("\t[3] Specific Year")
    print()

    choice = check_escape(input("\tChoice: ").strip())

    trips = []

    if choice == "1":
        trips = get_all_trips()

    elif choice == "2":
        try:
            month_input = check_escape(input(f"\tMonth (MM-YYYY e.g. {datetime.now().strftime('%m-%Y')}): ").strip())
            dt = datetime.strptime(month_input, "%m-%Y")
            trips = search_trips(
                start_date = dt.strftime("%Y-%m-01"),
                end_date = dt.strftime("%Y-%m-31"),
            )
        except EscapeToMenu:
            raise
        except ValueError:
            print(f"\tInvalid format. Use MM-YYYY e.g. {datetime.now().strftime('%m-%Y')}")
            input("\tPress Enter to go back")
            return
        
    elif choice == "3":
        try:
            year_input = check_escape(input(f"\tYear (YYYY e.g. {datetime.now().strftime('%Y')}): ").strip())
            year = int(year_input)
            trips = search_trips(
                start_date = f"{year}-01-01",
                end_date = f"{year}-12-31",
            )
        except EscapeToMenu:
            raise
        except ValueError:
            print(f"\tInvalid year.")
            input("\tPress Enter to go back")
            return
        
    else:
        input("\tInvalid choice. Press Enter to go back...")
        return
    
    if not trips:
        print("\n\tNo trips found for that range.")
        input("\tPress Enter to go back...")
        return
    
    clear()
    header()
    print("\tExport Preview")
    print("-" * 40)
    print()

    preview = trips[:5]
    rows = []
    for t in preview:
        rows.append([
            t["mode_of_transport"],
            t["starting_location"],
            t["ending_location"],
            f"${float(t['total_price']):.2f}",
            str(t["date"]),
        ])
    draw_table(["Mode of Transport", "Starting Location", "Ending Location", "Total Price", "Date"], rows)

    if len(trips) > 5:
        print(f"\n\t... and {len(trips) - 5} more trips")

    print(f"\n\tTotal to export: {len(trips)} trips")
    print()

    default_path = str(Path.home() / "Desktop" / "transit_export.csv")
    path_input = check_escape(input(f"\tSave to (Press Enter for Desktop): ").strip())

    if path_input == "":
        path_input = default_path
    
    path = Path(path_input)

    print()
    if not confirm_prompt(f"\tExport {len(trips)} trips to {path.name}? (yes/no): "):
        input("\tCancelled. Press Enter to go back...")
        return
    
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline = "", encoding = "utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Mode of Transport",
                "Starting Location",
                "Ending Location",
                "Total Price",
                "Date",
            ])
            for t in trips:
                writer.writerow([
                    t["mode_of_transport"],
                    t["starting_location"],
                    t["ending_location"],
                    f"{float(t['total_price']):.2f}",
                    str(t["date"]),
                ])
        print(f"\n\t✓ {len(trips)} trips exported to")
        print(f"\t {path}")
    except EscapeToMenu:
        raise
    except PermissionError:
        print(f"\tPermission denied. Is the file open in Excel?")
    except Exception as e:
        print(f"\tError: {e}")
    
    input("\n\tPress Enter to go back...")