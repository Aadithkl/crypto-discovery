# Crypto Discovery

A general-purpose crypto/Web3 research sub-agent for Claude Code and compatible platforms. Discover and deep-research projects using 25+ data sources. The free core works out of the box — add optional API keys to unlock premium data.

## Features

- **25+ Data Sources** — DeFiLlama, CoinGecko, DeBank, Flipside, Blockscout, RootData, CryptoFundraising, Dove Metrics, Twitter, GitHub, Snapshot, and more
- **Free Core** — 14 sources work without any API keys
- **Premium Upgrades** — Add keys for Dune, Token Terminal, Messari, Arkham, AgentCash, and more
- **Natural Language Queries** — "defillama protocols under 5M TVL on Base"
- **Deep Research** — 7-phase neutral research: Overview → On-Chain → Funding → Social → Technical → Governance → Verify
- **Watchlist** — Save and track projects over time
- **Cross-Reference Verification** — Flags data conflicts between sources
- **Neutral & Factual** — No hype, no investment advice, every fact cited

## Quick Start

### Install

```bash
# Clone the repo
git clone https://github.com/Aadithkl/crypto-discovery.git ~/.claude/plugins/crypto-discovery

# Register the skill (Claude Code)
mkdir -p ~/.claude/skills/crypto-discovery
cp ~/.claude/plugins/crypto-discovery/skills/crypto-discovery/SKILL.md ~/.claude/skills/crypto-discovery/SKILL.md

# Start a new Claude Code session and run setup
/crypto-discovery setup
```

### Discover Projects

```
/crypto-discovery discover defillama protocols under 5M TVL on Base
/crypto-discovery discover twitter accounts 5k-20k followers in DeFi
/crypto-discovery discover rootdata projects raised series a this year
```

### Research a Project

```
/crypto-discovery research Uniswap
/crypto-discovery research Aave
```

### Watchlist

```
/crypto-discovery watchlist add Uniswap dex ethereum
/crypto-discovery watchlist
/crypto-discovery watchlist research Uniswap
/crypto-discovery watchlist remove Uniswap
```

## Source Catalog

### Core Free (14 sources, no keys)

| Source | Type | Data |
|--------|------|------|
| DeFiLlama | API | TVL, protocols, yields, fees |
| CoinGecko | API | Prices, market cap |
| DeBank | API | Portfolios, holdings |
| Flipside Crypto | API | SQL on-chain analytics |
| Blockscout | API | Transactions, contracts, multi-chain |
| Snapshot | API | Governance |
| GitHub | WebSearch | Code activity |
| CryptoFundraising.info | Browser | Deal flow |
| Dove Metrics | Browser | Fundraising DB |
| Twitter | WebSearch | Social data |
| The Block | Browser | News |
| CoinDesk | Browser | News |
| Cointelegraph | Browser | News |
| Custom | File | Your data |

### Optional Free (3 sources, optional keys)

| Source | Data |
|--------|------|
| CoinMarketCap | Prices, rankings |
| RootData | Projects, fundraising |
| Crunchbase | Company info |

### Premium (8 sources, API key required)

| Source | Data | Free Fallback |
|--------|------|---------------|
| Dune | Custom queries | Flipside Crypto |
| Token Terminal | Fundamentals | DeFiLlama |
| Messari | Analyst research | The Block |
| Arkham | Whale tracking | DeBank |
| AgentCash | Exact Twitter metrics | Twitter WebSearch |
| LunarCrush | Sentiment | Manual analysis |
| Nansen | Smart money | Arkham → DeBank |
| Alchemy | Deep RPC | Blockscout |

## Architecture

```
crypto-discovery/
├── skills/crypto-discovery/SKILL.md    # Skill registration
├── commands/                            # Command definitions
│   ├── discover.md                      # /crypto-discovery discover
│   ├── research.md                      # /crypto-discovery research
│   └── setup.md                         # /crypto-discovery setup
├── lib/
│   └── source_manager.py               # Core Python module
├── config/
│   └── sources.example.yaml            # Configuration template
├── watchlist/
│   └── watchlist.yaml                  # Saved projects
├── references/
│   └── research-template.md            # Research output template
├── hooks/
│   └── session-start.sh                # Session context
├── README.md
├── CLAUDE.md                           # Agent instructions
└── LICENSE
```

## Core Python Module

The `lib/source_manager.py` module provides:

- `SourceManager` — Orchestrates all 25 sources
- `QueryInterpreter` — Parses natural language into structured queries
- `RateLimiter` — Per-source-type rate limiting
- `ResultMerger` — Merges and scores multi-source results
- `WatchlistManager` — YAML-based project tracking
- `ConfigLoader` — Configuration management

### Usage Example

```python
from lib.source_manager import create_source_manager

# Load config
sm = create_source_manager()

# Discover projects
results = sm.discover("defillama protocols under 5M TVL on Base")

# Print top results
for r in results[:10]:
    print(f"{r.name}: TVL=${r.tvl:,.0f}, Chain={r.chain}")
```

## Configuration

All settings in `config/sources.yaml` (gitignored). See `config/sources.example.yaml` for full documentation.

### Minimal Config (Free Core Only)

```yaml
sources:
  defillama: { enabled: true }
  coingecko: { enabled: true }
  # ... (13 more core sources)

api_keys: {}  # Empty — all free
```

### With Premium Keys

```yaml
api_keys:
  dune: "your-dune-key"
  token_terminal: "your-tt-key"
  messari: "your-messari-key"
  agentcash: "your-agentcash-key"
```

Premium sources auto-activate when keys are present. Free fallbacks used otherwise.

## Custom Sources

Add your own data in `config/sources.yaml`:

```yaml
custom_sources:
  - name: "event_attendees"
    type: "excel"
    path: "~/events.xlsx"
    schema:
      company: "Company Name"
      website: "URL"
```

## Platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| Claude Code | ✅ Full | Primary platform |
| Cline | ✅ Full | Compatible |
| Gemini CLI | ✅ Full | Use `google_web_search` |
| OpenCode | ✅ Full | Use `webfetch` / `websearch` |

## Research Output

Research reports follow a neutral 10-section template:

1. Executive Summary
2. Overview
3. On-Chain Data
4. Funding & Investors
5. Social & Community
6. Technical
7. Governance
8. Competitive Landscape
9. Sources
10. Data Quality Notes

All metrics are labeled as exact or approximate. Conflicts between sources are flagged.

## Development

```bash
# Clone
git clone https://github.com/Aadithkl/crypto-discovery.git
cd crypto-discovery

# The project is pure Python + Markdown — no build step needed
# lib/source_manager.py is the core module
```

## Contributing

Pull requests welcome! Areas for contribution:

- Additional data sources
- Better query parsing
- More research phases
- Platform integrations
- Bug fixes

## License

MIT — see [LICENSE](LICENSE)

## Support

- GitHub Issues: https://github.com/Aadithkl/crypto-discovery/issues
- Discussions: https://github.com/Aadithkl/crypto-discovery/discussions

---

**Note:** Crypto Discovery provides factual research data. It is not investment advice. Always do your own research.
