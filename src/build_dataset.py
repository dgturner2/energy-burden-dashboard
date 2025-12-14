"""
build_dataset.py 

"""

import pandas as pd

from fetch_bls import load_series_ids, fetch_bls


def period_to_date(year: str, period: str) -> pd.Timestamp:
    """
    Convert BLS year + period (like M01) into a real date.
    We use the first day of each month (YYYY-MM-01).
    
    """
    if not period.startswith("M"):
        return pd.NaT

    month_str = period.replace("M", "")
    if not month_str.isdigit():
        return pd.NaT

    month = int(month_str)

    # Only keep regular months 1-12
    if month < 1 or month > 12:
        return pd.NaT

    return pd.Timestamp(int(year), month, 1)


def main() -> None:
    print("build_dataset.py started...")

    # 1) Load series IDs from the catalog
    series_ids = load_series_ids("data/series_catalog.csv")

    # 2) Pull last 3 years (you can change this later)
    current_year = pd.Timestamp.today().year
    start_year = current_year - 3

    # 3) Fetch raw data
    raw = fetch_bls(series_ids=series_ids, start_year=start_year, end_year=current_year)
    print(f"Pulled {len(raw)} raw rows.")

    # 4) Clean: make dates + numeric values
    raw["date"] = raw.apply(lambda r: period_to_date(r["year"], r["period"]), axis=1)
    raw["value"] = pd.to_numeric(raw["value"], errors="coerce")

    # Keep only real monthly rows
    clean = raw.dropna(subset=["date", "value"]).copy()

    # 5) Merge metadata from series_catalog.csv
    meta = pd.read_csv("data/series_catalog.csv")
    meta["series_id"] = meta["series_id"].astype(str).str.strip()

    clean = clean.merge(meta, on="series_id", how="left")

    # 6) Keep the columns we want in the final dataset
    final = clean[
        ["date", "series_id", "series_name", "category", "area_type", "value", "units", "source"]
    ].sort_values(["series_id", "date"])

    # 7) Remove duplicates (important for re-running)
    final = final.drop_duplicates(subset=["series_id", "date"], keep="last")

    # 8) Save to CSV
    out_path = "data/bls_monthly.csv"
    final.to_csv(out_path, index=False)

    print(f"Saved cleaned dataset to {out_path}")
    print(final.head(10))
    print(f"Final rows: {len(final)} | Series: {final['series_id'].nunique()}")


if __name__ == "__main__":
    main()
