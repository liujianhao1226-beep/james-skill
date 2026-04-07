#!/usr/bin/env python3
"""Export a normalized smart-hardware scope tree to a .xmind archive."""

from __future__ import annotations

import argparse
import json
import uuid
import zipfile
from pathlib import Path
from typing import Any, Dict

from scope_tree_lib import ScopeTreeError, load_tree_from_path, prepare_tree


def new_id() -> str:
    return str(uuid.uuid4())


def _build_notes_plain(node: Dict[str, Any]) -> str:
    """Build a plain-text notes string from node metadata fields."""
    parts = []
    if node.get("note"):
        parts.append(str(node["note"]))
    meta_fields = [
        ("priority", "优先级"),
        ("test_type", "测试类型"),
        ("automation_hint", "自动化建议"),
        ("confidence", "置信度"),
        ("risk_score", "风险分"),
    ]
    for key, label in meta_fields:
        val = node.get(key)
        if val is not None and val != "" and val != []:
            if isinstance(val, list):
                val = ", ".join(str(v) for v in val)
            parts.append(f"{label}: {val}")
    refs = node.get("source_refs")
    if refs:
        if isinstance(refs, list):
            refs = ", ".join(str(r) for r in refs)
        parts.append(f"依据: {refs}")
    return "\n".join(parts)


def topic_to_xmind(node: Dict[str, Any], is_root: bool = False) -> Dict[str, Any]:
    topic: Dict[str, Any] = {
        "id": new_id(),
        "class": "topic",
        "title": node["title"],
    }
    if is_root:
        topic["structureClass"] = "org.xmind.ui.logic.right"
    # Embed metadata as XMind notes so they're visible when opened
    notes_text = _build_notes_plain(node)
    if notes_text:
        topic["notes"] = {"plain": {"content": notes_text}}
    children = node.get("children", [])
    if children:
        topic["children"] = {"attached": [topic_to_xmind(child, is_root=False) for child in children]}
    return topic


def build_sheet(wrapper: Dict[str, Any], sheet_title: str | None = None) -> Dict[str, Any]:
    title = sheet_title or wrapper["title"]
    return {
        "id": new_id(),
        "class": "sheet",
        "title": title,
        "rootTopic": topic_to_xmind(wrapper["root"], is_root=True),
    }


def write_xmind(wrapper: Dict[str, Any], output: Path, sheet_title: str | None = None) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    content = [build_sheet(wrapper, sheet_title=sheet_title)]
    metadata = {
        "dataStructureVersion": "2",
        "creator": {"name": "ChatGPT", "version": "1.0"},
        "layoutEngineVersion": "3",
    }
    manifest = {
        "file-entries": {
            "content.json": {},
            "metadata.json": {},
        }
    }
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("content.json", json.dumps(content, ensure_ascii=False, indent=2))
        zf.writestr("metadata.json", json.dumps(metadata, ensure_ascii=False))
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a normalized scope tree to .xmind")
    parser.add_argument("input", type=Path, help="path to markdown or json input")
    parser.add_argument("output", type=Path, help="path to output .xmind file")
    parser.add_argument("--input-format", choices=("auto", "markdown", "json"), default="auto")
    parser.add_argument("--title", help="override tree title")
    parser.add_argument("--sheet-title", help="override XMind sheet title")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.input.exists():
        raise SystemExit(f"error: file not found: {args.input}")
    try:
        wrapper = load_tree_from_path(args.input, input_format=args.input_format, title_hint=args.title)
        normalized = prepare_tree(wrapper)
        write_xmind(normalized, args.output, sheet_title=args.sheet_title)
        if normalized.get("warnings"):
            for item in normalized["warnings"]:
                print(f"warning: {item}")
    except ScopeTreeError as exc:
        raise SystemExit(f"error: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
