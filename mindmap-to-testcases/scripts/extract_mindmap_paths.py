#!/usr/bin/env python3
"""Extract normalized root-to-leaf paths from XMind, FreeMind .mm, outline text, or CSV sources.

Usage:
  python scripts/extract_mindmap_paths.py input.xmind output.json
  python scripts/extract_mindmap_paths.py input.mm output.json
  python scripts/extract_mindmap_paths.py input.md output.json
  python scripts/extract_mindmap_paths.py input.csv output.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from mindmap_io import MindmapParseError, parse_source


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract root-to-leaf paths from a mind map source")
    parser.add_argument("input", type=Path, help="Path to .xmind, .mm, .md, .txt, or .csv source")
    parser.add_argument("output", type=Path, help="Path to output JSON file")
    parser.add_argument(
        "--format",
        choices=("auto", "xmind", "freemind", "mm", "outline", "markdown", "text", "csv", "image"),
        default="auto",
        help="Override input format detection",
    )
    parser.add_argument(
        "--strip-root",
        action="store_true",
        default=False,
        help="Remove the root node (document title) from every path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.input.exists():
        print(f"error: file not found: {args.input}", file=sys.stderr)
        return 1

    try:
        payload = parse_source(args.input, input_format=args.format, strip_root=args.strip_root)
    except MindmapParseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    total = sum(group.get("path_count", 0) for group in payload.get("groups", []))
    stats = payload.get("stats", {})
    annotations = stats.get("annotation_paths", 0)
    depth_info = stats.get("depth_distribution", {})
    print(f"Extracted {total} path(s) from {args.input} -> {args.output}")
    if annotations:
        print(f"  ({annotations} annotation path(s) tagged)")
    if depth_info:
        print(f"  Depth distribution: {depth_info}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
