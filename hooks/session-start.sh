#!/bin/bash
# Crypto Discovery — Session Start Hook
# Checks for available resources and reports context

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONFIG="$PLUGIN_DIR/config/sources.yaml"
WATCHLIST="$PLUGIN_DIR/watchlist/watchlist.yaml"

echo "--- Crypto Discovery ---"

# Check for config
if [ ! -f "$CONFIG" ]; then
  echo "No config found. Run /crypto-discovery setup to configure."
  exit 0
fi

# Count enabled sources
ENABLED=$(grep -c "enabled: true" "$CONFIG" 2>/dev/null || echo "0")
echo "Sources enabled: $ENABLED"

# Count API keys
KEYS=$(grep -v "null" "$CONFIG" | grep -c ":" | head -1 || echo "0")
if [ "$KEYS" -gt 0 ]; then
  echo "Premium keys configured: $KEYS"
fi

# Check watchlist
if [ -f "$WATCHLIST" ]; then
  COUNT=$(grep -c "name:" "$WATCHLIST" 2>/dev/null || echo "0")
  if [ "$COUNT" -gt 0 ]; then
    echo "Watchlist: $COUNT projects tracked"
  fi
fi

# Check deep research results
RESEARCH_DIR="$PLUGIN_DIR/Research"
if [ -d "$RESEARCH_DIR" ]; then
  JSON_COUNT=$(find "$RESEARCH_DIR" -name "*.json" -type f 2>/dev/null | wc -l | tr -d ' ')
  REPORT_COUNT=$(find "$RESEARCH_DIR" -name "report.md" -type f 2>/dev/null | wc -l | tr -d ' ')
  if [ "$JSON_COUNT" -gt 0 ]; then
    echo "Deep research: $JSON_COUNT projects researched, $REPORT_COUNT reports"
  fi
fi

echo "---"