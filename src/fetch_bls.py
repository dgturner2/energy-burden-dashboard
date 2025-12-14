"""
fetch_bls.py (Step 7)

Beginner explanation:
- Reads series IDs from data/series_catalog.csv
- Calls the BLS API
- Prints a small preview so we know it worked

This file does NOT save the final dataset yet (that is Step 8).
"""

import os
import json
from typing import List, Optional

import requests
import pandas as pd

BLS_ENDPOINT = "https://api.bls.gov/publicAPI/v2/timeseries/data/"


def load_series_ids(catalog_path: str = "data/series_catalog.csv") -> List[str]:
    """Read series IDs from the CSV file."""
    df = pd.read_csv(catalog_path)

    if "series_id" not in df.columns:
        raise ValueError("series_catalog.csv must have a column named 'series_id'.")

    # Clean up IDs: trim spaces, drop blanks
    series_ids = (
        df["series_id"]
        .astype(str)
        .str.strip()
        .replace({"": None, "nan": None, "None": None})
        .dropna()
        .tolist()
    )

    # Remove duplicates while keeping order
    seen = set()
    series_ids = [x for x in series_ids if not (x in seen or seen.add(x))]

    if not series_ids:
        raise ValueError("No series IDs found. Check data/series_catalog.csv.")

    return series_ids


def fetch_bls(
    series_ids: List[str],
    start_year: int,
    end_year: int,
    api_key: Optional[str] = None,
) -> pd.DataFrame:
    """Call BLS API and return results as a DataFrame."""
    payload = {
        "seriesid": series_ids,
        "startyear": str(start_year),
        "endyear": str(end_year),
    }

    # Use API key if available (optional)
    key = os.getenv("BLS_API_KEY") or api_key
    if key:
        payload["registrationkey"] = key

    resp = requests.post(
        BLS_ENDPOINT,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    # BLS success status is REQUEST_SUCCEEDED
    status = str(data.get("status", "")).upper()
    if status != "REQUEST_SUCCEEDED":
        raise RuntimeError(f"BLS API error: status={status}, message={data.get('message')}")

    rows = []
    for series in data.get("Results", {}).get("series", []):
        sid = series.get("seriesID")
        for item in series.get("data", []):
            rows.append(
                {
                    "series_id": sid,
                    "year": item.get("year"),
                    "period": item.get("period"),
                    "period_name": item.get("periodName"),
                    "value": item.get("value"),
                }
            )

    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("BLS returned no rows. Check your series IDs and year range.")

    return df


def main() -> None:
    print("fetch_bls.py started...")

    series_ids = load_series_ids()
    print("Series IDs:", series_ids)

    current_year = pd.Timestamp.today().year
    start_year = current_year - 3

    df = fetch_bls(series_ids=series_ids, start_year=start_year, end_year=current_year)

    print("\nPreview (first 10 rows):")
    print(df.head(10))

    print(f"\nTotal rows: {len(df)}")
    print(f"Unique series returned: {df['series_id'].nunique()}")


if __name__ == "__main__":
    main()
