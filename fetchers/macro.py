"""
Fetch macro context data:
- Fed Funds Rate from FRED
- Total stablecoin market cap from DeFi Llama
"""

import os
import requests
from config import FRED_API_URL, FRED_API_KEY, DEFILLAMA_STABLECOINS_URL


def fetch_fed_funds_rate() -> dict:
    """
    Fetch the latest Federal Funds Effective Rate from FRED.
    Requires FRED_API_KEY (free at https://fred.stlouisfed.org/docs/api/api_key.html).
    """
    api_key = os.environ.get("FRED_API_KEY", FRED_API_KEY)
    if not api_key:
        print("[WARN] No FRED_API_KEY set — skipping Fed Funds rate")
        return {"fed_funds_rate": None, "date": None, "source": "FRED (no key)"}

    try:
        params = {
            "series_id": "FEDFUNDS",
            "api_key": api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 1,
        }
        resp = requests.get(FRED_API_URL, params=params, timeout=15)
        resp.raise_for_status()
        observations = resp.json().get("observations", [])
        if observations:
            obs = observations[0]
            return {
                "fed_funds_rate": float(obs["value"]),
                "date": obs["date"],
                "source": "FRED",
            }
    except Exception as e:
        print(f"[WARN] FRED API failed: {e}")

    return {"fed_funds_rate": None, "date": None, "source": "FRED (error)"}


def fetch_stablecoin_market_cap() -> dict:
    """
    Fetch total stablecoin market cap and top stablecoin breakdown
    from DeFi Llama stablecoins API.
    """
    try:
        resp = requests.get(DEFILLAMA_STABLECOINS_URL, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        assets = data.get("peggedAssets", [])

        # Calculate total market cap and per-coin breakdown
        total_mcap = 0
        coins = []
        for asset in assets:
            # Sum circulating across all chains
            circulating = asset.get("circulating", {})
            mcap = sum(
                v.get("peggedUSD", 0) if isinstance(v, dict) else 0
                for v in circulating.values()
            ) if isinstance(circulating, dict) else 0

            if mcap > 0:
                total_mcap += mcap
                coins.append({
                    "name": asset.get("name", ""),
                    "symbol": asset.get("symbol", ""),
                    "mcap": mcap,
                    "price": asset.get("price"),
                })

        # Sort by market cap, top 15
        coins.sort(key=lambda x: x["mcap"], reverse=True)

        return {
            "total_mcap": total_mcap,
            "top_coins": coins[:15],
            "source": "DeFi Llama",
        }
    except Exception as e:
        print(f"[WARN] DeFi Llama stablecoins API failed: {e}")
        return {"total_mcap": None, "top_coins": [], "source": "DeFi Llama (error)"}


def fetch_macro_data() -> dict:
    """Fetch all macro context data."""
    fed = fetch_fed_funds_rate()
    stables = fetch_stablecoin_market_cap()

    return {
        "fed_funds_rate": fed["fed_funds_rate"],
        "fed_funds_date": fed.get("date"),
        "total_stablecoin_mcap": stables["total_mcap"],
        "top_stablecoins": stables["top_coins"],
    }
