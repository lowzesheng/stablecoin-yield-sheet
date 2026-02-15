# PRD: Weekly Stablecoin Yield & Lending Sheet

## 1. Product Overview

A weekly publication (newsletter/sheet) that gives users a single-pane view of the most actionable stablecoin yields, lending rates, and borrowing rates across DeFi and CeFi — enabling readers to instantly compare where to park or borrow stablecoins for the best risk-adjusted return.

---

## 2. Target Users

- DeFi-native users rotating yield across protocols
- Treasury managers at DAOs/crypto funds
- Stablecoin holders looking for passive income
- Borrowers shopping for the cheapest leverage
- Analysts tracking rate trends week-over-week

---

## 3. Key Data Sections & Features

### 3.1 Stablecoins Covered

| Tier | Stablecoins |
|------|------------|
| Core (must-have) | USDC, USDT, DAI/sDAI, USDS/sUSDS |
| Secondary | USDe/sUSDe (Ethena), PYUSD, FRAX/sFRAX, GHO, crvUSD, LUSD |
| Emerging | USDY (Ondo), USD0/USD0++ (Usual), USDX, eUSD |

### 3.2 Section A — Native / Protocol Yields

These are "base yields" you get from simply holding or staking the stablecoin itself (not lending it).

| Data Point | Description | Example |
|-----------|-------------|---------|
| Stablecoin | Token name | sUSDe, sDAI, sUSDS, USD0++ |
| Protocol | Issuer/protocol | Ethena, MakerDAO, Sky, Usual |
| Native APY | Current yield from staking/holding | 10.2%, 6.5%, 6.5%, 4.0% |
| Source of Yield | Where the yield comes from | Funding rates + staking, DSR, DSR, RWA + protocol revenue |
| WoW Change | Week-over-week APY delta | +0.3%, -0.1% |
| TVL | Total value locked / total supply | $5.2B, $2.1B |
| Risk Rating | Subjective risk tier | Low / Medium / High |
| Notes | Manual commentary on anything notable | "Rate dropped due to negative funding" |

### 3.3 Section B — Lending Supply Rates (Earn)

What you earn by supplying stablecoins to lending protocols.

| Data Point | Description |
|-----------|-------------|
| Protocol | Aave V3, Compound V3, Morpho, Spark, Fluid, Venus, Benqi |
| Chain | Ethereum, Arbitrum, Base, Polygon, Optimism, BSC, Avalanche |
| Stablecoin | USDC, USDT, DAI, etc. |
| Supply APY (Base) | Base interest rate from utilisation |
| Supply APY (Reward) | Additional token incentives (MORPHO, COMP, etc.) |
| Supply APY (Net) | Base + Reward combined |
| Utilisation Rate | % of pool currently borrowed |
| Available Liquidity | How much can still be supplied/withdrawn |
| TVL / Market Size | Total pool size |
| WoW Change | Delta on net supply APY |

**Protocols to cover (priority order):**
1. Aave V3 (Ethereum, Arbitrum, Base, Optimism, Polygon)
2. Compound V3 (Ethereum, Arbitrum, Base, Polygon)
3. Morpho (Ethereum — vaults and direct markets)
4. Spark (Ethereum)
5. Fluid (Ethereum)
6. Sky / MakerDAO DSR
7. Venus (BSC)
8. Benqi (Avalanche)
9. Pendle (tokenised yield markets)

### 3.4 Section C — Borrowing Rates (Cost to Leverage)

What it costs to borrow stablecoins.

| Data Point | Description |
|-----------|-------------|
| Protocol | Same set as lending |
| Chain | Same |
| Stablecoin | USDC, USDT, DAI, GHO, etc. |
| Borrow APY (Variable) | Current variable borrow rate |
| Borrow APY (Stable) | Stable rate if available |
| Borrow Reward | Any incentive offsets |
| Net Borrow Cost | Variable - Rewards |
| Collateral Options | What you can post as collateral (ETH, wstETH, etc.) |
| Max LTV | Loan-to-value ratio |
| Liquidation Threshold | When you get liquidated |

### 3.5 Section D — Rate Arbitrage / Strategy Highlights

A curated section of actionable observations:

