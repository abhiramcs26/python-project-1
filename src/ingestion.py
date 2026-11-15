
import csv

months = [
    "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
    "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
]
valid_data = []
invalid_data = []
try:
    with open("data/raw/Kerala-Rainfall-Historical.csv",
              "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                year = int(row["YEAR"])
                if year < 1901 or year > 2017:
                    raise ValueError("Invalid year")
                rainfall = []
                for month in months:
                    value = float(row[month])
                    if value < 0:
                        raise ValueError("Negative rainfall")
                    rainfall.append(value)
                valid_data.append(row)
            except (ValueError, TypeError, KeyError) as error:
               invalid_data.append((row, str(error)))
except FileNotFoundError:
    print("Dataset file not found!")
print("Valid records:", len(valid_data))
print("Invalid records:", len(invalid_data))
import os
from datetime import datetime
os.makedirs("data/processed", exist_ok=True)
clean_file = "data/processed/clean_kerala_monsoon.csv"

if valid_data:
    with open(clean_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=valid_data[0].keys())
        writer.writeheader()
        writer.writerows(valid_data)

    print("Clean CSV created successfully!")
else:
    print("No valid records to export.")

# Q2: Generate audit log
log_file = "data/processed/monsoon_ingestion_audit.log"

with open(log_file, "w", encoding="utf-8") as file:
    file.write("KERALA MONSOON INGESTION AUDIT\n")
    file.write(f"Date: {datetime.now()}\n")
    file.write(f"Valid records: {len(valid_data)}\n")
    file.write(f"Invalid records: {len(invalid_data)}\n")

    if valid_data:
        years = [int(row["YEAR"]) for row in valid_data]
        file.write(f"Year coverage: {min(years)} - {max(years)}\n")

    file.write("\nRejected Records:\n")

    for row, error in invalid_data:
        file.write(f"{row} - Reason: {error}\n")

print("Audit log created successfully!")
