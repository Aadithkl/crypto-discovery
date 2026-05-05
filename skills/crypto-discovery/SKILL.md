---
name: crypto-discovery
description: |
  Crypto research sub-agent for Claude Code. Discover and research crypto/Web3 projects 
  using 25+ data sources. Free core works out of the box. Add API keys to unlock premium data.
version: 1.0.0
---

# Crypto Discovery

A general-purpose crypto research sub-agent that can be installed into Claude Code (or compatible platforms) to discover and deep-research crypto/Web3 projects.

## Philosophy

- **Neutral, not salesy.** No BD language, no investment advice, no hype.
- **Pure factual research.** Metrics, funding, tech, community, governance.
- **Free core, optional premium.** 14 sources work without any API keys. Add keys to unlock 11 more.
- **Cite everything.** Every fact must have a source URL.

## Commands

| Command | Description |
|---------|-------------|
| `/crypto-discovery discover <query>` | Find projects by natural language across all enabled sources |
| `/crypto-discovery research <project>` | Deep-dive factual research on a specific project (7 phases) |
| `/crypto-discovery watchlist` | List saved/bookmarked projects |
| `/crypto-discovery watchlist add <project> [tags...]` | Save a project to watchlist |
| `/crypto-discovery watchlist remove <project>` | Remove from watchlist |
| `/crypto-discovery setup` | Configure sources, API keys, rate limits |

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/Aadithkl/crypto-discovery.git ~/.claude/plugins/crypto-discovery

# 2. Register the skill
mkdir -p ~/.claude/skills/crypto-discovery
cp ~/.claude/plugins/crypto-discovery/skills/crypto-discovery/SKILL.md ~/.claude/skills/crypto-discovery/SKILL.md

# 3. Start a new Claude Code session and run setup
/crypto-discovery setup

# 4. Discover projects
/crypto-discovery discover defillama protocols under 5M TVL on Base

# 5. Research a project
/crypto-discovery research Uniswap
```

## Source Catalog (25 Sources)

### Core Free (14 sources — no keys needed)

| Source | Type | Data |
|--------|------|------|
| DeFiLlama | API | TVL, protocols, yields, fees, revenue |
| CoinGecko | API | Prices, market cap, categories |
| DeBank | API | Portfolios, holdings, protocol usage |
| Flipside Crypto | API | SQL on-chain analytics |
| Blockscout | API | Transactions, contracts, multi-chain |
| Snapshot | API | Governance proposals, voting |
| GitHub | WebSearch | Repos, stars, commits, contributors |
| CryptoFundraising.info | Browser | Deal flow, rounds, investors |
| Dove Metrics | Browser | Crypto fundraising database |
| Twitter/X | WebSearch | Followers, tweets, activity |
| The Block | Browser | News, metrics, research |
| CoinDesk | Browser | General crypto news |
| Cointelegraph | Browser | General crypto news |
| Custom | File/API | Excel, Sheets, Notion, user API |

### Optional Free (3 sources — optional keys for higher limits)

| Source | Type | Data | Key Required? |
|--------|------|------|---------------|
| CoinMarketCap | API | Prices, rankings | Optional |
| RootData | Browser | Projects, fundraising | Optional |
| Crunchbase | Browser | Funding, stage, company info | Optional |

### Premium (8 sources — API key required)

| Source | Type | Data | Free Fallback |
|--------|------|------|---------------|
| Dune | API | Custom SQL queries | Flipside Crypto |
| Token Terminal | API | Fundamentals, revenue multiples | DeFiLlama |
| Messari | API | Analyst research, screener | The Block + CoinGecko |
| Arkham | API | Entity intelligence, whale labels | DeBank + Blockscout |
| AgentCash (twit.sh) | API | Exact Twitter follower counts | Twitter WebSearch |
| LunarCrush | API | Social sentiment scoring | Manual keyword analysis |
| Nansen | API | Smart money, wallet labels | Arkham → DeBank |
| Alchemy | API | Deep RPC, traces | Blockscout |

## How It Works

1. **Load Config** — `config/sources.yaml` determines which sources are enabled and which API keys are available
2. **Parse Query** — Natural language is parsed into `{source, filters, original_input}`
3. **Route to Sources** — Query is sent to the appropriate source handlers based on enabled sources and available keys
4. **Rate Limit** — Automatic delays per source type (API: 500ms, WebSearch: 1s, Browser: 2s)
5. **Merge & Score** — Results from multiple sources are merged, deduplicated, and scored by filter match
6. **Research (optional)** — Deep-dive runs 7 phases: Overview → On-Chain → Funding → Social → Technical → Governance → Verify

## Architecture

```
crypto-discovery/
├── skills/crypto-discovery/SKILL.md    # Skill registration
├── commands/                            # Command routing & UX
│   ├── discover.md                      # /crypto-discovery discover
│   ├── research.md                      # /crypto-discovery research
│   └── setup.md                         # /crypto-discovery setup
├── lib/
│   └── source_manager.py               # Core Python: SourceManager, QueryInterpreter, RateLimiter, ResultMerger, WatchlistManager, ResearchEngine
├── config/
│   └── sources.example.yaml            # 25-source configuration template
├── watchlist/
│   └── watchlist.yaml                  # Persisted bookmarks
├── references/
│   └── research-template.md            # Neutral 7-phase research output
├── hooks/
│   └── session-start.sh                # Context loader
├── README.md                           # This file
├── CLAUDE.md                           # Agent instructions
└── LICENSE                             # MIT
```

## Configuration

All source settings live in `config/sources.yaml` (gitignored). See `config/sources.example.yaml` for full documentation.

### Required: None
The free core works without any API keys.

### Optional: API Keys
Add keys to unlock premium sources. Free fallbacks are used automatically if a key is missing.

```yaml
api_keys:
  dune: "your-dune-api-key"
  token_terminal: "your-tt-key"
  messari: "your-messari-key"
  arkham: "your-arkham-key"
  agentcash: "your-agentcash-key"
  lunarcrush: "your-lunarcrush-key"
  nansen: "your-nansen-key"
  alchemy: "your-alchemy-key"
```

## Custom Sources

Add your own data sources in `config/sources.yaml`:

```yaml
custom_sources:
  - name: "event_attendees"
    type: "excel"
    path: "~/events.xlsx"
    schema:
      company: "Company Name"
      website: "URL"
      chain: "Blockchain"
```

## Watchlist

Save projects for later tracking:

```
/crypto-discovery watchlist add Uniswap dex ethereum amm
/crypto-discovery watchlist
/crypto-discovery watchlist research Uniswap
/crypto-discovery watchlist remove Uniswap
```

Watchlist is stored in `watchlist/watchlist.yaml`.

## License

MIT — see LICENSE file.

## Contributing

Pull requests welcome. See README.md for development setup.

## Support

Open an issue on GitHub: https://github.com/Aadithkl/crypto-discovery/issues
