#!/usr/bin/env python3
"""Normalize and validate a smart-hardware scope tree from markdown or json."""

from __future__ import annotations

import argparse
from pathlib import Path

from scope_tree_lib import ScopeTreeError, load_tree_from_path, prepare_tree, save_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize and validate a smart-hardware scope tree")
    parser.add_argument("input", type=Path, help="path to markdown or json input")
    parser.add_argument("--input-format", choices=("auto", "markdown", "json"), default="auto")
    parser.add_argument("--title", help="override tree title")
    parser.add_argument("--output", type=Path, help="write normalized json to this path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.input.exists():
        raise SystemExit(f"error: file not found: {args.input}")
    try:
        wrapper = load_tree_from_path(args.input, input_format=args.input_format, title_hint=args.title)
        normalized = prepare_tree(wrapper)
        save_json(normalized, args.output)
    except ScopeTreeError as exc:
        raise SystemExit(f"error: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
