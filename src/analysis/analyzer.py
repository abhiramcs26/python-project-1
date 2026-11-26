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
