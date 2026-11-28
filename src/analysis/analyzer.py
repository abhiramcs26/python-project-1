import numpy as np
import pandas as pd


def comparator(df: pd.DataFrame) -> dict[str, bool]:
    months = [
     "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
     "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
    ]
    
    raw_arr = df[months].to_numpy(dtype=float)
    #Computed values
    comp_annual = np.sum(raw_arr, axis=1)
    comp_sw = np.sum(raw_arr[:, 5:9], axis=1) #JUN, JUL, AUG, SEP are sw monsoon
  
    #Real values
    csv_annual = df["ANNUAL"].to_numpy(dtype=float)
    csv_sw = df["SW_Monsoon"].to_numpy(dtype=float)

    print("=== Annual & SW Monsoon Comparison ===")
    print(f"Annual Total     -> Calculated: {np.sum(comp_annual):.2f} mm | CSV: {np.sum(csv_annual):.2f} mm")
    print(f"SW Monsoon Total -> Calculated: {np.sum(comp_sw):.2f} mm | CSV: {np.sum(csv_sw):.2f} mm")

    annual_confirm = bool(np.allclose(comp_annual, csv_annual))
    sw_match = bool(np.allclose(comp_sw, csv_sw))

    return {
     "annual_match": annual_confirm,
     "sw_monsoon_match": sw_match,
    }


if __name__ == "__main__":
    df = pd.read_csv("data/processed/clean_kerala_monsoon.csv")
    results = comparator(df)
    print(f"Annual totals match CSV    : {results['annual_match']}")
    print(f"SW Monsoon totals match CSV: {results['sw_monsoon_match']}")

def rolling_analysis(df):
    df = df.sort_values("YEAR")
    rolling_mean = df["SW_Monsoon"].rolling(10).mean()
    rolling_std = df["SW_Monsoon"].rolling(10).std()
    print(rolling_mean.isna().sum())
    print(rolling_std.isna().sum())
    rolling_mean = rolling_mean.bfill()
    rolling_std = rolling_std.bfill()
    print("Rolling Mean:")
    print(rolling_mean)
    print("Rolling Standard Deviation:")
    print(rolling_std)
    return rolling_mean, rolling_std
bins = [1900, 1930, 1960, 1990, 2017]
labels = [
    "1901-1930",
    "1931-1960",
    "1961-1990",
    "1991-2017"
]
def calculate_cv(x):
    return (x.std() / x.mean()) * 100
def epoch_analysis(df):
    df = df.sort_values("YEAR")
    df["Epoch"] = pd.cut(df["YEAR"], bins=bins, labels=labels)
    grouped = df.groupby("Epoch")[["SW_Monsoon", "NE_Monsoon"]]
    mean = grouped.mean()
    std = grouped.std()
    cv = (std / mean) * 100
    print("Mean:")
    print(mean)
    print("Standard Deviation:")
    print(std)
    print("Coefficient of Variation (%):")
    print(cv)
    summary = grouped.agg(["mean", "std", calculate_cv])
    print("Epoch Summary:")
    print(summary)
    print("Seasonal Pivot Table:")
    pivot = pd.pivot_table(
        df,
        index="Epoch",
        values=["SW_Monsoon", "NE_Monsoon"],
        aggfunc=["mean", "std", calculate_cv],
        margins=True,
        observed=True
    )
    print(pivot.round(2))
    return pivot
rolling_analysis(df)
epoch_analysis(df)