| Feature | Example |
|---------|---------|
| Cheapest borrow | "Borrow USDC on Aave Base at 3.1%" |
| Highest supply | "Supply USDT on Morpho at 8.2%" |
| Best carry trade | "Borrow GHO at 2.5% → supply USDC on Morpho at 8.2% = 5.7% spread" |
| Yield trend | "Rates compressing across the board — utilisation dropping" |
| Risk callout | "USDe funding rate turning negative, sUSDe yield at risk" |

### 3.6 Section E — Macro & Market Context (Manual / Editorial)

- Fed Funds Rate / SOFR (benchmark comparison)
- On-chain stablecoin supply trends (total stablecoin mcap)
- DEX volume trends (indicates leverage demand)
- Funding rate environment (impacts Ethena, basis trade yields)
- Notable protocol governance changes affecting rates

### 3.7 Section F — Historical Tracking

- 4-week rolling rate history for key pairs (USDC supply on Aave, USDT supply on Compound, etc.)
- Sparkline or mini-charts for top 10 rates
- Trend indicators (arrows / colour coding)

---

## 4. Layout & Presentation

### Weekly Sheet Layout (recommended)

```
┌─────────────────────────────────────────────────────┐
│  🏦 STABLECOIN YIELD SHEET — Week of [DATE]         │
│  Fed Funds: 4.50% | Total Stablecoin Mcap: $XXXbn   │
├─────────────────────────────────────────────────────┤
│  NATIVE YIELDS                                       │
│  sUSDe: 10.2% | sDAI: 6.5% | sUSDS: 6.5% | ...    │
├─────────────────────────────────────────────────────┤
│  TOP SUPPLY RATES (EARN)                             │
│  [Table: Protocol | Chain | Asset | APY | WoW]       │
├─────────────────────────────────────────────────────┤
│  TOP BORROW RATES (COST)                             │
│  [Table: Protocol | Chain | Asset | APY | WoW]       │
├─────────────────────────────────────────────────────┤
│  STRATEGY HIGHLIGHTS                                 │
│  - Best carry: ...                                   │
│  - Cheapest borrow: ...                              │
├─────────────────────────────────────────────────────┤
│  COMMENTARY / NOTES                                  │
│  [Manual editorial section]                          │
└─────────────────────────────────────────────────────┘
```

---

## 5. Required APIs & Data Sources

### 5.1 Fully Automatable via API

| Data | Source | API | Free Tier |
|------|--------|-----|-----------|
| Aave V3 supply/borrow rates, TVL | Aave subgraph / Aave API | GraphQL subgraph on each chain | Yes (The Graph) |
| Compound V3 supply/borrow rates | Compound subgraph / Compound API | GraphQL subgraph | Yes |
| Morpho rates | Morpho API | `https://blue-api.morpho.org/graphql` | Yes |
| Spark rates | Spark subgraph | GraphQL | Yes |
| Venus rates | Venus API | REST API `https://api.venus.io` | Yes |
| Ethena sUSDe yield | Ethena API | `https://ethena.fi/api/yields/protocol-and-staking-yield` | Yes |
| MakerDAO / Sky DSR | On-chain (pot.dsr) or DeFi Llama | Contract read or API | Yes |
| DeFi Llama yields | DeFi Llama | `https://yields.llama.fi/pools` | Yes, no key needed |
| DeFi Llama TVL | DeFi Llama | `https://api.llama.fi/tvl/{protocol}` | Yes, no key needed |
| DeFi Llama stablecoin data | DeFi Llama | `https://stablecoins.llama.fi/stablecoins` | Yes, no key needed |
| Pendle yields | Pendle API | `https://api-v2.pendle.finance/core/...` | Yes |
| Token prices | CoinGecko / DeFi Llama | REST | Yes (rate-limited) |
| Fed Funds Rate | FRED API | `https://api.stlouisfed.org/fred/series/observations?series_id=FEDFUNDS` | Yes (free key) |

### 5.2 Semi-Automatable (API + Manual)

| Data | Source | Notes |
|------|--------|-------|
| Fluid rates | Fluid contracts / Instadapp API | May need direct contract reads |
| GHO borrow rate | Aave governance / on-chain | Fixed by governance, check Aave API |
| Benqi rates | Benqi subgraph | Less mature API |

