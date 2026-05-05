# /crypto-discovery discover — Find Crypto Projects

## Purpose

Discover crypto/Web3 projects using natural language queries across 24+ data sources.

## Step 0: Load Config

Read `config/sources.yaml` from the plugin directory. If missing, run `/crypto-discovery setup`.

Load:
- Enabled sources
- API keys
- Custom sources
- Rate limiting settings

## Step 1: Parse User Input

User must specify at least ONE source or data type. Extract:
1. **Source(s)** — Required context (defillama, twitter, rootdata, etc.)
2. **Filters** — Optional (TVL, followers, category, chain, stage, etc.)

If no source context is found, infer from keywords or prompt:
```
"Please specify what you're looking for. Examples:
- 'defillama protocols under 5M TVL on Arbitrum'
- 'twitter accounts 5k-20k followers in DeFi'
- 'rootdata projects that raised series a this year'
- 'protocols with high yield on Base'

Available sources: defillama, coingecko, debank, flipside, blockscout, 
rootdata, crypto_fundraising, twitter, github, crunchbase,
orbis, and your custom sources."
```

## Step 2: Identify Sources

Map input to source types using keyword matching:

| Keyword | Primary Source | Fallback |
|---------|---------------|----------|
| "tvl", "protocol", "yield", "defillama" | DeFiLlama | CoinGecko |
| "price", "market cap", "token" | CoinGecko | CoinMarketCap |
| "portfolio", "holders", "on-chain" | DeBank | Blockscout |
| "query", "analytics", "dashboard" | Flipside Crypto | Dune (if key) |
| "contract", "transaction", "verified" | Blockscout | Alchemy (if key) |
| "fundraising", "raised", "investors" | CryptoFundraising.info | RootData |
| "deal flow", "rounds" | RootData | CryptoFundraising.info |
| "followers", "twitter", "social" | Twitter WebSearch | AgentCash (if key) |
| "code", "repo", "github", "commits" | GitHub | — |
| "governance", "proposal", "vote" | Snapshot | — |
| "news", "recent" | The Block | CoinDesk, Cointelegraph |

If multiple sources match, query all enabled ones and merge results.

## Step 3: Build & Execute Queries

### API Sources (DeFiLlama, CoinGecko, DeBank, Flipside, Blockscout, Snapshot)

**If WebFetch is available (Claude/Cline):**
```
1. Use WebFetch to call the API endpoint
2. Parse JSON response
3. Apply filters from user input
4. Return structured results
```

**Example: DeFiLlama**
```
WebFetch: https://api.llama.fi/protocols
Filter: tvl >= {tvl_min}, tvl <= {tvl_max}, chain contains '{chain}', category contains '{category}'
Return: name, tvl, chain, category, url, twitter, change_1d, change_7d
```

**Example: CoinGecko**
```
WebFetch: https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category={category}&order=market_cap_desc
Filter: market_cap >= {mcap_min}, market_cap <= {mcap_max}
Return: name, symbol, market_cap, current_price, total_volume, price_change_24h
```

**Example: Blockscout**
```
WebFetch: https://{chain}.blockscout.com/api/v2/main-page/transactions
Or: https://eth.blockscout.com/api/v2/addresses/{address}
Return: transactions, verified contracts, gas used
```

**Example: Flipside Crypto**
```
WebFetch: https://api.flipsidecrypto.com/api/v2/queries/{query_id}/data/latest
Or use their SQL API
Return: Custom query results
```

### Browser Sources (RootData, CryptoFundraising, Crunchbase)

**If Playwright MCP is available:**
```
1. Navigate to source website
2. Extract project/company data
3. Return structured results
```

**If WebFetch only:**
```
1. WebFetch the specific project/company page
2. Parse HTML for structured data
3. Return extracted fields
```

**Example: RootData**
```
WebFetch: https://www.rootdata.com/Projects/{project_name}
Return: funding_rounds, investors, valuation, founded_date
```

