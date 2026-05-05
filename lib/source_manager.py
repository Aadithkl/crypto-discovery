# Source Manager
# Handles loading, querying, and merging all data sources for crypto discovery

from typing import Dict, List, Any, Optional, Set, Tuple
import asyncio
import re
import time
import json
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SourceResult:
    """Result from a single source query"""
    source: str
    data: List[Dict[str, Any]]
    filters_matched: List[str]
    is_approximate: bool = False
    fallback_used: Optional[str] = None


@dataclass
class MergedResult:
    """Final merged result across multiple sources"""
    name: str
    category: Optional[str] = None
    chain: Optional[str] = None
    tvl: Optional[float] = None
    market_cap: Optional[float] = None
    token: Optional[str] = None
    funding_raised: Optional[float] = None
    sources: List[str] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    match_score: float = 0.0
    is_approximate: bool = False


class RateLimiter:
    """Rate limiter for API/web requests"""

    def __init__(self, config: Dict):
        self.delays = config.get("rate_limiting", {}).get("delays", {
            "api": 500,
            "websearch": 1000,
            "browser": 2000,
            "custom": 0
        })
        self.last_request: Dict[str, float] = {}

    async def wait(self, source_type: str):
        """Wait if necessary to respect rate limits"""
        delay_ms = self.delays.get(source_type, 1000)
        last = self.last_request.get(source_type, 0)
        elapsed = (time.time() - last) * 1000
        if elapsed < delay_ms:
            await asyncio.sleep((delay_ms - elapsed) / 1000)
        self.last_request[source_type] = time.time()


