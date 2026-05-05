# Crypto Discovery

A general-purpose crypto/Web3 research sub-agent for Claude Code and compatible platforms. Discover and deep-research projects using 24+ data sources. The free core works out of the box — add optional API keys to unlock premium data.

## Features

- **24+ Data Sources** — DeFiLlama, CoinGecko, DeBank, Flipside, Blockscout, RootData, CryptoFundraising, Twitter, GitHub, Snapshot, and more
- **Free Core** — 13 sources work without any API keys
- **Premium Upgrades** — Add keys for Dune, Token Terminal, Messari, Arkham, AgentCash, and more
- **Natural Language Queries** — "defillama protocols under 5M TVL on Base"
- **Deep Research Pipeline** — Parallel sub-agents, field validation, uncertainty tracking, resume capability, report generation
- **Multi-Item Research** — Research a topic (e.g., "L2 protocols on Ethereum") with multiple projects in parallel
- **Single Project Research** — Deep-dive on one project with full 6-category coverage
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

### Research a Single Project

```
/crypto-discovery research Uniswap
```

This runs the deep research pipeline for a single project:
1. Creates a 1-item outline
2. Loads default crypto field schema
3. Launches 1 sub-agent that researches using all 24 sources
4. Validates JSON output against field schema
5. Generates detailed markdown report

### Research a Topic (Multi-Item)

```
/crypto-discovery research "L2 protocols on Ethereum"
```

This runs the full deep research pipeline:
1. Generates outline of relevant projects (Arbitrum, Optimism, Base, etc.)
2. Web search supplements for latest projects
3. User confirms outline and customizes fields
4. Parallel sub-agents research each project (batch of 5)
5. Each sub-agent validates, re-searches if needed, tracks uncertainty
6. Generates comparative report with summary table

### Resume & Report

```
/crypto-discovery research continue    # Resume incomplete research (skip done items)
/crypto-discovery research report      # Regenerate report from existing JSONs
```

### Watchlist

```
/crypto-discovery watchlist add Uniswap dex ethereum
/crypto-discovery watchlist
/crypto-discovery watchlist research Uniswap
/crypto-discovery watchlist remove Uniswap
```

## Deep Research Pipeline

The research command uses a structured pipeline adapted from System 2's deep research architecture:

### 1. Outline Generation
- Detects single project vs topic
- Uses model knowledge + web search to build item list
- Saves `outline.yaml` to `Research/{topic_slug}/`

### 2. Field Schema
- Loads defaults from `references/deep-research-fields.yaml` (6 categories, ~30 fields)
- User can add/remove/customize fields
- Saves `fields.yaml` to `Research/{topic_slug}/`

### 3. Parallel Sub-Agent Execution
- Resumes from previous runs (skips completed JSONs)
- Batches sub-agents (default: 5 parallel)
- Each sub-agent researches one project using all 24 crypto sources
- Validates JSON against field schema
- Re-searches missing required fields if validation fails
- Tracks uncertainty with `[uncertain]` tags and `uncertain[]` array
- Saves JSON to `Research/{topic_slug}/results/{slug}.json`

### 4. Report Generation
- Reads all JSONs from `results/`
- User selects summary table fields
- Generates comparative markdown report with:
  - Summary table (one row per project)
  - Detailed per-project sections by category
  - Data quality notes (uncertain fields flagged)
  - Source citations on every fact

### Output Structure

```
Research/
├── uniswap/                    # Single project
│   ├── outline.yaml
│   ├── fields.yaml
│   ├── results/
│   │   └── uniswap.json
│   └── report.md
├── l2-protocols-on-ethereum/   # Multi-item
│   ├── outline.yaml
│   ├── fields.yaml
│   ├── results/
│   │   ├── arbitrum.json
│   │   ├── optimism.json
│   │   ├── base.json
│   │   └── ...
│   └── report.md
```

## Field Schema

Default fields by category:

| Category | Fields | Required |
|----------|--------|----------|
| Overview | name, website, founded, category, chains, description, token_symbol | name, website, category, chains, description |
| On-Chain Data | tvl, tvl_change_7d, market_cap, fdv, token_price, fees_24h, revenue_24h, active_addresses_24h, transactions_24h | tvl |
| Funding | total_raised, funding_rounds, lead_investors, latest_valuation | — |
| Social | twitter_handle, twitter_followers, github_org, github_stars, github_last_commit, github_contributors, discord_members | — |
| Technical | tech_stack, audits, security_incidents, bug_bounty | — |
| Governance | snapshot_space, proposals_count, participation_rate | — |

## Source Catalog

### Core Free (13 sources, no keys)

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
| RootData | Browser | Projects, fundraising, investors |
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
│   ├── research.md                      # /crypto-discovery research (deep research pipeline)
│   └── setup.md                         # /crypto-discovery setup
├── lib/
│   ├── source_manager.py               # Core Python module
│   └── deep-research/
│       ├── validate_json.py            # JSON field coverage validator
│       └── generate_report.py          # JSON → markdown report generator
├── config/
│   └── sources.example.yaml            # Configuration template
├── watchlist/
│   └── watchlist.yaml                  # Saved projects
├── references/
│   ├── deep-research-fields.yaml       # Default crypto field definitions
│   ├── deep-research-outline-template.yaml # Outline template
│   └── deep-research-subagent.md       # Sub-agent prompt template
├── hooks/
│   └── session-start.sh                # Session context
├── README.md
├── CLAUDE.md                           # Agent instructions
└── LICENSE
```

## Core Python Module

The `lib/source_manager.py` module provides:

- `SourceManager` — Orchestrates all 24 sources
- `QueryInterpreter` — Parses natural language into structured queries
- `RateLimiter` — Per-source-type rate limiting
- `ResultMerger` — Merges and scores multi-source results
- `WatchlistManager` — YAML-based project tracking
- `ConfigLoader` — Configuration management

### Deep Research Tools

- `lib/deep-research/validate_json.py` — Validates JSON against `fields.yaml`, reports coverage %, missing required fields
- `lib/deep-research/generate_report.py` — Reads JSON results + field schema, generates comparative markdown report

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

### Validation Example

```bash
# Validate a research JSON against field schema
python lib/deep-research/validate_json.py -f Research/uniswap/fields.yaml -j Research/uniswap/results/uniswap.json

# Generate report from all JSON results
python lib/deep-research/generate_report.py \
  --topic "Uniswap" \
  --fields Research/uniswap/fields.yaml \
  --dir Research/uniswap/results \
  --output Research/uniswap/report.md \
  --summary-fields category tvl market_cap
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
| Claude Code | Full | Primary platform |
| Cline | Full | Compatible |
| Gemini CLI | Full | Use `google_web_search` |
| OpenCode | Full | Use `webfetch` / `websearch` |

## Contributing

Pull requests welcome! Areas for contribution:

- Additional data sources
- Better query parsing
- Field schema improvements
- Report template variations
- Platform integrations
- Bug fixes

## License

MIT — see [LICENSE](LICENSE)

## Support

- GitHub Issues: https://github.com/Aadithkl/crypto-discovery/issues
- Discussions: https://github.com/Aadithkl/crypto-discovery/discussions

---

**Note:** Crypto Discovery provides factual research data. It is not investment advice. Always do your own research.