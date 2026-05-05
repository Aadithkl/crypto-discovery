# /crypto-discovery setup — Configure Sources

## Purpose

Interactive wizard to configure crypto-discovery sources, API keys, and preferences.

## Step 1: Welcome

```markdown
# Crypto Discovery — Setup

Welcome! This wizard will configure your research sub-agent.

Good news: 13 sources work without any API keys.
Add optional keys to unlock 11 more premium sources.

Estimated time: 2 minutes.
```

## Step 2: Check Dependencies

```markdown
## Required Tools

Checking for available tools...

[✓] WebFetch — Available (direct API calls)
[✓] WebSearch — Available (web searches)
[ ] Playwright MCP — Not detected (browser scraping)

Playwright MCP is recommended for best results with RootData, 
CryptoFundraising, and Crunchbase.

Install: https://github.com/microsoft/playwright-mcp
(You can skip this and use WebFetch fallbacks)
```

## Step 3: Core Sources (Auto-enabled)

```markdown
## Core Free Sources (Auto-enabled)

These 13 sources work without API keys:

✓ DeFiLlama — TVL, protocols, yields, fees
✓ CoinGecko — Prices, market cap, categories
✓ DeBank — Portfolio data, holdings
✓ Flipside Crypto — SQL on-chain analytics
✓ Blockscout — Transactions, contracts, multi-chain
✓ Snapshot — Governance proposals
✓ GitHub — Code activity
✓ CryptoFundraising.info — Deal flow
✓ RootData — Projects, fundraising, investors
✓ Twitter WebSearch — Social data
✓ The Block — News & research
✓ CoinDesk — Crypto news
✓ Cointelegraph — Crypto news
✓ Custom — Your files (Excel, Sheets, etc.)

Press Enter to continue...
```

## Step 4: Optional Free Sources

```markdown
## Optional Free Sources

These are free but you can enable/disable:

[✓] CoinMarketCap — Prices, rankings (optional API key for higher limits)
[✓] RootData — Projects, fundraising (optional API key)
[✓] Crunchbase — Funding, company info (optional API key)

Toggle any off by typing the number, or press Enter to keep all.
```

## Step 5: Premium API Keys

```markdown
## Premium Sources (Optional)

Add API keys to unlock deeper data. Free fallbacks are used automatically if keys are missing.

---

**Dune Analytics**
- What: Custom SQL queries, dashboards
- Cost: Paid (2,500 free credits/month)
- Fallback: Flipside Crypto (free)
- Get key: https://dune.com/
- API Key: [input or press Enter to skip]

---

**Token Terminal**
- What: Fundamentals, revenue metrics, P/S ratios
- Cost: Paid
- Fallback: DeFiLlama (free)
- Get key: https://tokenterminal.com/
- API Key: [input or press Enter to skip]

---

**Messari**
- What: Analyst research reports, screener
- Cost: Paid
- Fallback: The Block + CoinGecko (free)
- Get key: https://messari.io/
- API Key: [input or press Enter to skip]

---

**Arkham Intelligence**
- What: Entity labels, whale tracking
- Cost: Paid (free tier available)
- Fallback: DeBank + Blockscout (free)
- Get key: https://arkham.intelligence/
- API Key: [input or press Enter to skip]

---

**AgentCash / twit.sh**
- What: Exact Twitter follower counts, real-time metrics
- Cost: API key required
- Fallback: Twitter WebSearch (approximate)
- Get key: https://agentcash.ai/
- API Key: [input or press Enter to skip]

---

**LunarCrush**
- What: Social sentiment scoring
- Cost: Paid
- Fallback: Manual keyword analysis
- Get key: https://lunarcrush.com/
- API Key: [input or press Enter to skip]

---

**Nansen**
- What: Smart money tracking, wallet labels
- Cost: Paid
- Fallback: Arkham (if key) → DeBank (free)
- Get key: https://nansen.ai/
- API Key: [input or press Enter to skip]

---

**Alchemy**
- What: Deep RPC, transaction traces
- Cost: Paid (free tier: 300M CU/month)
- Fallback: Blockscout (free)
- Get key: https://alchemy.com/
- API Key: [input or press Enter to skip]
```

## Step 6: Rate Limiting

```markdown
## Rate Limiting

To avoid getting rate limited, delays are added between requests.

| Speed | Delay | Best For |
|-------|-------|----------|
| Fast | 1000ms | Quick research, may hit limits |
| Normal | 2000ms | Balanced (recommended) |
| Slow | 3000ms | Safe for sensitive sources |

Select [Normal]:
```

## Step 7: Custom Sources (Optional)