### 5.3 Manual / Editorial Only

| Data | Notes |
|------|-------|
| Risk ratings | Subjective — you assign based on your framework |
| Strategy highlights | Your analysis of the data |
| Weekly commentary | Your editorial on macro + rate trends |
| Source-of-yield explanations | Semi-static, update when mechanisms change |

### 5.3 Primary Recommendation: DeFi Llama as Backbone

**DeFi Llama's `/pools` endpoint** is the single most valuable API because it:
- Aggregates yield data across 800+ protocols
- Covers Aave, Compound, Morpho, Spark, Venus, Pendle, and more
- Returns: pool APY (base + reward), TVL, chain, project, stablecoin
- Is free with no API key required
- Updates frequently

You can build 80% of the sheet from DeFi Llama alone, then supplement with protocol-specific APIs for granular data (utilisation, borrow rates, collateral details).

---

## 6. Automation Recommendation

### Recommended Approach: Automated Data Pipeline + Manual Editorial

**Why not pure manual?**
- 50+ data points to update weekly across protocols/chains — error-prone and tedious
- Rate data is available from free APIs with no authentication
- Automation ensures consistency and allows WoW tracking

**Why not pure automation?**
- The highest-value parts of the sheet are the editorial: strategy highlights, risk commentary, and market context
- Risk ratings require human judgment
- Some niche protocols lack clean APIs

### Architecture: Python Script + Google Sheets

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Python       │────>│ Google Sheets │────>│ Distribution  │
│  Data Fetcher │     │ (formatted)   │     │ (newsletter/  │
│               │     │               │     │  Twitter/     │
│ - DeFi Llama │     │ - Auto data   │     │  Substack)    │
│ - Aave API   │     │ - Manual cols │     │               │
│ - Ethena API │     │ - Charts      │     │               │
│ - FRED API   │     │ - WoW calc    │     │               │
└──────────────┘     └──────────────┘     └──────────────┘
      ↑                     ↑
   Cron/manual           You add:
   trigger               - Commentary
                         - Risk ratings
                         - Strategy picks
```

**Workflow:**
1. Run Python script (manually or cron) — pulls all rate data
2. Script writes to Google Sheet via API (or outputs CSV for paste)
3. You open sheet, review data, add editorial columns
4. Export / screenshot for distribution

### Alternative: Pure Google Sheets + Apps Script

If you prefer no Python setup:
- Use Google Apps Script (JavaScript in Sheets) to call APIs directly
- `UrlFetchApp.fetch()` can hit DeFi Llama, Aave subgraphs, etc.
- Trigger on a schedule or manually
- Keeps everything in one place

---

## 7. MVP Scope (Week 1)

| Feature | Status |
|---------|--------|
| Native yields: sUSDe, sDAI, sUSDS, USD0++ | Auto |
| Supply rates: Aave V3 + Compound V3 (USDC, USDT, DAI) on Ethereum | Auto |
| Borrow rates: Aave V3 + Compound V3 (same assets) | Auto |
| Morpho top USDC/USDT vaults | Auto |
| WoW change calculation | Auto (store previous week) |
| Fed Funds rate | Auto |
| Total stablecoin market cap | Auto |
| Strategy highlights (top 3) | Manual |
| Risk ratings | Manual |
| Commentary | Manual |

### Post-MVP (Week 2+)
- Add Spark, Fluid, Venus, Pendle
- Multi-chain (Arbitrum, Base, Optimism)
- Historical tracking + sparklines
- Automated distribution (email/Telegram bot)
- Collateral detail tables for borrowing

---

## 8. Success Metrics

- User engagement (opens, shares, saves)
- Time-to-publish (target: < 30 min/week with automation)
- Data accuracy (spot-check against protocol UIs)
- Coverage breadth (# of protocols x chains x assets)

---

## 9. Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| API deprecation / breaking changes | DeFi Llama as fallback; alert on fetch failures |
| Stale data | Timestamp all data; show "as of" time |
| Rate manipulation (flash loan artifacts) | Use time-weighted averages where available |
| Stablecoin depeg | Include price column; flag any deviation > 0.5% |
| Information overload | Curate top N rates, not dump everything |