class QueryInterpreter:
    """Interprets natural language into source queries"""

    # Source keyword mappings
    SOURCE_KEYWORDS = {
        "defillama": ["defillama", "tvl", "protocol", "yield", "defi"],
        "coingecko": ["coingecko", "token", "market cap", "price", "coin"],
        "coinmarketcap": ["coinmarketcap", "cmc", "ranking"],
        "debank": ["debank", "portfolio", "holders", "on-chain"],
        "flipside": ["flipside", "query", "analytics"],
        "blockscout": ["blockscout", "contract", "transaction", "verified"],
        "snapshot": ["snapshot", "governance", "proposal", "vote"],
        "github": ["github", "code", "repo", "commit", "developer"],
        "crypto_fundraising": ["fundraising", "raised", "investors", "deal"],
        "rootdata": ["rootdata", "project", "fundraising", "raised"],
        "rootdata": ["rootdata", "project"],
        "crunchbase": ["crunchbase", "funding", "series"],
        "twitter": ["twitter", "x.com", "followers", "social"],
        "the_block": ["the block", "news"],
        "coindesk": ["coindesk"],
        "cointelegraph": ["cointelegraph"],
        "dune": ["dune"],
        "token_terminal": ["token terminal", "fundamentals"],
        "messari": ["messari", "research"],
        "arkham": ["arkham", "whale", "entity"],
        "agentcash": ["agentcash", "exact"],
        "lunarcrush": ["lunarcrush", "sentiment"],
        "nansen": ["nansen", "smart money"],
        "alchemy": ["alchemy", "rpc", "trace"],
        "custom": ["my", "excel", "sheet", "custom"]
    }

    # Chain keywords
    CHAINS = [
        "ethereum", "arbitrum", "optimism", "base", "solana",
        "avalanche", "polygon", "bsc", "avax", "fantom",
        "celo", "moonbeam", "gnosis", "cronos"
    ]

    # Category keywords
    CATEGORIES = [
        "defi", "lending", "dex", "nft", "gaming", "infrastructure",
        "yield", "derivatives", "stablecoin", "bridge", "oracle",
        "dao", "privacy", "identity", "payments", "insurance",
        "liquid staking", "restaking", "perpetual", "options"
    ]

    # Stage keywords
    STAGES = ["seed", "series a", "series b", "series c", "pre-seed", "ico", "ido"]

    def __init__(self):
        pass

    def parse_input(self, user_input: str) -> Dict[str, Any]:
        """Parse natural language input into source and filters"""
        input_lower = user_input.lower()

        # Find source
        source = self._find_source(input_lower)

        # Extract filters
        filters = self._extract_filters(input_lower)

        return {
            "source": source,
            "filters": filters,
            "original_input": user_input,
            "inferred": source is None  # Whether source was inferred
        }

    def _find_source(self, text: str) -> Optional[str]:
        """Find primary source from input"""
        scores: Dict[str, int] = {}
        for source, keywords in self.SOURCE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[source] = score

        if scores:
            return max(scores, key=scores.get)
        return None

    def _extract_filters(self, text: str) -> Dict[str, Any]:
        """Extract filter values from text"""
        filters = {}

        # TVL filters
        tvl_patterns = [
            (r"over\s+(\d+\.?\d*)\s*([mkMbB]?)\s*tvl", "tvl_min"),
            (r"under\s+(\d+\.?\d*)\s*([mkMbB]?)\s*tvl", "tvl_max"),
            (r"tvl\s*[:\s>]+\s*(\d+\.?\d*)\s*([mkMbB]?)", "tvl_min"),
            (r"tvl\s*[:\s<]+\s*(\d+\.?\d*)\s*([mkMbB]?)", "tvl_max"),
            (r"(\d+\.?\d*)\s*([mkMbB]?)\s*-\s*(\d+\.?\d*)\s*([mkMbB]?)\s*tvl", "tvl_range"),
        ]

        for pattern, key in tvl_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if key == "tvl_range":
                    min_val = self._parse_number(match.group(1), match.group(2))
                    max_val = self._parse_number(match.group(3), match.group(4))
                    filters["tvl_min"] = min_val
                    filters["tvl_max"] = max_val
                else:
                    val = self._parse_number(match.group(1), match.group(2))
                    filters[key] = val
                break

        # Market cap filters
        mcap_patterns = [
            (r"market cap\s*[:\s>]+\s*(\d+\.?\d*)\s*([mkMbB]?)", "mcap_min"),
            (r"market cap\s*[:\s<]+\s*(\d+\.?\d*)\s*([mkMbB]?)", "mcap_max"),
            (r"cap\s*[:\s>]+\s*(\d+\.?\d*)\s*([mkMbB]?)", "mcap_min"),
        ]

        for pattern, key in mcap_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                val = self._parse_number(match.group(1), match.group(2))
                filters[key] = val
                break

        # Chain filter
        for chain in self.CHAINS:
            if chain in text.lower():
                filters["chain"] = chain
                break

        # Category filter
        for cat in self.CATEGORIES:
            if cat in text.lower():
                filters["category"] = cat
                break

        # Stage filter
        for stage in self.STAGES:
            if stage in text.lower():
                filters["stage"] = stage
                break

        # Follower filters
        follower_patterns = [
            (r"followers\s*[:\s>]+\s*(\d+\.?\d*)\s*([kKmM]?)", "followers_min"),
            (r"followers\s*[:\s<]+\s*(\d+\.?\d*)\s*([kKmM]?)", "followers_max"),
            (r"(\d+\.?\d*)\s*([kKmM]?)\s*-\s*(\d+\.?\d*)\s*([kKmM]?)\s*followers", "followers_range"),
        ]

        for pattern, key in follower_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if key == "followers_range":
                    min_val = self._parse_number(match.group(1), match.group(2))
                    max_val = self._parse_number(match.group(3), match.group(4))
                    filters["followers_min"] = min_val
                    filters["followers_max"] = max_val
                else:
                    val = self._parse_number(match.group(1), match.group(2))
                    filters[key] = val
                break

        return filters

    def _parse_number(self, num_str: str, suffix: str) -> float:
        """Parse number with k/m/b suffix"""
        num = float(num_str)
        suffix = suffix.lower()
        if suffix == "k":
            return num * 1000
        elif suffix == "m":
            return num * 1000000
        elif suffix == "b":
            return num * 1000000000
        return num


