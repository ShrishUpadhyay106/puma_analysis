"""
data_cleaner.py
---------------
Loads the raw Puma CSV, cleans it, derives calculated columns,
and returns ready-to-use DataFrames for the Streamlit dashboard.
"""

import pandas as pd
import numpy as np


RAW_PATH = "data/Puma-Dashboard-START.csv"


# ─────────────────────────────────────────────
# 1. LOAD
# ─────────────────────────────────────────────
def load_raw(path: str = RAW_PATH) -> pd.DataFrame:
    """
    Read the CSV, skipping the first 4 title/blank rows so that
    row index 4 (0-based) becomes the header.
    """
    df = pd.read_csv(
        path,
        skiprows=4,           # skip blank rows + title row
        encoding="utf-8-sig",
        dtype=str,            # keep everything as string until we clean
    )
    df.columns = df.columns.str.strip()
    return df


# ─────────────────────────────────────────────
# 2. CLEAN
# ─────────────────────────────────────────────
def _clean_currency(series: pd.Series) -> pd.Series:
    """Remove $, commas, spaces then cast to float."""
    return (
        series.astype(str)
        .str.replace(r"[$,\s]", "", regex=True)
        .replace("", np.nan)
        .astype(float)
    )


def _clean_percent(series: pd.Series) -> pd.Series:
    """Remove % then cast to float (0-100 scale)."""
    return (
        series.astype(str)
        .str.replace("%", "", regex=False)
        .str.strip()
        .replace("", np.nan)
        .astype(float)
    )


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full cleaning pipeline:
      - Drop completely empty rows
      - Strip whitespace from all string columns
      - Parse Invoice Date to datetime (DD-MM-YYYY format)
      - Parse numeric columns (price, units, totals, margin)
      - Recalculate Total Sales = Units Sold × Price per Unit
      - Drop duplicate rows
      - Reset index
    """
    # Drop rows where ALL cells are empty/NaN
    df = df.dropna(how="all").copy()

    # Strip whitespace from object columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    # Drop rows where Retailer is blank (leftover header artefacts)
    df = df[df["Retailer"].notna() & (df["Retailer"] != "")]

    # ── Dates ──────────────────────────────────
    df["Invoice Date"] = pd.to_datetime(
        df["Invoice Date"], format="%d-%m-%Y", errors="coerce"
    )

    # ── Numeric columns ────────────────────────
    df["Price per Unit"] = _clean_currency(df["Price per Unit"])
    df["Units Sold"]     = _clean_currency(df["Units Sold"])   # has commas
    df["Total Sales"]    = _clean_currency(df["Total Sales"])
    df["Operating Profit"] = _clean_currency(df["Operating Profit"])
    df["Operating Margin"] = _clean_percent(df["Operating Margin"])

    # ── Retailer ID → int ──────────────────────
    df["Retailer ID"] = (
        df["Retailer ID"]
        .str.replace(",", "", regex=False)
        .replace("", np.nan)
        .astype("Int64")
    )

    # ── Recalculate Sales (Step 3 of analysis) ──
    df["Calculated Sales"] = df["Units Sold"] * df["Price per Unit"]

    # ── Derived time columns ───────────────────
    df["Year"]  = df["Invoice Date"].dt.year
    df["Month"] = df["Invoice Date"].dt.month
    df["Month Name"] = df["Invoice Date"].dt.strftime("%b")

    # ── Drop duplicates ────────────────────────
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    after = len(df)
    print(f"[clean] Duplicates removed: {before - after}")
    print(f"[clean] Final shape: {df.shape}")
    print(f"[clean] Missing values:\n{df.isnull().sum()}\n")

    return df


# ─────────────────────────────────────────────
# 3. SUMMARY HELPERS (Step 4)
# ─────────────────────────────────────────────
def summary_by(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """Total sales, total units, avg margin grouped by any column."""
    return (
        df.groupby(group_col, observed=True)
        .agg(
            Total_Sales=("Total Sales", "sum"),
            Total_Units=("Units Sold", "sum"),
            Total_Profit=("Operating Profit", "sum"),
            Avg_Margin=("Operating Margin", "mean"),
            Transactions=("Total Sales", "count"),
        )
        .sort_values("Total_Sales", ascending=False)
        .reset_index()
    )


def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly aggregated sales across all years."""
    grp = (
        df.groupby(["Year", "Month", "Month Name"], observed=True)
        .agg(Total_Sales=("Total Sales", "sum"), Total_Units=("Units Sold", "sum"))
        .reset_index()
        .sort_values(["Year", "Month"])
    )
    grp["Period"] = grp["Month Name"].astype(str) + " " + grp["Year"].astype(str)
    return grp


# ─────────────────────────────────────────────
# 4. ENTRY POINT
# ─────────────────────────────────────────────
def get_clean_data(path: str = RAW_PATH) -> pd.DataFrame:
    """One-call helper used by the Streamlit app."""
    return clean(load_raw(path))


if __name__ == "__main__":
    df = get_clean_data()
    print(df.head())
    print("\nRetailer summary:")
    print(summary_by(df, "Retailer"))
