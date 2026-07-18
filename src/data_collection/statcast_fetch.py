"""
statcast_fetch.py

Pulls pitch-level Statcast data from Baseball Savant using the pybaseball
package. Statcast includes exit velocity, launch angle, spin rate, pitch
type, and other tracking metrics.

Install dependency first:
    pip install pybaseball --break-system-packages

Usage:
    python statcast_fetch.py --start 2025-04-01 --end 2025-04-07 --out ../../data/raw

Notes:
    - Large date ranges can take a while and return millions of rows;
      pybaseball chunks requests internally but consider pulling in
      smaller windows (week or month) for your first tests.
    - pybaseball caches some requests locally by default; call
      pybaseball.cache.enable() if you want that behavior explicitly.
"""

import argparse
from pathlib import Path

from pybaseball import statcast


def fetch_statcast(start_date: str, end_date: str):
    """Fetch all Statcast pitch-level data between start_date and end_date (YYYY-MM-DD)."""
    df = statcast(start_dt=start_date, end_dt=end_date)
    return df


def main():
    parser = argparse.ArgumentParser(description="Pull Statcast data for a date range.")
    parser.add_argument("--start", required=True, help="Start date, YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="End date, YYYY-MM-DD")
    parser.add_argument("--out", default="../../data/raw", help="Output directory")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Fetching Statcast data from {args.start} to {args.end}...")
    df = fetch_statcast(args.start, args.end)
    print(f"Retrieved {len(df)} rows, {len(df.columns)} columns")

    out_path = out_dir / f"statcast_{args.start}_to_{args.end}.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
