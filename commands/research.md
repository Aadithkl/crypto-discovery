# /crypto-discovery research — Deep Research on a Project

## Purpose

Deep-dive factual research on a specific crypto/Web3 project. Neutral, no investment advice.

## Step 0: Load Config

Read `config/sources.yaml`. If missing, run `/crypto-discovery setup`.

## Step 1: Resolve Project Name

User provides project name (e.g., "Uniswap", "Aave", "Jito").

If ambiguous:
```
Multiple matches found:
1. Uniswap (DEX protocol, Ethereum)
2. Uniswap Labs (Company behind Uniswap)
3. UNI (Token)

Which one? Reply with the number or clarify.
```

## Step 2: Execute 7-Phase Research

Run all phases in parallel where possible. Each phase queries the relevant sources.

### Phase 1: Overview

**Sources:** CoinGecko, CoinMarketCap, RootData, Crunchbase, The Block

**Gather:**
- Name, website, founded date, HQ
- Category (DeFi, NFT, Infrastructure, Gaming, etc.)
- Chains deployed on
- Description (2-3 sentences)

**Output:**
```markdown
## 1. Overview

| Field | Detail |
|-------|--------|
| Name | {name} |
| Website | {url} |
| Founded | {year} |
| HQ | {location} |
| Category | {category} |
| Chains | {ethereum, arbitrum, base, solana, etc.} |
| Description | {2-3 sentences} |
```

### Phase 2: On-Chain Data

**Sources:** DeFiLlama, CoinGecko, DeBank, Blockscout, Flipside Crypto, Dune (if key)

**Gather:**
- TVL (total value locked)
- TVL change (1d, 7d, 1m)
- Chains with TVL breakdown
- Category
- Fees (24h)
- Revenue (24h)
- Token: symbol, market cap, FDV, price, price change
- Top holders / portfolio breakdown
- Contract verification status
- Transaction volume

**Output:**
```markdown
## 2. On-Chain Data

### DeFiLlama
| Metric | Value |
|--------|-------|
| TVL | ${tvl} |
| TVL Change (24h) | {change}% |
| Chains | {chains} |
| Category | {category} |
| Fees (24h) | ${fees} |
| Revenue (24h) | ${revenue} |

### Token
| Metric | Value |
|--------|-------|
| Symbol | {token} |
| Market Cap | ${mcap} |
| FDV | ${fdv} |
| Price | ${price} |
| Price Change (24h) | {change}% |

### Holders & Activity
- Top holders: {summary from DeBank/Blockscout}
- Contract verified: {yes/no} (Blockscout)
- Active addresses (24h): {count}
```

### Phase 3: Funding & Investors

**Sources:** CryptoFundraising.info, RootData, Crunchbase, The Block

**Gather:**
- Funding rounds (seed, series a, etc.)
- Amount raised per round
- Lead investors
- Total raised
- Valuation (if available)

**Output:**
```markdown
## 3. Funding & Investors

| Round | Date | Amount | Lead Investors | Other Investors |
|-------|------|--------|----------------|-----------------|
| Seed | {date} | ${amount} | {lead} | {others} |
| Series A | {date} | ${amount} | {lead} | {others} |

**Total Raised:** ${total}
**Latest Valuation:** ${valuation} (if available)
**Key Investors:** {list}
```

If no funding data found:
```
No fundraising data found. This may indicate:
- Bootstrapped project
- No public fundraising
- Data not yet indexed by sources
```

### Phase 4: Social & Community

**Sources:** Twitter WebSearch, AgentCash (if key), GitHub, The Block

**Gather:**
- Twitter/X handle, followers, following, account age
- Recent tweet activity
- Discord/Telegram links and member counts (if available)
- GitHub repos, stars, contributors
- Developer activity

**Output:**
```markdown
## 4. Social & Community

### Twitter/X
| Metric | Value | Source |
|--------|-------|--------|
| Handle | @{handle} | |
| Followers | {count} | {AgentCash exact OR WebSearch approx} |
| Account Age | {date} | |
| Recent Activity | {active/stale} | |

### Development
| Metric | Value |
|--------|-------|
| GitHub Org | {org} |
| Repos | {count} |
| Stars | {count} |
| Contributors | {count} |
| Last Commit | {date} |
| Primary Language | {language} |
```

### Phase 5: Technical

**Sources:** GitHub, Blockscout, The Block, CoinDesk

**Gather:**
- Tech stack (solidity, rust, etc.)
- Smart contract audits (firm, date, findings)
- Architecture (if documented)
- Security incidents (if any)

**Output:**
```markdown
## 5. Technical

### Tech Stack
{List of technologies used}

### Audits
| Firm | Date | Findings |
|------|------|----------|
| {firm} | {date} | {summary} |

### Security
- Major incidents: {list or "None found"}
- Bug bounties: {status}
```

### Phase 6: Governance

**Sources:** Snapshot, The Block

**Gather:**
- Snapshot space
- Number of proposals
- Proposal types
- Participation rate
- Voting power distribution

**Output:**
```markdown
## 6. Governance

### Snapshot
| Metric | Value |
|--------|-------|
| Space | {space_url} |
| Proposals | {count} |
| Participation Rate | {rate}% |
| Active Voters | {count} |

### Recent Proposals
| Title | Status | Participation |
|-------|--------|---------------|
| {title} | {passed/failed} | {votes} |
```

### Phase 7: Verify & Cross-Reference

**Sources:** All of the above

**Tasks:**
1. Cross-check TVL across DeFiLlama, CoinGecko, DeBank
2. Cross-check funding across CryptoFundraising, RootData
3. Cross-check token price across CoinGecko, CoinMarketCap
4. Flag any discrepancies
5. Note data quality issues

**Output:**
```markdown
## 7. Data Quality & Verification

### Cross-Reference Checks
| Metric | Source A | Source B | Match? |
|--------|----------|----------|--------|
| TVL | ${a} (DeFiLlama) | ${b} (DeBank) | {✓/✗} |
| Market Cap | ${a} (CoinGecko) | ${b} (CoinMarketCap) | {✓/✗} |
| Total Raised | ${a} (CryptoFundraising) | ${b} (RootData) | {✓/✗} |

### Discrepancies Found
- {List any conflicting data with sources}

### Data Gaps
- {Metrics that could not be found}
```

## Step 3: Competitive Landscape

**Sources:** DeFiLlama, CoinGecko, The Block

**Gather:**
- Direct competitors in same category/chain
- Key differentiators

**Output:**
```markdown
## 8. Competitive Landscape

| Competitor | Category | Key Metric | Differentiator |
|------------|----------|------------|----------------|
| {name} | {category} | {tvl/market cap} | {brief} |
| {name} | {category} | {tvl/market cap} | {brief} |
```

## Step 4: Compile Final Report

Use `references/research-template.md` as the structure. Fill in all sections.

Save to: `Research/{project_name}-{date}.md` (or user-configured path)

## Step 5: Offer Next Steps

```
Research complete. Saved to: Research/{project_name}-{date}.md

Next:
- /crypto-discovery watchlist add {project} — save for tracking
- /crypto-discovery research {competitor} — compare with competitor
- /crypto-discovery discover {category} on {chain} — find similar projects
```

## Rules

1. **Factual only** — No hype, no investment advice, no "great opportunity"
2. **Cite everything** — Every fact must have a source URL
3. **Label approximations** — "Followers: ~50K (Twitter WebSearch, approximate)"
4. **Flag conflicts** — If sources disagree, show both values
5. **Note gaps** — If data is missing, say so explicitly
6. **Neutral tone** — Describe what exists, not what could be
