"""
Fetch sUSDe yield directly from Ethena's API.

Ethena API response shape:
{
  "stakingYield": {
    "value": "10.2",        # current sUSDe APY %
    "change7d": "0.3",
    "change30d": "-1.2"
  },
  "protocolYield": {
    "value": "12.5",        # protocol-level yield before staking
    ...
  },
  ...
}

Falls back to DeFi Llama data if Ethena API is unavailable.
"""

import requests
from config import ETHENA_YIELD_URL


def fetch_ethena_yield() -> dict:
    """
    Fetch sUSDe staking yield from Ethena.
    Returns dict with apy, change_7d, change_30d.
    """
    try:
        resp = requests.get(ETHENA_YIELD_URL, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        staking = data.get("stakingYield", {})
        protocol = data.get("protocolYield", {})

        return {
            "token": "sUSDe",
            "protocol": "Ethena",
            "staking_apy": _to_float(staking.get("value")),
            "protocol_apy": _to_float(protocol.get("value")),
            "change_7d": _to_float(staking.get("change7d")),
            "change_30d": _to_float(staking.get("change30d")),
            "source": "Ethena API",
        }
    except Exception as e:
        print(f"[WARN] Ethena API failed ({e}), will use DeFi Llama fallback")
        return {
            "token": "sUSDe",
            "protocol": "Ethena",
            "staking_apy": None,
            "protocol_apy": None,
            "change_7d": None,
            "change_30d": None,
            "source": "unavailable",
        }


def _to_float(val) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None
