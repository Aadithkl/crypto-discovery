#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Crypto Discovery — Deep Research Report Generator
# Reads JSON research results and fields.yaml, generates markdown report

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


CATEGORY_MAPPING = {
    "Overview": ["overview", "Overview"],
    "On-Chain Data": ["on_chain_data", "on-chain data", "On-Chain Data", "onchain_data", "onchain data"],
    "Funding": ["funding", "Funding"],
    "Social": ["social", "Social"],
    "Technical": ["technical", "Technical"],
    "Governance": ["governance", "Governance"],
}

_SKIP_KEYS = {"_source_file", "uncertain"}


def load_fields_yaml(fields_path):
    with fields_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    categories = []
    for category in data.get("field_categories", []):
        cat_name = category["category"]
        fields = []
        for field in category.get("fields", []):
            fields.append({
                "name": field["name"],
                "description": field.get("description", ""),
                "required": field.get("required", False),
            })
        categories.append({"category": cat_name, "fields": fields})
    return categories


def get_field_value(data, field_name, category_mapping=None):
    category_mapping = CATEGORY_MAPPING if category_mapping is None else category_mapping
    if field_name in data:
        return data[field_name]
    if isinstance(data, dict):
        for k, v in data.items():
            if k in _SKIP_KEYS:
                continue
            if isinstance(v, dict):
                result = get_field_value(v, field_name, category_mapping)
                if result is not None:
                    return result
    return None


def is_uncertain(data, field_name):
    if isinstance(data, dict):
        uncertain_list = data.get("uncertain", [])
        if field_name in uncertain_list:
            return True
        value = get_field_value(data, field_name)
        if isinstance(value, str) and "[uncertain]" in value:
            return True
    return False


def should_skip(data, field_name):
    if is_uncertain(data, field_name):
        return True
    value = get_field_value(data, field_name)
    if value is None or value == "" or value == "[not found]":
        return True
    return False


def slugify(text):
    import re
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text


def format_value(value):
    if isinstance(value, list):
        if len(value) == 0:
            return "N/A"
        if isinstance(value[0], dict):
            lines = []
            for item in value:
                parts = [f"{k}: {v}" for k, v in item.items() if k not in _SKIP_KEYS]
                lines.append(" | ".join(parts))
            return "\n" + "\n".join(f"  - {line}" for line in lines)
        if len(value) <= 5:
            return ", ".join(str(v) for v in value)
        return ", ".join(str(v) for v in value[:5]) + f" (+{len(value)-5} more)"
    if isinstance(value, dict):
        parts = [f"{k}: {v}" for k, v in value.items() if k not in _SKIP_KEYS]
        return "; ".join(parts)
    if isinstance(value, str) and len(value) > 150:
        return value[:147] + "..."
    return str(value)


def generate_summary_table(items_data, summary_fields, field_categories):
    lines = []
    lines.append("| # | Project | " + " | ".join(summary_fields) + " |")
    lines.append("|---|---------|" + "|".join(["--------"] * len(summary_fields)) + "|")
    for i, (item_name, data) in enumerate(items_data, 1):
        slug = slugify(item_name)
        values = []
        for field_name in summary_fields:
            val = get_field_value(data, field_name)
            if val is None or val == "" or val == "[not found]":
                values.append("-")
            elif isinstance(val, str) and "[uncertain]" in val:
                values.append(val.replace("[uncertain]", "").strip() + " ⚠")
            else:
                formatted = format_value(val)
                if len(formatted) > 40:
                    formatted = formatted[:37] + "..."
                values.append(formatted)
        lines.append(f"| {i} | [{item_name}](#{slug}) | " + " | ".join(values) + " |")
    return "\n".join(lines)


def generate_item_section(item_name, data, field_categories):
    lines = []
    slug = slugify(item_name)
    lines.append(f"## {item_name}")
    lines.append("")

    if isinstance(data, dict) and "uncertain" in data:
        uncertain_fields = data["uncertain"]
        if uncertain_fields:
            lines.append(f"⚠ **Uncertain fields:** {', '.join(uncertain_fields)}")
            lines.append("")

    for category_info in field_categories:
        cat_name = category_info["category"]
        cat_fields = category_info["fields"]
        values_in_category = []

        for field_info in cat_fields:
            field_name = field_info["name"]
            if should_skip(data, field_name):
                continue
            value = get_field_value(data, field_name)
            if value is None or value == "" or value == "[not found]":
                continue
            values_in_category.append((field_name, value))

        if not values_in_category:
            continue

        lines.append(f"### {cat_name}")
        lines.append("")
        lines.append("| Field | Value |")
        lines.append("|-------|-------|")
        for field_name, value in values_in_category:
            formatted = format_value(value)
            if isinstance(value, str) and "[uncertain]" in value:
                formatted = formatted.replace("[uncertain]", "").strip() + " ⚠"
            lines.append(f"| {field_name} | {formatted} |")
        lines.append("")

    extra_fields = []
    if isinstance(data, dict):
        defined_names = set()
        for cat_info in field_categories:
            for f in cat_info["fields"]:
                defined_names.add(f["name"])
        for k, v in data.items():
            if k in _SKIP_KEYS:
                continue
            if k in defined_names:
                continue
            nested_keys = {nk for keys in CATEGORY_MAPPING.values() for nk in keys}
            if k in nested_keys and isinstance(v, dict):
                for nk, nv in v.items():
                    if nk not in defined_names and nk not in _SKIP_KEYS:
                        extra_fields.append((nk, nv))
            elif k not in nested_keys:
                extra_fields.append((k, v))

    if extra_fields:
        lines.append("### Additional Information")
        lines.append("")
        lines.append("| Field | Value |")
        lines.append("|-------|-------|")
        for field_name, value in extra_fields:
            formatted = format_value(value)
            lines.append(f"| {field_name} | {formatted} |")
        lines.append("")

    return "\n".join(lines)


