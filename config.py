"""
Configuration for the stablecoin yield sheet data fetcher.
Edit these lists to control what gets fetched and displayed.
"""

# ---------------------------------------------------------------------------
# Stablecoins to track
# ---------------------------------------------------------------------------
STABLECOINS = [
    "USDC", "USDT", "DAI", "USDS", "FRAX", "PYUSD",
    "GHO", "crvUSD", "LUSD", "USDY", "USD0", "FDUSD",
]

# Symbols that DeFi Llama uses in pool names (sometimes wrapped versions)
STABLECOIN_ALIASES = {
    "USDC.E": "USDC",
    "USDC.e": "USDC",
    "USDbC": "USDC",
    "DAI": "DAI",
    "sDAI": "DAI",
    "SDAI": "DAI",
    "WXDAI": "DAI",
}

# ---------------------------------------------------------------------------
# Protocols to track (DeFi Llama project slugs)
# ---------------------------------------------------------------------------
LENDING_PROTOCOLS = [
    "aave-v3",
    "compound-v3",
    "morpho-blue",
    "spark",
    "fluid",
    "venus-core-pool",
    "benqi-lending",
    "sky-savings-rate",
]

# ---------------------------------------------------------------------------
# Chains to track
# ---------------------------------------------------------------------------
CHAINS = [
    "Ethereum",
    "Arbitrum",
    "Base",
    "Optimism",
    "Polygon",
    "BSC",
    "Avalanche",
]

# ---------------------------------------------------------------------------
# Native yield stablecoins (staked / wrapped versions with built-in yield)
# ---------------------------------------------------------------------------
NATIVE_YIELD_TOKENS = {
    "sUSDe": {
        "protocol": "Ethena",
        "underlying": "USDe",
        "source": "Funding rates + ETH staking",
        "risk": "Medium",
    },
    "sDAI": {
        "protocol": "MakerDAO",
        "underlying": "DAI",
        "source": "DAI Savings Rate (RWA + protocol revenue)",
        "risk": "Low",
    },
    "sUSDS": {
        "protocol": "Sky",
        "underlying": "USDS",
        "source": "Sky Savings Rate",
        "risk": "Low",
    },
    "sFRAX": {
        "protocol": "Frax",
        "underlying": "FRAX",
        "source": "IORB-pegged yield (RWA)",
        "risk": "Low-Medium",
    },
    "USD0++": {
        "protocol": "Usual",
        "underlying": "USD0",
        "source": "RWA yield + USUAL emissions",
        "risk": "Medium",
    },
    "USDY": {
        "protocol": "Ondo",
        "underlying": "USD",
        "source": "Short-term US Treasuries",
        "risk": "Low",
    },
}

# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------
DEFILLAMA_POOLS_URL = "https://yields.llama.fi/pools"
DEFILLAMA_STABLECOINS_URL = "https://stablecoins.llama.fi/stablecoins?includePrices=true"
DEFILLAMA_POOL_CHART_URL = "https://yields.llama.fi/chart/{pool_id}"

ETHENA_YIELD_URL = "https://ethena.fi/api/yields/protocol-and-staking-yield"
MAKERDAO_DSR_URL = "https://yields.llama.fi/pools"  # Filtered via DeFi Llama

FRED_API_URL = "https://api.stlouisfed.org/fred/series/observations"
FRED_API_KEY = ""  # Set via env var FRED_API_KEY

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
HISTORY_FILE = "data/history.json"
OUTPUT_CSV_DIR = "output"

# Google Sheets (optional — leave empty to skip)
GOOGLE_SHEETS_CREDENTIALS_FILE = ""  # Path to service account JSON
GOOGLE_SHEET_ID = ""  # The spreadsheet ID from the URL
