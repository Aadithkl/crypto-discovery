---
name: crypto-discovery
description: |
  Crypto research sub-agent for Claude Code. Discover and research crypto/Web3 projects 
  using 24+ data sources. Free core works out of the box. Add API keys to unlock premium data.
  Deep research pipeline with parallel sub-agents, field validation, and report generation.
version: 2.0.0
---

# Crypto Discovery

A general-purpose crypto research sub-agent that can be installed into Claude Code (or compatible platforms) to discover and deep-research crypto/Web3 projects.

## Philosophy

- **Neutral, not salesy.** No BD language, no investment advice, no hype.
- **Pure factual research.** Metrics, funding, tech, community, governance.
- **Free core, optional premium.** 13 sources work without any API keys. Add keys to unlock 11 more.
- **Cite everything.** Every fact must have a source URL.
- **Deep research pipeline.** Parallel sub-agents, field validation, uncertainty tracking, resume capability.

## Commands

| Command | Description |
|---------|-------------|
| `/crypto-discovery discover <query>` | Find projects by natural language across all enabled sources |
| `/crypto-discovery research <project>` | Deep research on a single project (1-item pipeline) |
| `/crypto-discovery research "<topic>"` | Deep research on a topic (multi-item pipeline) |
| `/crypto-discovery research continue` | Resume incomplete deep research (skip completed items) |
| `/crypto-discovery research report` | Regenerate report from existing JSON results |
| `/crypto-discovery watchlist` | List saved/bookmarked projects |
| `/crypto-discovery watchlist add <project>` | Save a project to watchlist |
| `/crypto-discovery watchlist remove <project>` | Remove from watchlist |
| `/crypto-discovery setup` | Configure sources, API keys, rate limits |

## Deep Research Pipeline

The `/crypto-discovery research` command uses a deep research pipeline adapted from System 2:

1. **Outline Generation** — Detect single project vs topic, generate item list, web search supplement
2. **Field Schema** — Load crypto-specific field definitions (6 categories, ~30 fields), user can customize
3. **Parallel Sub-Agent Execution** — Launch background agents (default: 5 per batch) to research each item using all 24 crypto sources
4. **Validation Loop** — Each sub-agent validates JSON output against field schema, re-searches missing required fields
5. **Uncertainty Tracking** — Fields that can't be confirmed are marked `[uncertain]` and listed in `uncertain[]` array
6. **Report Generation** — Python script reads all JSONs, generates comparative markdown report with source citations

### Output Structure

```
Research/{topic_slug}/
├── outline.yaml      # Items list + execution config
├── fields.yaml       # Field definitions (customizable)
├── results/           # JSON per project
│   ├── uniswap.json
│   ├── arbitrum.json
│   └── ...
└── report.md          # Generated comparative report
```

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

# 5. Research a single project
/crypto-discovery research Uniswap

# 6. Research a topic (multi-item)
/crypto-discovery research "L2 protocols on Ethereum"

# 7. Resume incomplete research
/crypto-discovery research continue

# 8. Regenerate report
/crypto-discovery research report
```

## Source Catalog (24 Sources)

### Core Free (13 sources — no keys needed)

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
| RootData | Browser | Projects, fundraising, investors |
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
6. **Deep Research** — Parallel sub-agents research each item using all 24 sources, validate JSON, track uncertainty

## Architecture

```
crypto-discovery/
├── skills/crypto-discovery/SKILL.md    # Skill registration
├── commands/                            # Command routing & UX
│   ├── discover.md                      # /crypto-discovery discover
│   ├── research.md                      # /crypto-discovery research (deep research pipeline)
│   └── setup.md                         # /crypto-discovery setup
├── lib/
│   ├── source_manager.py               # Core Python module
│   └── deep-research/
│       ├── validate_json.py            # JSON field coverage validator
│       └── generate_report.py          # JSON → markdown report generator
├── config/
│   └── sources.example.yaml            # 24-source configuration template
├── watchlist/
│   └── watchlist.yaml                  # Persisted bookmarks
├── references/
│   ├── deep-research-fields.yaml       # Default crypto field definitions
│   ├── deep-research-outline-template.yaml # Outline template
│   └── deep-research-subagent.md       # Sub-agent prompt template
├── hooks/
│   └── session-start.sh                # Context loader
├── README.md
├── CLAUDE.md                           # Agent instructions
└── LICENSE
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