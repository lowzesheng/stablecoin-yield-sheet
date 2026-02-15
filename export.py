"""
Export fetched data to CSV files and optionally to Google Sheets.

Generates three CSVs:
  - output/native_yields.csv
  - output/supply_rates.csv
  - output/borrow_rates.csv
  - output/macro.csv

And a combined summary for quick viewing.
"""

import csv
import os
from datetime import datetime
from config import (
    OUTPUT_CSV_DIR,
    GOOGLE_SHEETS_CREDENTIALS_FILE,
    GOOGLE_SHEET_ID,
    NATIVE_YIELD_TOKENS,
)


def _fmt_pct(val, decimals=2) -> str:
    """Format a percentage value."""
    if val is None:
        return ""
    return f"{val:.{decimals}f}%"


def _fmt_usd(val) -> str:
    """Format USD value in millions/billions."""
    if val is None:
        return ""
    if val >= 1_000_000_000:
        return f"${val / 1_000_000_000:.2f}B"
    if val >= 1_000_000:
        return f"${val / 1_000_000:.1f}M"
    return f"${val:,.0f}"


def _fmt_wow(val) -> str:
    """Format WoW change with +/- sign."""
    if val is None:
        return "—"
    sign = "+" if val > 0 else ""
    return f"{sign}{val:.2f}%"


def _ensure_output_dir():
    os.makedirs(OUTPUT_CSV_DIR, exist_ok=True)


def export_native_yields_csv(native_yields: list) -> str:
    """Export native yield stablecoins to CSV."""
    _ensure_output_dir()
    path = os.path.join(OUTPUT_CSV_DIR, "native_yields.csv")

    headers = [
        "Token", "Protocol", "APY", "WoW Change", "TVL",
        "Source of Yield", "Risk Rating",
    ]

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in native_yields:
            token = row["token"]
            meta = NATIVE_YIELD_TOKENS.get(token, {})
            writer.writerow([
                token,
                row["protocol"],
                _fmt_pct(row["apy"]),
                _fmt_wow(row.get("apy_wow")),
                _fmt_usd(row["tvl_usd"]),
                meta.get("source", ""),
                meta.get("risk", ""),
            ])

    print(f"[OK] {path} ({len(native_yields)} rows)")
    return path


def export_supply_rates_csv(lending: list) -> str:
    """Export supply (earn) rates to CSV."""
    _ensure_output_dir()
    path = os.path.join(OUTPUT_CSV_DIR, "supply_rates.csv")

    headers = [
        "Protocol", "Chain", "Stablecoin",
        "Supply APY (Base)", "Supply APY (Reward)", "Supply APY (Net)",
        "WoW Change", "TVL", "Utilisation",
    ]

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in lending:
            writer.writerow([
                row["protocol"],
                row["chain"],
                row["stablecoin"],
                _fmt_pct(row["supply_apy_base"]),
                _fmt_pct(row["supply_apy_reward"]),
                _fmt_pct(row["supply_apy_net"]),
                _fmt_wow(row.get("supply_apy_wow")),
                _fmt_usd(row["tvl_usd"]),
                _fmt_pct(row.get("utilisation")),
            ])

    print(f"[OK] {path} ({len(lending)} rows)")
    return path


def export_borrow_rates_csv(lending: list) -> str:
    """Export borrow (cost) rates to CSV."""
    _ensure_output_dir()
    path = os.path.join(OUTPUT_CSV_DIR, "borrow_rates.csv")

    # Only include pools that have borrow data
    borrow_pools = [r for r in lending if r.get("borrow_apy_base") is not None]
    # Sort by cheapest borrow first
    borrow_pools.sort(key=lambda x: x.get("borrow_apy_net") or 999)

    headers = [
        "Protocol", "Chain", "Stablecoin",
        "Borrow APY (Base)", "Borrow APY (Reward)", "Net Borrow Cost",
        "WoW Change", "Available Liquidity",
    ]

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in borrow_pools:
            available = (row.get("total_supply_usd") or 0) - (row.get("total_borrow_usd") or 0)
            writer.writerow([
                row["protocol"],
                row["chain"],
                row["stablecoin"],
                _fmt_pct(row["borrow_apy_base"]),
                _fmt_pct(row.get("borrow_apy_reward")),
                _fmt_pct(row.get("borrow_apy_net")),
                _fmt_wow(row.get("borrow_apy_wow")),
                _fmt_usd(available if available > 0 else 0),
            ])

    print(f"[OK] {path} ({len(borrow_pools)} rows)")
    return path


