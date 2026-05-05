# /crypto-discovery research — Deep Research Pipeline

## Purpose

Deep-dive factual research on crypto/Web3 projects using parallel sub-agents, structured field validation, and multi-source data. Supports both single projects and multi-item comparative research.

Neutral, no investment advice.

## Step 0: Load Config

Read `config/sources.yaml`. If missing, run `/crypto-discovery setup`.

## Step 1: Detect Mode

Determine if input is a **single project** or a **topic**:

- **Single project**: Known project name (e.g., "Uniswap", "Aave", "Jito")
  → Create 1-item outline
- **Topic**: Descriptive phrase (e.g., "L2 protocols on Ethereum", "DeFi lending protocols")
  → Generate multi-item outline

## Step 2: Generate Outline

### If Single Project

Create 1-item outline:

```yaml
topic: "Uniswap"
items:
  - name: "Uniswap"
    category: "DEX"
    description: "Decentralized exchange protocol on Ethereum"
    chains: ["ethereum"]
execution:
  batch_size: 5
  items_per_agent: 1
  output_dir: "./results"
```

### If Topic

**Step 2a: Generate initial framework**

Use model knowledge to list relevant projects for the topic.

**Step 2b: Web search supplement**

Launch a background sub-agent to search for latest projects matching the topic using crypto sources:

```
Search for {topic} related crypto projects
Use DeFiLlama, CoinGecko, RootData to find projects
List project names, categories, and brief descriptions
```

**Step 2c: Merge**

Merge model knowledge items with web search findings. Deduplicate by project name.

**Step 2d: Confirm with user**

Show the outline and ask:

```
Research Topic: {topic}
Items ({count}):
  1. {name} — {description}
  2. {name} — {description}
  ...

Add/remove items? Confirm to proceed.
```

### Save Outline

Save to `Research/{topic_slug}/outline.yaml`.

## Step 3: Field Schema

Load defaults from `references/deep-research-fields.yaml`.

Show field categories and counts:

```
Using default crypto field categories:
- Overview (7 fields, 4 required)
- On-Chain Data (9 fields, 1 required)
- Funding (4 fields, 0 required)
- Social (7 fields, 0 required)
- Technical (4 fields, 0 required)
- Governance (3 fields, 0 required)

Customize fields? (add/remove/rename categories or fields)
```

Allow user to:
- Add custom fields
- Remove categories or fields
- Rename field descriptions
- Change required flags

Save to `Research/{topic_slug}/fields.yaml`.

## Step 4: Execute Deep Research (Parallel Sub-Agents)

### Step 4a: Resume Check

Scan `Research/{topic_slug}/results/*.json` for completed items. Skip items that already have valid JSONs.

### Step 4b: Batch Execution

Batch items by `batch_size` (default: 5). For each item, launch a background sub-agent using the template from `references/deep-research-subagent.md`.

**Parameter Retrieval**:

- `{item_name}`: Item's name field from outline
- `{item_category}`: Item's category field
- `{item_description}`: Item's description field
- `{item_related_info}`: Item's complete YAML content from outline
- `{output_dir}`: `Research/{topic_slug}/results`
- `{fields_path}`: Absolute path to `Research/{topic_slug}/fields.yaml`
- `{output_path}`: Absolute path to `Research/{topic_slug}/results/{item_slug}.json`
- `{validate_path}`: Absolute path to `lib/deep-research/validate_json.py`

**Sub-Agent Prompt Template** (from `references/deep-research-subagent.md`):

```
Research {item_name}, output structured JSON to {output_path}

Field definitions: Read {fields_path}
Source routing: Use crypto-discovery's 24 data sources
Citation rules: Every fact needs source URL
Data quality: Label exact vs approximate
Uncertainty: Mark [uncertain] + uncertain[] array
Output: {output_path}
Validation: python {validate_path} -f {fields_path} -j {output_path}
Task complete only after validation passes.
```

**One-shot Example** (assuming researching Arbitrum):

