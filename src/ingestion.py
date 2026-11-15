
import csv
import math
import os
from datetime import datetime

# Q1: Read and validate rainfall data

months = [
    "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
    "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
]

valid_data = []
invalid_data = []
seen_years = set()

input_file = "data/raw/Kerala-Rainfall-Historical.csv"

try:
    with open(input_file, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV is empty")

        reader.fieldnames = [
            name.strip().upper() for name in reader.fieldnames
        ]

        for line_number, row in enumerate(reader, start=2):
            try:
                year = int(row["YEAR"])

                if year < 1901 or year > 2017:
                    raise ValueError("Invalid year")

                if year in seen_years:
                    raise ValueError("Duplicate year")

                rainfall = []

                for month in months:
                    value = float(row[month])

                    if not math.isfinite(value):
                        raise ValueError("Invalid rainfall value")

                    if value < 0:
                        raise ValueError("Negative rainfall")

                    rainfall.append(value)

                # Calculate rainfall totals
                annual = sum(rainfall)
                sw = sum(rainfall[5:9])
                ne = sum(rainfall[9:12])

                clean_row = {"YEAR": year}

                for month, value in zip(months, rainfall):
                    clean_row[month] = value

                clean_row["ANNUAL"] = round(annual, 2)
                clean_row["SW_Monsoon"] = round(sw, 2)
                clean_row["NE_Monsoon"] = round(ne, 2)

                valid_data.append(clean_row)
                seen_years.add(year)

            except (ValueError, TypeError, KeyError) as error:
                invalid_data.append(
                    (line_number, str(error))
                )

except (FileNotFoundError, ValueError) as error:
    print("Error reading dataset:", error)
    raise SystemExit(1)


print("Valid records:", len(valid_data))
print("Invalid records:", len(invalid_data))


# Q2: Export cleaned CSV and audit log

os.makedirs("data/processed", exist_ok=True)

clean_file = "data/processed/clean_kerala_monsoon.csv"

columns = (
    ["YEAR"] + months +
    ["ANNUAL", "SW_Monsoon", "NE_Monsoon"]
)

with open(clean_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(valid_data)

print("Clean CSV created successfully!")


# Generate audit log

log_file = "data/processed/monsoon_ingestion_audit.log"

with open(log_file, "w", encoding="utf-8") as file:
    file.write("KERALA MONSOON INGESTION AUDIT\n")
    file.write(f"Date: {datetime.now()}\n")
    file.write(f"Total records: {len(valid_data) + len(invalid_data)}\n")
    file.write(f"Valid records: {len(valid_data)}\n")
    file.write(f"Invalid records: {len(invalid_data)}\n")

    if valid_data:
        years = [row["YEAR"] for row in valid_data]
        file.write(f"Year coverage: {min(years)} - {max(years)}\n")

        missing_years = [
            year for year in range(1901, 2018)
            if year not in seen_years
        ]
        file.write(f"Missing years: {missing_years}\n")

    file.write("\nRejected Records:\n")

    for line_number, error in invalid_data:
        file.write(f"Line {line_number}: {error}\n")



