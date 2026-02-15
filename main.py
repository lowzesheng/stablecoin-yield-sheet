#!/usr/bin/env python3
"""
Stablecoin Yield Sheet — Data Fetcher

Fetches stablecoin lending/borrowing rates, native yields, and macro data
from DeFi Llama, Ethena, and FRED APIs. Exports to CSV + Google Sheets.

Usage:
    python main.py              # Full fetch + export
    python main.py --dry-run    # Fetch and print summary, don't save history
    python main.py --csv-only   # Skip Google Sheets export
"""

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Load .env file if present (no dependency needed)
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _key, _, _val = _line.partition("=")
                os.environ.setdefault(_key.strip(), _val.strip())

from fetchers.defillama import fetch_pools, filter_lending_pools, fetch_native_yields
from fetchers.ethena import fetch_ethena_yield
from fetchers.macro import fetch_macro_data
from history import (
    save_snapshot,
    get_previous_snapshot,
    compute_wow_lending,
    compute_wow_native,
)
from export import export_all, export_summary


def main():
    parser = argparse.ArgumentParser(description="Stablecoin Yield Sheet Data Fetcher")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Fetch and display data without saving to history",
    )
    parser.add_argument(
        "--csv-only", action="store_true",
        help="Export to CSV only, skip Google Sheets",
    )
    args = parser.parse_args()

    print(f"{'=' * 60}")
    print(f"  Stablecoin Yield Sheet — Fetching data...")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 60}")
    print()

    # ── Step 1: Fetch all pools from DeFi Llama (single request) ──
    print("[1/5] Fetching DeFi Llama pools...")
    t0 = time.time()
    try:
        all_pools = fetch_pools()
        print(f"       {len(all_pools)} pools fetched in {time.time() - t0:.1f}s")
    except Exception as e:
        print(f"[FATAL] Failed to fetch DeFi Llama pools: {e}")
        sys.exit(1)

    # ── Step 2: Filter lending/borrowing rates ──
    print("[2/5] Filtering lending & borrowing rates...")
    lending = filter_lending_pools(all_pools)
    print(f"       {len(lending)} stablecoin lending pools matched")

    # ── Step 3: Fetch native yields ──
    print("[3/5] Fetching native yields (sUSDe, sDAI, sUSDS, ...)...")
    native_yields = fetch_native_yields(all_pools)

    # Enrich with Ethena direct API if available
    ethena = fetch_ethena_yield()
    if ethena.get("staking_apy") is not None:
        for ny in native_yields:
            if ny["token"] == "sUSDe":
                ny["apy"] = ethena["staking_apy"]
                break
        else:
            native_yields.insert(0, {
                "token": "sUSDe",
                "protocol": "Ethena",
                "apy": ethena["staking_apy"],
                "tvl_usd": 0,
                "pool_id": "",
            })
        native_yields.sort(key=lambda x: x["apy"], reverse=True)

    print(f"       {len(native_yields)} native yield tokens found")

    # ── Step 4: Fetch macro data ──
    print("[4/5] Fetching macro context...")
    macro = fetch_macro_data()
    fed = macro.get("fed_funds_rate")
    mcap = macro.get("total_stablecoin_mcap")
    if fed:
        print(f"       Fed Funds Rate: {fed}%")
    if mcap:
        print(f"       Total Stablecoin Mcap: ${mcap / 1e9:.1f}B")

    # ── Step 5: Compute WoW changes ──
    print("[5/5] Computing week-over-week changes...")
    prev = get_previous_snapshot()
    if prev:
        print(f"       Previous snapshot: {prev['date']}")
        lending = compute_wow_lending(lending, prev)
        native_yields = compute_wow_native(native_yields, prev)
    else:
        print("       No previous snapshot — WoW will show as '—'")
        lending = compute_wow_lending(lending, None)
        native_yields = compute_wow_native(native_yields, None)

    print()

    # ── Save & export ──
    if not args.dry_run:
        save_snapshot(lending, native_yields, macro)

    export_all(native_yields, lending, macro)


if __name__ == "__main__":
    main()
