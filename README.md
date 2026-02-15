# Stablecoin Yield Sheet — Data Fetcher

Automated data pipeline for a weekly stablecoin yield & lending rate publication.

Pulls rates from DeFi Llama, Ethena, and FRED, then exports to CSV (and optionally Google Sheets) for editorial review and distribution.

## What it fetches

| Section | Data | Source |
|---------|------|--------|
| Native Yields | sUSDe, sDAI, sUSDS, sFRAX, USD0++, USDY | DeFi Llama + Ethena API |
| Supply Rates | Earn APY across Aave, Compound, Morpho, Spark, Fluid, Venus, Benqi | DeFi Llama |
| Borrow Rates | Borrow cost across same protocols | DeFi Llama |
| Macro | Fed Funds Rate, total stablecoin market cap | FRED + DeFi Llama |
| WoW Changes | Week-over-week deltas for all rates | Computed from local history |

## Quick start

```bash
pip install -r requirements.txt
python main.py
```

Output files land in `output/`:
- `native_yields.csv` — native stablecoin yields
- `supply_rates.csv` — lending supply rates
- `borrow_rates.csv` — borrowing costs
- `macro.csv` — macro context
- `summary.txt` — combined text summary for copy-paste

## Options

```bash
python main.py --dry-run    # Fetch + print, don't save history
python main.py --csv-only   # Skip Google Sheets export
```

## Configuration

Edit `config.py` to:
- Add/remove stablecoins, protocols, or chains
- Set your FRED API key (or `export FRED_API_KEY=...`)
- Configure Google Sheets credentials

## Google Sheets setup (optional)

1. Create a Google Cloud service account and download the JSON key
2. Share your Google Sheet with the service account email
3. Set in `config.py`:
   ```python
   GOOGLE_SHEETS_CREDENTIALS_FILE = "path/to/credentials.json"
   GOOGLE_SHEET_ID = "your-sheet-id-from-url"
   ```
4. Create three tabs in your sheet: `Native Yields`, `Supply Rates`, `Borrow Rates`
5. `pip install google-api-python-client google-auth`

## Weekly workflow

1. Run `python main.py` (takes ~5 seconds)
2. Open the CSVs or Google Sheet
3. Add your editorial: risk ratings, strategy highlights, commentary
4. Distribute (newsletter, Twitter, Telegram)

History is stored in `data/history.json` — WoW deltas auto-compute from the previous run.

## Project structure

```
├── main.py              # CLI entry point & orchestrator
├── config.py            # All configuration (coins, protocols, APIs)
├── fetchers/
│   ├── defillama.py     # DeFi Llama pools API
│   ├── ethena.py        # Ethena sUSDe yield API
│   └── macro.py         # FRED + stablecoin market cap
├── history.py           # WoW tracking & snapshot storage
├── export.py            # CSV + Google Sheets + summary export
├── data/                # Local history (gitignored)
├── output/              # Generated CSVs (gitignored)
└── PRD.md               # Product requirements document
```
