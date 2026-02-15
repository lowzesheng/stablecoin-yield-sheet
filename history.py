"""
Week-over-week tracking and historical data storage.

Stores weekly snapshots as JSON so we can compute WoW deltas
and build trend data over time.

Data file structure (data/history.json):
{
  "snapshots": [
    {
      "date": "2025-01-12",
      "lending": [...],
      "native_yields": [...],
      "macro": {...}
    },
    ...
  ]
}
"""

import json
import os
from datetime import datetime, timedelta
from config import HISTORY_FILE


def load_history() -> dict:
    """Load historical snapshots from disk."""
    path = HISTORY_FILE
    if not os.path.exists(path):
        return {"snapshots": []}
    with open(path, "r") as f:
        return json.load(f)


def save_snapshot(lending: list, native_yields: list, macro: dict) -> None:
    """Save this week's data as a new snapshot."""
    history = load_history()
    today = datetime.now().strftime("%Y-%m-%d")

    # Remove any existing snapshot for today (allow re-runs)
    history["snapshots"] = [
        s for s in history["snapshots"] if s["date"] != today
    ]

    history["snapshots"].append({
        "date": today,
        "lending": lending,
        "native_yields": native_yields,
        "macro": macro,
    })

    # Keep last 52 weeks
    history["snapshots"] = history["snapshots"][-52:]
    history["snapshots"].sort(key=lambda s: s["date"])

    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

    print(f"[OK] Snapshot saved for {today} ({len(history['snapshots'])} total)")


def get_previous_snapshot() -> dict | None:
    """Get the most recent snapshot before today."""
    history = load_history()
    today = datetime.now().strftime("%Y-%m-%d")
    previous = [s for s in history["snapshots"] if s["date"] < today]
    if previous:
        return previous[-1]
    return None


def compute_wow_lending(current: list, previous_snapshot: dict | None) -> list:
    """
    Add WoW delta fields to current lending data by comparing to previous week.
    Matches on (protocol, chain, stablecoin) tuple.
    """
    if previous_snapshot is None:
        for row in current:
            row["supply_apy_wow"] = None
            row["borrow_apy_wow"] = None
        return current

    # Build lookup from previous data
    prev_lookup = {}
    for p in previous_snapshot.get("lending", []):
        key = (p["protocol"], p["chain"], p["stablecoin"])
        prev_lookup[key] = p

    for row in current:
        key = (row["protocol"], row["chain"], row["stablecoin"])
        prev = prev_lookup.get(key)
        if prev:
            row["supply_apy_wow"] = round(
                row["supply_apy_net"] - prev["supply_apy_net"], 4
            )
            prev_borrow = prev.get("borrow_apy_net")
            curr_borrow = row.get("borrow_apy_net")
            if prev_borrow is not None and curr_borrow is not None:
                row["borrow_apy_wow"] = round(curr_borrow - prev_borrow, 4)
            else:
                row["borrow_apy_wow"] = None
        else:
            row["supply_apy_wow"] = None
            row["borrow_apy_wow"] = None

    return current


def compute_wow_native(current: list, previous_snapshot: dict | None) -> list:
    """Add WoW delta to native yield data."""
    if previous_snapshot is None:
        for row in current:
            row["apy_wow"] = None
        return current

    prev_lookup = {p["token"]: p for p in previous_snapshot.get("native_yields", [])}

    for row in current:
        prev = prev_lookup.get(row["token"])
        if prev:
            row["apy_wow"] = round(row["apy"] - prev["apy"], 4)
        else:
            row["apy_wow"] = None

    return current


def get_trend(pool_key: tuple, weeks: int = 4) -> list[float]:
    """Get historical APY values for a specific pool over N weeks."""
    history = load_history()
    snapshots = history["snapshots"][-(weeks + 1):]  # +1 for current

    trend = []
    for snap in snapshots:
        for p in snap.get("lending", []):
            if (p["protocol"], p["chain"], p["stablecoin"]) == pool_key:
                trend.append(p["supply_apy_net"])
                break

    return trend