def export_macro_csv(macro: dict) -> str:
    """Export macro context to CSV."""
    _ensure_output_dir()
    path = os.path.join(OUTPUT_CSV_DIR, "macro.csv")

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Fed Funds Rate", _fmt_pct(macro.get("fed_funds_rate"))])
        writer.writerow(["Total Stablecoin Mcap", _fmt_usd(macro.get("total_stablecoin_mcap"))])
        writer.writerow(["Date", datetime.now().strftime("%Y-%m-%d")])
        writer.writerow([])
        writer.writerow(["Top Stablecoins by Market Cap", ""])
        writer.writerow(["Symbol", "Market Cap"])
        for coin in macro.get("top_stablecoins", []):
            writer.writerow([coin["symbol"], _fmt_usd(coin["mcap"])])

    print(f"[OK] {path}")
    return path


def export_summary(native_yields: list, lending: list, macro: dict) -> str:
    """
    Generate a single combined summary text file for quick viewing
    and copy-paste into newsletters.
    """
    _ensure_output_dir()
    path = os.path.join(OUTPUT_CSV_DIR, "summary.txt")
    date = datetime.now().strftime("%Y-%m-%d")

    lines = []
    lines.append(f"{'=' * 60}")
    lines.append(f"  STABLECOIN YIELD SHEET — {date}")
    lines.append(f"{'=' * 60}")

    # Macro
    fed = macro.get("fed_funds_rate")
    mcap = macro.get("total_stablecoin_mcap")
    lines.append(f"  Fed Funds Rate: {_fmt_pct(fed) if fed else 'N/A'}")
    lines.append(f"  Total Stablecoin Mcap: {_fmt_usd(mcap) if mcap else 'N/A'}")
    lines.append("")

    # Native yields
    lines.append(f"{'─' * 60}")
    lines.append("  NATIVE YIELDS (hold/stake to earn)")
    lines.append(f"{'─' * 60}")
    lines.append(f"  {'Token':<10} {'Protocol':<12} {'APY':>8} {'WoW':>8} {'TVL':>12}")
    lines.append(f"  {'─'*10} {'─'*12} {'─'*8} {'─'*8} {'─'*12}")
    for r in native_yields:
        lines.append(
            f"  {r['token']:<10} {r['protocol']:<12} "
            f"{_fmt_pct(r['apy']):>8} {_fmt_wow(r.get('apy_wow')):>8} "
            f"{_fmt_usd(r['tvl_usd']):>12}"
        )
    lines.append("")

    # Top supply rates
    lines.append(f"{'─' * 60}")
    lines.append("  TOP SUPPLY RATES (lend to earn)")
    lines.append(f"{'─' * 60}")
    lines.append(
        f"  {'Protocol':<15} {'Chain':<10} {'Asset':<7} "
        f"{'APY':>8} {'WoW':>8} {'TVL':>10}"
    )
    lines.append(f"  {'─'*15} {'─'*10} {'─'*7} {'─'*8} {'─'*8} {'─'*10}")
    for r in lending[:20]:  # Top 20
        lines.append(
            f"  {r['protocol']:<15} {r['chain']:<10} {r['stablecoin']:<7} "
            f"{_fmt_pct(r['supply_apy_net']):>8} "
            f"{_fmt_wow(r.get('supply_apy_wow')):>8} "
            f"{_fmt_usd(r['tvl_usd']):>10}"
        )
    lines.append("")

    # Top borrow rates (cheapest first)
    borrow_pools = sorted(
        [r for r in lending if r.get("borrow_apy_net") is not None],
        key=lambda x: x["borrow_apy_net"],
    )
    lines.append(f"{'─' * 60}")
    lines.append("  CHEAPEST BORROW RATES")
    lines.append(f"{'─' * 60}")
    lines.append(
        f"  {'Protocol':<15} {'Chain':<10} {'Asset':<7} "
        f"{'Cost':>8} {'WoW':>8}"
    )
    lines.append(f"  {'─'*15} {'─'*10} {'─'*7} {'─'*8} {'─'*8}")
    for r in borrow_pools[:15]:
        lines.append(
            f"  {r['protocol']:<15} {r['chain']:<10} {r['stablecoin']:<7} "
            f"{_fmt_pct(r['borrow_apy_net']):>8} "
            f"{_fmt_wow(r.get('borrow_apy_wow')):>8}"
        )
    lines.append("")

    # Carry trade opportunities
    if borrow_pools and lending:
        cheapest_borrow = borrow_pools[0]
        highest_supply = lending[0]
        spread = highest_supply["supply_apy_net"] - cheapest_borrow["borrow_apy_net"]
        if spread > 0:
            lines.append(f"{'─' * 60}")
            lines.append("  TOP CARRY TRADE")
            lines.append(f"{'─' * 60}")
            lines.append(
                f"  Borrow {cheapest_borrow['stablecoin']} on "
                f"{cheapest_borrow['protocol']} ({cheapest_borrow['chain']}) "
                f"at {_fmt_pct(cheapest_borrow['borrow_apy_net'])}"
            )
            lines.append(
                f"  Supply {highest_supply['stablecoin']} on "
                f"{highest_supply['protocol']} ({highest_supply['chain']}) "
                f"at {_fmt_pct(highest_supply['supply_apy_net'])}"
            )
            lines.append(f"  Spread: {_fmt_pct(spread)}")
            lines.append("")

    lines.append(f"{'=' * 60}")
    lines.append("  [Add your commentary / risk notes below]")
    lines.append("")

    text = "\n".join(lines)
    with open(path, "w") as f:
        f.write(text)

    print(f"[OK] {path}")
    return text