class SourceManager:
    """Manages all data sources for crypto discovery"""

    # Source type mappings
    SOURCE_TYPES = {
        "defillama": "api",
        "coingecko": "api",
        "coinmarketcap": "api",
        "debank": "api",
        "flipside": "api",
        "blockscout": "api",
        "snapshot": "api",
        "dune": "api",
        "token_terminal": "api",
        "messari": "api",
        "arkham": "api",
        "agentcash": "api",
        "lunarcrush": "api",
        "nansen": "api",
        "alchemy": "api",
        "github": "websearch",
        "twitter": "websearch",
        "crypto_fundraising": "browser",
        "rootdata": "browser",
        "crunchbase": "browser",
        "the_block": "browser",
        "coindesk": "browser",
        "cointelegraph": "browser",
        "custom": "custom"
    }

    # Premium sources that need API keys
    PREMIUM_SOURCES = {
        "dune", "token_terminal", "messari", "arkham",
        "agentcash", "lunarcrush", "nansen", "alchemy"
    }

    # Free fallbacks for premium sources
    FALLBACKS = {
        "dune": "flipside",
        "token_terminal": "defillama",
        "messari": "the_block",
        "arkham": "debank",
        "agentcash": "twitter",
        "lunarcrush": None,  # No good free fallback
        "nansen": "arkham",
        "alchemy": "blockscout"
    }

    def __init__(self, config: Dict):
        self.config = config
        self.sources = config.get("sources", {})
        self.api_keys = config.get("api_keys", {})
        self.custom_sources = config.get("custom_sources", [])
        self.rate_limiter = RateLimiter(config)
        self.query_interpreter = QueryInterpreter()

    def get_enabled_sources(self) -> List[str]:
        """Return list of enabled source names"""
        enabled = []
        for name, settings in self.sources.items():
            if settings.get("enabled", False):
                # Check if premium source has API key
                if name in self.PREMIUM_SOURCES:
                    if self.api_keys.get(name):
                        enabled.append(name)
                else:
                    enabled.append(name)
        return enabled

    def is_source_enabled(self, source_name: str) -> bool:
        """Check if a specific source is enabled and available"""
        settings = self.sources.get(source_name, {})
        if not settings.get("enabled", False):
            return False
        if source_name in self.PREMIUM_SOURCES:
            return bool(self.api_keys.get(source_name))
        return True

    def get_source_type(self, source_name: str) -> str:
        """Get the type for a source"""
        return self.SOURCE_TYPES.get(source_name, "custom")

    def get_fallback(self, source_name: str) -> Optional[str]:
        """Get fallback source for a premium source"""
        return self.FALLBACKS.get(source_name)

    def discover(self, query: str) -> List[MergedResult]:
        """Main discovery method"""
        # Parse query
        parsed = self.query_interpreter.parse_input(query)
        source = parsed["source"]
        filters = parsed["filters"]

        # Determine which sources to query
        sources_to_query = []
        if source and self.is_source_enabled(source):
            sources_to_query.append(source)
        elif source and source in self.PREMIUM_SOURCES:
            # Try fallback
            fallback = self.get_fallback(source)
            if fallback and self.is_source_enabled(fallback):
                sources_to_query.append(fallback)
        else:
            # Query all enabled sources that match filters
            for s in self.get_enabled_sources():
                sources_to_query.append(s)

        # Execute queries
        results_by_source: Dict[str, SourceResult] = {}
        for s in sources_to_query:
            result = self._query_source(s, filters)
            if result:
                results_by_source[s] = result

        # Merge results
        merged = self._merge_results(results_by_source, filters)

        return merged

    def _query_source(self, source_name: str, filters: Dict) -> Optional[SourceResult]:
        """Query a single source"""
        if not self.is_source_enabled(source_name):
            return None

        source_type = self.get_source_type(source_name)
        asyncio.run(self.rate_limiter.wait(source_type))

        # Build query parameters
        params = self._build_query_params(source_name, filters)

        # Return query instruction for AI agent
        return SourceResult(
            source=source_name,
            data=[params],  # AI will execute this
            filters_matched=list(filters.keys()),
            is_approximate=source_name in self.PREMIUM_SOURCES and not self.is_source_enabled(source_name)
        )

    def _build_query_params(self, source: str, filters: Dict) -> Dict[str, Any]:
        """Build query parameters for a source"""
        params = {
            "source": source,
            "type": self.get_source_type(source),
            "filters": filters
        }

        # Add source-specific instructions
        if source == "defillama":
            params["url"] = "https://api.llama.fi/protocols"
            params["method"] = "GET"
            params["instructions"] = self._build_defillama_instructions(filters)

        elif source == "coingecko":
            params["url"] = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
            params["method"] = "GET"
            params["instructions"] = self._build_coingecko_instructions(filters)

        elif source == "blockscout":
            params["instructions"] = self._build_blockscout_instructions(filters)

        elif source == "flipside":
            params["instructions"] = self._build_flipside_instructions(filters)

        elif source == "twitter":
            params["instructions"] = self._build_twitter_instructions(filters)

        elif source == "github":
            params["url"] = "https://api.github.com/search/repositories"
            params["method"] = "GET"
            params["instructions"] = self._build_github_instructions(filters)

        elif source in ["crypto_fundraising", "rootdata", "crunchbase"]:
            params["instructions"] = self._build_browser_instructions(source, filters)

        return params

    def _build_defillama_instructions(self, filters: Dict) -> str:
        """Build DeFiLlama query instructions"""
        instructions = """
        1. Use WebFetch to get: https://api.llama.fi/protocols
        2. Parse JSON response
        3. Filter protocols where:
        """
        conditions = []
        if "tvl_min" in filters:
            conditions.append(f"   - tvl >= ${filters['tvl_min']:,.0f}")
        if "tvl_max" in filters:
            conditions.append(f"   - tvl <= ${filters['tvl_max']:,.0f}")
        if "chain" in filters:
            conditions.append(f"   - chain contains '{filters['chain']}'")
        if "category" in filters:
            conditions.append(f"   - category contains '{filters['category']}'")

        if not conditions:
            conditions.append("   - Return top 50 by TVL")

        instructions += "\n".join(conditions)
        instructions += """
        4. Return for each match:
           - name
           - tvl
           - chain
           - category
           - url
           - twitter
           - change_1d
           - change_7d
        """
        return instructions

    def _build_coingecko_instructions(self, filters: Dict) -> str:
        """Build CoinGecko query instructions"""
        instructions = """
        1. Use WebFetch to get: https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc
        2. Parse JSON response
        3. Filter tokens where:
        """
        conditions = []
        if "mcap_min" in filters:
            conditions.append(f"   - market_cap >= ${filters['mcap_min']:,.0f}")
        if "mcap_max" in filters:
            conditions.append(f"   - market_cap <= ${filters['mcap_max']:,.0f}")
        if "category" in filters:
            conditions.append(f"   - name/symbol related to '{filters['category']}'")

        if not conditions:
            conditions.append("   - Return top 50 by market cap")

        instructions += "\n".join(conditions)
        instructions += """
        4. Return for each match:
           - name
           - symbol
           - market_cap
           - current_price
           - total_volume
           - price_change_24h
        """
        return instructions

    def _build_blockscout_instructions(self, filters: Dict) -> str:
        """Build Blockscout query instructions"""
        chain = filters.get("chain", "ethereum")
        instructions = f"""
        1. Use WebFetch to get: https://{chain}.blockscout.com/api/v2/main-page/transactions
        2. Or search for verified contracts: https://{chain}.blockscout.com/api/v2/smart-contracts
        3. Parse JSON response
        4. Return:
           - transaction counts
           - verified contracts
           - active addresses
        """
        return instructions

    def _build_flipside_instructions(self, filters: Dict) -> str:
        """Build Flipside Crypto query instructions"""
        instructions = """
        1. Use WebFetch to query Flipside Crypto API
        2. Or use their SQL API with a query like:
           SELECT * FROM ethereum.core.fact_transactions LIMIT 100
        3. Parse JSON response
        4. Return query results
        """
        return instructions

    def _build_twitter_instructions(self, filters: Dict) -> str:
        """Build Twitter query instructions"""
        instructions = """
        1. Use WebSearch to find: "site:twitter.com {project} followers"
        2. Or search: "{project} twitter followers"
        3. Parse search results for:
           - follower counts (approximate)
           - account activity
           - recent tweets
        4. Label all metrics as "approximate" (WebSearch)
        """
        if "followers_min" in filters or "followers_max" in filters:
            instructions += f"""
        5. Filter accounts where:
           - followers {'>=' + str(filters.get('followers_min')) if 'followers_min' in filters else ''} 
           {'<=' + str(filters.get('followers_max')) if 'followers_max' in filters else ''}
        """
        return instructions

    def _build_github_instructions(self, filters: Dict) -> str:
        """Build GitHub query instructions"""
        instructions = """
        1. Use WebFetch to search: https://api.github.com/search/repositories?q={keyword}&sort=stars&order=desc
        2. Parse JSON response
        3. Return for each repo:
           - name
           - full_name
           - stars
           - language
           - last_push
           - description
        """
        return instructions

    def _build_browser_instructions(self, source: str, filters: Dict) -> str:
        """Build browser scraping instructions"""
        site_map = {
            "crypto_fundraising": "https://crypto-fundraising.info",
            "rootdata": "https://www.rootdata.com",
            "crunchbase": "https://www.crunchbase.com"
        }
        base_url = site_map.get(source, "")

        instructions = f"""
        1. Use WebFetch or Playwright MCP to navigate to: {base_url}
        2. Search for projects matching filters:
        """
        conditions = []
        if "stage" in filters:
            conditions.append(f"   - Stage: {filters['stage']}")
        if "category" in filters:
            conditions.append(f"   - Category: {filters['category']}")

        if not conditions:
            conditions.append("   - Return recent projects/deals")

        instructions += "\n".join(conditions)
        instructions += f"""
        3. Extract from {source}:
           - project name
           - funding rounds
           - amounts
           - investors
           - dates
        4. Return structured data
        """
        return instructions

    def _merge_results(self, results_by_source: Dict[str, SourceResult], filters: Dict) -> List[MergedResult]:
        """Merge results from multiple sources"""
        # Group by project name
        by_name: Dict[str, Dict[str, Any]] = {}

        for source, result in results_by_source.items():
            for item in result.data:
                name = item.get("name", "Unknown")
                if name not in by_name:
                    by_name[name] = {
                        "sources": [],
                        "raw": {},
                        "tvl": None,
                        "market_cap": None,
                        "category": None,
                        "chain": None
                    }
                by_name[name]["sources"].append(source)
                by_name[name]["raw"][source] = item

                # Extract common fields
                if "tvl" in item and by_name[name]["tvl"] is None:
                    by_name[name]["tvl"] = item["tvl"]
                if "market_cap" in item and by_name[name]["market_cap"] is None:
                    by_name[name]["market_cap"] = item["market_cap"]
                if "category" in item and by_name[name]["category"] is None:
                    by_name[name]["category"] = item["category"]
                if "chain" in item and by_name[name]["chain"] is None:
                    by_name[name]["chain"] = item["chain"]

        # Convert to MergedResult
        merged = []
        for name, data in by_name.items():
            # Calculate match score
            score = 0
            matched = []
            for filter_name, filter_value in filters.items():
                if filter_name == "tvl_min" and data.get("tvl") and data["tvl"] >= filter_value:
                    score += 1
                    matched.append("tvl_min")
                elif filter_name == "tvl_max" and data.get("tvl") and data["tvl"] <= filter_value:
                    score += 1
                    matched.append("tvl_max")
                elif filter_name == "category" and data.get("category") and filter_value.lower() in data["category"].lower():
                    score += 1
                    matched.append("category")
                elif filter_name == "chain" and data.get("chain") and filter_value.lower() in data["chain"].lower():
                    score += 1
                    matched.append("chain")

            merged.append(MergedResult(
                name=name,
                category=data.get("category"),
                chain=data.get("chain"),
                tvl=data.get("tvl"),
                market_cap=data.get("market_cap"),
                sources=data["sources"],
                raw_data=data["raw"],
                match_score=score
            ))

        # Sort by match score
        merged.sort(key=lambda x: x.match_score, reverse=True)
        return merged