def generate_report(topic, items_data, field_categories, summary_fields):
    lines = []
    date_str = datetime.now().strftime("%Y-%m-%d")
    items_count = len(items_data)
    items_with_uncertain = sum(1 for _, data in items_data if isinstance(data, dict) and data.get("uncertain"))

    lines.append(f"# {topic} — Crypto Research Report")
    lines.append("")
    lines.append(f"**Date:** {date_str}  ")
    lines.append(f"**Projects:** {items_count}  ")
    lines.append(f"**Data Quality:** {items_count - items_with_uncertain} complete, {items_with_uncertain} with uncertain fields  ")
    lines.append(f"**Generated by:** Crypto Discovery Deep Research")
    lines.append("")
    lines.append("---")
    lines.append("")

    if items_count > 1 and summary_fields:
        lines.append("## Summary Table")
        lines.append("")
        lines.append(generate_summary_table(items_data, summary_fields, field_categories))
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("## Table of Contents")
    lines.append("")
    for i, (item_name, data) in enumerate(items_data, 1):
        slug = slugify(item_name)
        lines.append(f"{i}. [{item_name}](#{slug})")
    lines.append("")
    lines.append("---")
    lines.append("")

    for item_name, data in items_data:
        lines.append(generate_item_section(item_name, data, field_categories))
        lines.append("---")
        lines.append("")

    lines.append("## Data Quality Notes")
    lines.append("")
    for item_name, data in items_data:
        if isinstance(data, dict) and data.get("uncertain"):
            fields = ", ".join(data["uncertain"])
            lines.append(f"- **{item_name}:** Uncertain fields — {fields}")
    if not any(isinstance(data, dict) and data.get("uncertain") for _, data in items_data):
        lines.append("All projects have complete data with no uncertain fields.")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*Generated by Crypto Discovery Deep Research*  ")
    lines.append("*Neutral, factual research. Not investment advice.*")

    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate crypto research report from JSON results")
    parser.add_argument("--topic", "-t", type=str, help="Research topic (used for title)")
    parser.add_argument("--fields", "-f", type=str, help="Path to fields.yaml", default="fields.yaml")
    parser.add_argument("--dir", "-d", type=str, help="Directory containing JSON files", default="results")
    parser.add_argument("--output", "-o", type=str, help="Output markdown file path", default="report.md")
    parser.add_argument("--summary-fields", "-s", type=str, nargs="*", help="Fields to include in summary table")
    args = parser.parse_args()

    fields_path = Path(args.fields)
    if not fields_path.exists():
        for p in (Path.cwd() / "fields.yaml", Path.cwd().parent / "fields.yaml"):
            if p.exists():
                fields_path = p
                break
    if not fields_path.exists():
        print(f"[ERROR] fields.yaml not found: {fields_path}")
        sys.exit(1)

    field_categories = load_fields_yaml(fields_path)
    all_field_names = []
    for cat in field_categories:
        for f in cat["fields"]:
            all_field_names.append(f["name"])

    json_dir = Path(args.dir)
    if not json_dir.exists():
        print(f"[ERROR] Results directory not found: {json_dir}")
        sys.exit(1)

    json_files = sorted(json_dir.glob("*.json"))
    if not json_files:
        print("[ERROR] No JSON files found in results directory")
        sys.exit(1)

    items_data = []
    for json_file in json_files:
        try:
            with json_file.open(encoding="utf-8") as f:
                data = json.load(f)
            name = data.get("name", json_file.stem)
            if isinstance(data, dict):
                for cat_key in ["Overview", "overview"]:
                    if cat_key in data and isinstance(data[cat_key], dict):
                        if "name" in data[cat_key]:
                            name = data[cat_key]["name"]
                            break
                flat_name = data.get("name")
                if flat_name:
                    name = flat_name
            items_data.append((name, data))
        except Exception as e:
            print(f"[WARN] Failed to load {json_file}: {e}")

    if not items_data:
        print("[ERROR] No valid JSON data found")
        sys.exit(1)

    topic = args.topic
    if not topic:
        topic = items_data[0][0] if len(items_data) == 1 else "Crypto Research Report"

    summary_fields = args.summary_fields
    if not summary_fields:
        default_summary = ["category", "tvl", "market_cap", "chains", "total_raised"]
        available = [f for f in default_summary if f in all_field_names]
        summary_fields = available

    report = generate_report(topic, items_data, field_categories, summary_fields)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        f.write(report)

    print(f"Report generated: {output_path}")
    print(f"Projects: {len(items_data)}")
    print(f"Summary fields: {', '.join(summary_fields)}")


if __name__ == "__main__":
    main()