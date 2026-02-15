"""
Fetch lending/borrowing rates and TVL from DeFi Llama yields API.

DeFi Llama /pools response shape (per pool):
{
  "chain": "Ethereum",
  "project": "aave-v3",
  "symbol": "USDC",
  "tvlUsd": 1234567890,
  "apyBase": 3.5,          # base supply APY
  "apyReward": 0.2,        # reward token supply APY
  "apy": 3.7,              # total supply APY
  "apyBaseBorrow": 5.1,    # base borrow APY
  "apyRewardBorrow": -0.3, # reward offset on borrow (negative = you earn)
  "totalSupplyUsd": ...,
  "totalBorrowUsd": ...,
  "pool": "pool-id-uuid",
  "poolMeta": "...",
  "ilRisk": "no",
  "stablecoin": true,
  "exposure": "single",
  ...
}
"""

import requests
from typing import Optional
from config import (
    DEFILLAMA_POOLS_URL,
    STABLECOINS,
    STABLECOIN_ALIASES,
    LENDING_PROTOCOLS,
    CHAINS,
)


def _normalise_symbol(symbol: str) -> Optional[str]:
    """Map a pool symbol to our canonical stablecoin name."""
    # Pool symbols can be compound like "USDC-WETH" — take first token
    parts = symbol.split("-")
    for part in parts:
        part = part.strip()
        if part in STABLECOINS:
            return part
        if part in STABLECOIN_ALIASES:
            return STABLECOIN_ALIASES[part]
    return None


def fetch_pools() -> list[dict]:
    """Fetch all pools from DeFi Llama and return raw list."""
    resp = requests.get(DEFILLAMA_POOLS_URL, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", [])


def filter_lending_pools(pools: list[dict]) -> list[dict]:
    """
    Filter pools to only stablecoin lending pools on tracked protocols/chains.
    Returns enriched list with normalised fields.
    """
    results = []
    for p in pools:
        project = p.get("project", "")
        chain = p.get("chain", "")
        symbol_raw = p.get("symbol", "")

        if project not in LENDING_PROTOCOLS:
            continue
        if chain not in CHAINS:
            continue
        if not p.get("stablecoin"):
            continue

        # Only single-asset pools (not LP pairs)
        if p.get("exposure") != "single":
            continue

        stablecoin = _normalise_symbol(symbol_raw)
        if stablecoin is None:
            continue

        results.append({
            "pool_id": p.get("pool", ""),
            "protocol": project,
            "chain": chain,
            "stablecoin": stablecoin,
            "symbol_raw": symbol_raw,
            "pool_meta": p.get("poolMeta", ""),
            # Supply side
            "supply_apy_base": p.get("apyBase") or 0.0,
            "supply_apy_reward": p.get("apyReward") or 0.0,
            "supply_apy_net": p.get("apy") or 0.0,
            # Borrow side
            "borrow_apy_base": p.get("apyBaseBorrow"),
            "borrow_apy_reward": p.get("apyRewardBorrow"),
            "borrow_apy_net": _calc_net_borrow(p),
            # Size
            "tvl_usd": p.get("tvlUsd") or 0.0,
            "total_supply_usd": p.get("totalSupplyUsd") or 0.0,
            "total_borrow_usd": p.get("totalBorrowUsd") or 0.0,
            "utilisation": _calc_utilisation(p),
        })

    # Sort: highest supply APY first
    results.sort(key=lambda x: x["supply_apy_net"], reverse=True)
    return results


def _calc_net_borrow(pool: dict) -> Optional[float]:
    """Calculate net borrow cost (base - reward offset)."""
    base = pool.get("apyBaseBorrow")
    if base is None:
        return None
    reward = pool.get("apyRewardBorrow") or 0.0
    # reward on borrow is typically negative (a benefit), so net = base + reward
    return base + reward


def _calc_utilisation(pool: dict) -> Optional[float]:
    """Calculate utilisation rate as borrowed / supplied."""
    supply = pool.get("totalSupplyUsd") or 0
    borrow = pool.get("totalBorrowUsd") or 0
    if supply == 0:
        return None
    return round((borrow / supply) * 100, 2)


def fetch_lending_rates() -> list[dict]:
    """Main entry point: fetch and return filtered lending pool data."""
    pools = fetch_pools()
    return filter_lending_pools(pools)


def fetch_native_yields(pools: list[dict] = None) -> list[dict]:
    """
    Extract native yield tokens (sDAI, sUSDe, etc.) from DeFi Llama pools.
    These are pools where the 'project' corresponds to a savings/staking product.
    """
    if pools is None:
        pools = fetch_pools()

    NATIVE_PROJECTS = {
        "ethena-susde": {"token": "sUSDe", "protocol": "Ethena"},
        "makerdao-dsr": {"token": "sDAI", "protocol": "MakerDAO"},
        "sky-savings-rate": {"token": "sUSDS", "protocol": "Sky"},
        "frax-ether-staking": {"token": "sFRAX", "protocol": "Frax"},
        "ondo-usdy": {"token": "USDY", "protocol": "Ondo"},
        "usual-usd0++": {"token": "USD0++", "protocol": "Usual"},
    }

    # Also match by symbol for broader coverage
    NATIVE_SYMBOLS = {"sUSDe", "sDAI", "sUSDS", "sFRAX", "USD0++", "USDY"}

    results = []
    seen = set()

    for p in pools:
        project = p.get("project", "")
        symbol = p.get("symbol", "")

        match = None
        if project in NATIVE_PROJECTS:
            match = NATIVE_PROJECTS[project]
        elif symbol in NATIVE_SYMBOLS:
            match = {"token": symbol, "protocol": project}

        if match is None:
            continue
        if p.get("chain") != "Ethereum":
            continue

        key = match["token"]
        if key in seen:
            continue
        seen.add(key)

        results.append({
            "token": match["token"],
            "protocol": match["protocol"],
            "apy": p.get("apy") or p.get("apyBase") or 0.0,
            "tvl_usd": p.get("tvlUsd") or 0.0,
            "pool_id": p.get("pool", ""),
        })

    results.sort(key=lambda x: x["apy"], reverse=True)
    return results