class WatchlistManager:
    """Manages watchlist of tracked projects"""

    def __init__(self, watchlist_path: Path = None):
        self.watchlist_path = watchlist_path or Path("watchlist/watchlist.yaml")
        self.watchlist = self._load()

    def _load(self) -> Dict:
        """Load watchlist from file"""
        if self.watchlist_path.exists():
            try:
                import yaml
                return yaml.safe_load(self.watchlist_path.read_text()) or {"projects": []}
            except Exception:
                return {"projects": []}
        return {"projects": []}

    def save(self):
        """Save watchlist to file"""
        try:
            import yaml
            self.watchlist_path.write_text(yaml.dump(self.watchlist, default_flow_style=False))
        except Exception as e:
            print(f"Error saving watchlist: {e}")

    def add(self, name: str, tags: List[str] = None, notes: str = "", source: str = ""):
        """Add a project to watchlist"""
        # Check if already exists
        for p in self.watchlist["projects"]:
            if p["name"].lower() == name.lower():
                return False, f"{name} is already in watchlist"

        project = {
            "name": name,
            "added": datetime.now().isoformat(),
            "tags": tags or [],
            "notes": notes,
            "discovered_via": source
        }
        self.watchlist["projects"].append(project)
        self.save()
        return True, f"Added {name} to watchlist"

    def remove(self, name: str):
        """Remove a project from watchlist"""
        original_len = len(self.watchlist["projects"])
        self.watchlist["projects"] = [
            p for p in self.watchlist["projects"]
            if p["name"].lower() != name.lower()
        ]
        if len(self.watchlist["projects"]) < original_len:
            self.save()
            return True, f"Removed {name} from watchlist"
        return False, f"{name} not found in watchlist"

    def list(self, tag: str = None) -> List[Dict]:
        """List watchlist projects, optionally filtered by tag"""
        projects = self.watchlist["projects"]
        if tag:
            projects = [p for p in projects if tag.lower() in [t.lower() for t in p.get("tags", [])]]
        return projects

    def get(self, name: str) -> Optional[Dict]:
        """Get a specific project from watchlist"""
        for p in self.watchlist["projects"]:
            if p["name"].lower() == name.lower():
                return p
        return None

    def get_tags(self) -> Dict[str, int]:
        """Get all tags with counts"""
        tags: Dict[str, int] = {}
        for p in self.watchlist["projects"]:
            for t in p.get("tags", []):
                tags[t] = tags.get(t, 0) + 1
        return tags