```markdown
## Custom Data Sources

Do you have custom data to add? Examples:
- Excel/CSV with event attendees
- Google Sheet with portfolio companies
- Notion database with leads
- Your own API endpoint

Describe your source, or press Enter to skip.
```

If user provides custom source:
```markdown
Source type:
1. Excel/CSV file
2. Google Sheet
3. Notion database
4. REST API
5. Other

Select: [input]

Path/URL: [input]
Schema (column names mapping):
  Company Name: [input]
  Website: [input]
  Chain: [input]
```

## Step 8: Save Configuration

Save to `config/sources.yaml`:

```yaml
version: "1.0.0"

# =============================================================================
# SOURCE ENABLING
# =============================================================================

sources:
  # Core Free (always enabled)
  defillama:
    enabled: true
    type: api
    description: "TVL, protocols, yields, fees, revenue"
    
  coingecko:
    enabled: true
    type: api
    description: "Prices, market cap, categories"
    
  debank:
    enabled: true
    type: api
    description: "Portfolio tracking, holdings"
    
  flipside:
    enabled: true
    type: api
    description: "SQL on-chain analytics"
    
  blockscout:
    enabled: true
    type: api
    description: "Transactions, contracts, multi-chain"
    
  snapshot:
    enabled: true
    type: api
    description: "Governance proposals, voting"
    
  github:
    enabled: true
    type: websearch
    description: "Code activity, repos"
    
  crypto_fundraising:
    enabled: true
    type: browser
    description: "Deal flow, rounds, investors"
    
  rootdata:
    enabled: true
    type: browser
    description: "Projects, fundraising, investors"
    
  twitter:
    enabled: true
    type: websearch
    description: "Followers, tweets, activity"
    
  the_block:
    enabled: true
    type: browser
    description: "News, metrics, research"
    
  coindesk:
    enabled: true
    type: browser
    description: "Crypto news"
    
  cointelegraph:
    enabled: true
    type: browser
    description: "Crypto news"
    
  # Optional Free
  coinmarketcap:
    enabled: true
    type: api
    description: "Prices, rankings"
    
  rootdata:
    enabled: true
    type: browser
    description: "Projects, fundraising"
    
  crunchbase:
    enabled: true
    type: browser
    description: "Funding, company info"
    
  # Premium (only active if API key present)
  dune:
    enabled: false
    type: api
    description: "Custom SQL queries"
    
  token_terminal:
    enabled: false
    type: api
    description: "Fundamentals, revenue metrics"
    
  messari:
    enabled: false
    type: api
    description: "Analyst research"
    
  arkham:
    enabled: false
    type: api
    description: "Entity intelligence"
    
  agentcash:
    enabled: false
    type: api
    description: "Exact Twitter metrics"
    
  lunarcrush:
    enabled: false
    type: api
    description: "Social sentiment"
    
  nansen:
    enabled: false
    type: api
    description: "Smart money tracking"
    
  alchemy:
    enabled: false
    type: api
    description: "Deep RPC, traces"

# =============================================================================
# API KEYS
# =============================================================================

api_keys:
  coingecko: null
  coinmarketcap: null
  debank: null
  flipside: null
  blockscout: null
  rootdata: null
  crunchbase: null
  dune: null
  token_terminal: null
  messari: null
  arkham: null
  agentcash: null
  lunarcrush: null
  nansen: null
  alchemy: null

# =============================================================================
# CUSTOM SOURCES
# =============================================================================

custom_sources: []

# =============================================================================
# RATE LIMITING
# =============================================================================

rate_limiting:
  enabled: true
  default_delay_ms: 2000
  delays:
    api: 500
    websearch: 1000
    browser: 2000
    custom: 0

# =============================================================================
# DISCOVERY PREFERENCES
# =============================================================================

discovery:
  default_limit: 10
  max_results: 50
  show_filters: true
  prompt_research: true
  show_source_labels: true
  show_data_quality: true
```

## Step 9: Verify

```markdown
## Setup Complete

Configuration saved to: `config/sources.yaml`

Summary:
- Core sources: 14 enabled (free)
- Optional sources: {N} enabled
- Premium sources: {N} configured with API keys
- Custom sources: {N} added

Test your setup:
/crypto-discovery discover defillama protocols under 5M TVL on Base

Or research a specific project:
/crypto-discovery research Uniswap
```

## Error Handling

| Scenario | Response |
|----------|----------|
| Config write fails | Show error, offer manual save path |
| Invalid API key format | Warn, allow saving anyway |
| Tool not available | Show fallback instructions |
| User skips everything | Save with defaults (14 core sources only) |