```
Research name: Arbitrum
category: L2
description: Optimistic rollup on Ethereum by Offchain Labs
chains: ethereum

Output structured JSON to Research/l2-protocols-on-ethereum/results/arbitrum.json

Field definitions: Read Research/l2-protocols-on-ethereum/fields.yaml

Source routing:
- Overview: CoinGecko, RootData, CoinMarketCap
- On-Chain Data: DeFiLlama, CoinGecko, DeBank, Blockscout
- Funding: CryptoFundraising.info, RootData
- Social: Twitter WebSearch, GitHub WebSearch
- Technical: GitHub, Blockscout
- Governance: Snapshot

Rules:
1. Cite every fact with source URL
2. Label exact vs approximate metrics
3. Cross-reference key metrics across sources
4. Flag data conflicts if sources disagree
5. Mark uncertain values with [uncertain]
6. Add uncertain[] array listing all uncertain field names
7. All values in English

Validation: python lib/deep-research/validate_json.py -f fields.yaml -j results/arbitrum.json
Task complete only after validation passes.
```

### Step 4c: Wait and Monitor

- Wait for current batch to complete
- Display progress: "5/13 items complete"
- Note any items with validation issues
- Launch next batch

### Step 4d: Summary

After all items complete:

```
Deep research complete!
- {completed}/{total} items researched
- {uncertain_count} items have uncertain fields (noted in JSON)
- Results: Research/{topic_slug}/results/
```

## Step 5: Generate Report

### Step 5a: Scan Results

Read all JSONs from `Research/{topic_slug}/results/`.

### Step 5b: Ask User

Ask which fields to display in the summary table:

```
Available fields for summary table:
  category, tvl, market_cap, chains, total_raised, twitter_followers, ...

Which fields to include? (default: category, tvl, market_cap, chains, total_raised)
```

### Step 5c: Generate Report

Run `python lib/deep-research/generate_report.py`:

```bash
python lib/deep-research/generate_report.py \
  --topic "{topic}" \
  --fields Research/{topic_slug}/fields.yaml \
  --dir Research/{topic_slug}/results \
  --output Research/{topic_slug}/report.md \
  --summary-fields category tvl market_cap chains total_raised
```

The report includes:
- **Summary table** (multi-item): One row per project with key metrics
- **Table of Contents**: Anchor links to each project section
- **Detailed sections**: One per project, grouped by field category
- **Data quality notes**: Uncertain fields flagged per project
- **Source citations**: Every fact includes source URL

### Step 5d: Display Report Path

```
Report saved: Research/{topic_slug}/report.md

Next:
- /crypto-discovery watchlist add {project} — save for tracking
- /crypto-discovery research continue — re-research uncertain fields
- /crypto-discovery research report — regenerate with different fields
```

## Sub-Command: continue

Resume incomplete research. Skip items that already have valid JSONs.

```
/crypto-discovery research continue
```

1. Find `Research/{topic}/outline.yaml`
2. Scan `results/*.json` for completed items
3. Launch sub-agents only for items without valid JSONs
4. Continue from Step 4

## Sub-Command: report

Regenerate report from existing JSONs (without re-running research).

```
/crypto-discovery research report
```

1. Find `Research/{topic}/outline.yaml`
2. Scan `results/*.json`
3. Ask for summary fields
4. Run `generate_report.py`
5. Save report

## Rules

1. **Factual only** — No hype, no investment advice, no "great opportunity"
2. **Cite everything** — Every fact must have a source URL
3. **Label approximations** — "Followers: ~50K (Twitter WebSearch, approximate)"
4. **Flag conflicts** — If sources disagree, show both values, flag as "Data Conflict"
5. **Note gaps** — If data is missing, say so explicitly
6. **Neutral tone** — Describe what exists, not what could be
7. **Validate** — Every sub-agent must pass validation before completing
8. **Uncertainty** — Mark uncertain fields with `[uncertain]` and list in `uncertain[]` array
9. **Model-agnostic** — Sub-agents use platform's default model, no hardcoding
10. **Resume support** — Skip completed items on continue

## Output Directory Structure

```
Research/
├── uniswap/
│   ├── outline.yaml
│   ├── fields.yaml
│   ├── results/
│   │   └── uniswap.json
│   └── report.md
├── l2-protocols-on-ethereum/
│   ├── outline.yaml
│   ├── fields.yaml
│   ├── results/
│   │   ├── arbitrum.json
│   │   ├── optimism.json
│   │   ├── base.json
│   │   └── ...
│   └── report.md
```