class ConfigLoader:
    """Loads and validates configuration"""

    @staticmethod
    def load(config_path: Path = None) -> Dict:
        """Load configuration from file"""
        config_path = config_path or Path("config/sources.yaml")

        if not config_path.exists():
            # Try example config
            example_path = Path("config/sources.example.yaml")
            if example_path.exists():
                try:
                    import yaml
                    return yaml.safe_load(example_path.read_text())
                except Exception:
                    pass
            return ConfigLoader._default_config()

        try:
            import yaml
            return yaml.safe_load(config_path.read_text())
        except Exception as e:
            print(f"Error loading config: {e}")
            return ConfigLoader._default_config()

    @staticmethod
    def _default_config() -> Dict:
        """Return default configuration"""
        return {
            "sources": {
                "defillama": {"enabled": True, "type": "api"},
                "coingecko": {"enabled": True, "type": "api"},
                "debank": {"enabled": True, "type": "api"},
                "flipside": {"enabled": True, "type": "api"},
                "blockscout": {"enabled": True, "type": "api"},
                "snapshot": {"enabled": True, "type": "api"},
                "github": {"enabled": True, "type": "websearch"},
                "crypto_fundraising": {"enabled": True, "type": "browser"},
                "rootdata": {"enabled": True, "type": "browser"},
                "twitter": {"enabled": True, "type": "websearch"},
                "the_block": {"enabled": True, "type": "browser"},
                "coindesk": {"enabled": True, "type": "browser"},
                "cointelegraph": {"enabled": True, "type": "browser"},
            },
            "api_keys": {},
            "custom_sources": [],
            "rate_limiting": {
                "enabled": True,
                "default_delay_ms": 2000,
                "delays": {"api": 500, "websearch": 1000, "browser": 2000, "custom": 0}
            },
            "discovery": {
                "default_limit": 10,
                "max_results": 50,
                "show_filters": True,
                "prompt_research": True,
                "show_source_labels": True,
                "show_data_quality": True
            }
        }


# Convenience function for direct usage
def create_source_manager(config_path: Path = None) -> SourceManager:
    """Create a SourceManager from config file"""
    config = ConfigLoader.load(config_path)
    return SourceManager(config)