def export_to_google_sheets(native_yields: list, lending: list, macro: dict) -> bool:
    """
    Export data to Google Sheets. Requires:
    - google-api-python-client and google-auth packages
    - Service account credentials JSON file
    - Sheet ID

    Returns True if successful, False if skipped/failed.
    """
    if not GOOGLE_SHEETS_CREDENTIALS_FILE or not GOOGLE_SHEET_ID:
        print("[SKIP] Google Sheets export — no credentials/sheet ID configured")
        return False

    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        print("[SKIP] Google Sheets export — install google-api-python-client google-auth")
        return False

    try:
        creds = Credentials.from_service_account_file(
            GOOGLE_SHEETS_CREDENTIALS_FILE,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        service = build("sheets", "v4", credentials=creds)
        sheets = service.spreadsheets()

        date = datetime.now().strftime("%Y-%m-%d")

        # --- Native Yields sheet ---
        native_rows = [["Token", "Protocol", "APY", "WoW", "TVL", "Source", "Risk"]]
        for r in native_yields:
            meta = NATIVE_YIELD_TOKENS.get(r["token"], {})
            native_rows.append([
                r["token"], r["protocol"],
                r["apy"], r.get("apy_wow"),
                r["tvl_usd"],
                meta.get("source", ""), meta.get("risk", ""),
            ])

        sheets.values().update(
            spreadsheetId=GOOGLE_SHEET_ID,
            range="Native Yields!A1",
            valueInputOption="USER_ENTERED",
            body={"values": native_rows},
        ).execute()

        # --- Supply Rates sheet ---
        supply_rows = [[
            "Protocol", "Chain", "Stablecoin",
            "Base APY", "Reward APY", "Net APY", "WoW", "TVL", "Utilisation",
        ]]
        for r in lending:
            supply_rows.append([
                r["protocol"], r["chain"], r["stablecoin"],
                r["supply_apy_base"], r["supply_apy_reward"], r["supply_apy_net"],
                r.get("supply_apy_wow"), r["tvl_usd"], r.get("utilisation"),
            ])

        sheets.values().update(
            spreadsheetId=GOOGLE_SHEET_ID,
            range="Supply Rates!A1",
            valueInputOption="USER_ENTERED",
            body={"values": supply_rows},
        ).execute()

        # --- Borrow Rates sheet ---
        borrow_pools = sorted(
            [r for r in lending if r.get("borrow_apy_base") is not None],
            key=lambda x: x.get("borrow_apy_net") or 999,
        )
        borrow_rows = [[
            "Protocol", "Chain", "Stablecoin",
            "Base Borrow APY", "Reward", "Net Cost", "WoW", "Available Liquidity",
        ]]
        for r in borrow_pools:
            avail = (r.get("total_supply_usd") or 0) - (r.get("total_borrow_usd") or 0)
            borrow_rows.append([
                r["protocol"], r["chain"], r["stablecoin"],
                r["borrow_apy_base"], r.get("borrow_apy_reward"),
                r.get("borrow_apy_net"), r.get("borrow_apy_wow"),
                max(avail, 0),
            ])

        sheets.values().update(
            spreadsheetId=GOOGLE_SHEET_ID,
            range="Borrow Rates!A1",
            valueInputOption="USER_ENTERED",
            body={"values": borrow_rows},
        ).execute()

        print(f"[OK] Google Sheets updated ({GOOGLE_SHEET_ID})")
        return True

    except Exception as e:
        print(f"[ERR] Google Sheets export failed: {e}")
        return False


def export_all(native_yields: list, lending: list, macro: dict) -> None:
    """Run all exports."""
    export_native_yields_csv(native_yields)
    export_supply_rates_csv(lending)
    export_borrow_rates_csv(lending)
    export_macro_csv(macro)
    summary = export_summary(native_yields, lending, macro)
    export_to_google_sheets(native_yields, lending, macro)

    print("\n" + summary)
