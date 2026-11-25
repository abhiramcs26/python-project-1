import csv
import math
import os
from datetime import datetime
import numpy as np
import pandas as pd

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

''' '''


class MonsoonEpochAnalyzer:
    def __init__(self):
     self._data = None
     self._spi = None

    def load_from_csv(self, filepath: str = "data/processed/clean_kerala_monsoon.csv") -> None:
     self._data = pd.read_csv(filepath)
     self._spi = None

    def compute_spi(self, window_years: int = 30, column: str = "ANNUAL") -> np.ndarray:
     #Rolling window starts after 30 years
     #The Annual Rainfall row is used to calculate the spi
     if window_years <= 0:
        raise ValueError("window_years must be greater than 0.")
     if self._data is None:
        raise RuntimeError("No data loaded. Call load_from_csv() first.")

     values = self._data[column].to_numpy(dtype=float)
     #Temp means temporary here , not temprature
     spi_temp = []

     for i in range(len(values)):
        if i < window_years - 1:
         spi_temp.append(np.nan)
         continue

        window = values[i - window_years + 1 : i + 1]

        mean = np.mean(window)
        std = np.std(window)

        if std == 0:
         spi_temp.append(0.0)
        else:
         spi_temp.append((values[i] - mean) / std)

     self._spi = np.array(spi_temp, dtype=float)
     return self._spi.copy()

    def summary_report(self, column: str = "ANNUAL") -> str:
     if self._data is None:
        return "No data loaded."

     values = self._data[column]
     total_rain = values.sum()
     mean_rain = values.mean()
     std_rain = values.std()

     lines = [
        "=== Monsoon Epoch Summary Report ===",
        f"Years Covered : {int(self._data['YEAR'].min())} - {int(self._data['YEAR'].max())} ({len(self._data)} records)",
        f"Total Rainfall: {total_rain:.2f} mm",
        f"Mean Rainfall : {mean_rain:.2f} mm",
        f"Std Deviation : {std_rain:.2f} mm",
        ]

     if self._spi is not None:
        lines.append(f"Mean SPI      : {np.nanmean(self._spi):.4f}")
        lines.append(f"Min / Max SPI : {np.nanmin(self._spi):.4f} / {np.nanmax(self._spi):.4f}")
     else:
        lines.append("SPI           : Not computed yet (call compute_spi())")

     return "\n".join(lines)


if __name__ == "__main__":
    analyzer = MonsoonEpochAnalyzer()
    analyzer.load_from_csv("data/processed/clean_kerala_monsoon.csv")
    spi = analyzer.compute_spi(window_years=30)
    print(analyzer.summary_report())