**Example: CryptoFundraising**
```
WebFetch: https://crypto-fundraising.info/projects/{project_name}
Return: rounds, amounts, investors, dates
```

### WebSearch Sources (Twitter, GitHub)

**Twitter:**
```
WebSearch: "site:twitter.com {project_name} followers"
Or: "{project_name} twitter followers"
Parse: Follower count (approximate), recent activity
```

**GitHub:**
```
WebSearch: "{project_name} github stars"
Or direct: https://api.github.com/search/repositories?q={project_name}
Return: repos, stars, last_push, language
```

### Premium Sources (with API keys)

Only query if API key is configured and source is enabled.

**Dune:**
```
WebFetch: https://api.dune.com/api/v1/query/{query_id}/results
Headers: "x-dune-api-key: {key}"
```

**AgentCash / twit.sh:**
```
WebFetch: https://api.agentcash.ai/twit/users/by/username/{username}
Headers: "Authorization: Bearer {key}"
Return: exact follower_count, following_count, tweet_count
```

**Token Terminal:**
```
WebFetch: https://api.tokenterminal.com/v2/projects/{project_id}/metrics
Headers: "Authorization: Bearer {key}"
```

## Step 4: Rate Limiting

Automatic delays based on source type:

| Source Type | Delay | Rationale |
|-------------|-------|-----------|
| API | 500ms | Fast, but respect rate limits |
| WebSearch | 1000ms | Search engines are stricter |
| Browser (Playwright) | 2000ms | Simulates human browsing |
| Custom File | 0ms | Local files, no delay |

## Step 5: Process Results

### Single Source
Return results directly with matched filters highlighted.

### Multiple Sources
1. Query each matching source
2. Match by project name (fuzzy matching)
3. Score by number of matching filters
4. Merge and rank by score
5. Flag conflicts between sources

### Scoring
```python
match_score = sum(1 for filter in filters if filter_matches(result, filter))
```

Results sorted by `match_score` descending.

## Step 6: Output Format

```markdown
# Discover Results: "{user query}"
# Sources: {source list} | Filters: {matched filters}

| # | Project | Key Metric 1 | Key Metric 2 | Matched Filters | Sources |
|---|---------|-------------|-------------|-----------------|---------|
| 1 | Uniswap | $4.2B TVL | Ethereum | TVL ✓, Chain ✓ | DeFiLlama |
| 2 | Aave | $12.1B TVL | Multi-chain | TVL ✓ | DeFiLlama, DeBank |
| 3 | Jito | $2.8B TVL | Solana | TVL ✓, Chain ✓ | DeFiLlama |

# {N} results found from {X} sources
# Matched on: TVL > $1B, Chain = Ethereum/Solana
# Data quality: {exact count} exact metrics, {approx count} approximate
```

If results include approximate metrics (from WebSearch fallback), label them:
```
⚠ Follower count is approximate (Twitter WebSearch). 
  Add AgentCash API key for exact counts: /crypto-discovery setup
```

## Step 7: Next Steps

Offer:
- "Type a number or name to research any project in depth"
- "/crypto-discovery watchlist add {project}" to save for later
- "/crypto-discovery discover" to refine search

## Error Handling

| Error | Response |
|-------|----------|
| No source context | Prompt with examples |
| Source disabled | Offer to enable via setup |
| No results | Suggest relaxing filters or trying a different source |
| Rate limited | Wait and retry with exponential backoff |
| API error | Try fallback source, report error |
| Missing API key for premium | Use free fallback, suggest adding key |

## Platform-Specific Notes

### Claude / Cline
- Use `WebFetch` for direct API calls
- Use `WebSearch` for web searches
- Use `Playwright MCP` if available for browser scraping

### Gemini
- Use `google_web_search` for web queries
- Use `web_fetch` for fetching specific URLs
- Built-in web search capabilities

### OpenCode
- Use `webfetch` for URL fetching
- Use `websearch` for web searches
- Use `bash` with curl as fallback
