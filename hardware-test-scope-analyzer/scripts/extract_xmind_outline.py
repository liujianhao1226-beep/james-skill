#!/usr/bin/env python3
"""Extract a readable outline from a .xmind file.

Supports common XMind zip packages that contain content.json. Falls back to
workbook-like json structures when present.
"""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence


def load_xmind_json(zf: zipfile.ZipFile) -> List[Dict[str, Any]]:
    names = set(zf.namelist())

    if "content.json" in names:
        data = json.loads(zf.read("content.json"))
        sheets = normalize_sheet_container(data)
        if sheets:
            return sheets

    if "workbook.json" in names:
        data = json.loads(zf.read("workbook.json"))
        sheets = normalize_sheet_container(data)
        if sheets:
            return sheets

    return []


def normalize_sheet_container(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]

    if not isinstance(data, dict):
        return []

    if "rootTopic" in data:
        return [data]

    for key in ("sheets", "sheet", "worksheets", "pages"):
        value = data.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]

    return []


def topic_title(topic: Dict[str, Any]) -> str:
    title = topic.get("title")
    if isinstance(title, str) and title.strip():
        return " ".join(title.split())
    return "[untitled]"


def iter_child_topics(topic: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    children = topic.get("children")
    if not isinstance(children, dict):
        return []

    found: List[Dict[str, Any]] = []
    seen_ids = set()

    def add_candidates(value: Any) -> None:
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    item_id = item.get("id")
                    if item_id and item_id in seen_ids:
                        continue
                    if item_id:
                        seen_ids.add(item_id)
                    found.append(item)
        elif isinstance(value, dict):
            for subkey in ("attached", "detached"):
                add_candidates(value.get(subkey))

    for key in ("attached", "topics", "detached"):
        add_candidates(children.get(key))

    for key, value in children.items():
        if key not in {"attached", "topics", "detached", "summary", "summaries"}:
            add_candidates(value)

    return found


def iter_summary_topics(topic: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    children = topic.get("children")
    if not isinstance(children, dict):
        return []
    value = children.get("summary")
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def render_topic_markdown(topic: Dict[str, Any], depth: int, include_summaries: bool) -> List[str]:
    indent = "  " * depth
    lines = [f"{indent}- {topic_title(topic)}"]

    for child in iter_child_topics(topic):
        lines.extend(render_topic_markdown(child, depth + 1, include_summaries))

    if include_summaries:
        summary_indent = "  " * (depth + 1)
        for summary in iter_summary_topics(topic):
            lines.append(f"{summary_indent}- [summary] {topic_title(summary)}")

    return lines


def render_json_outline(topic: Dict[str, Any], include_summaries: bool) -> Dict[str, Any]:
    node = {
        "title": topic_title(topic),
        "children": [render_json_outline(child, include_summaries) for child in iter_child_topics(topic)],
    }
    if include_summaries:
        summaries = [topic_title(item) for item in iter_summary_topics(topic)]
        if summaries:
            node["summaries"] = summaries
    return node


def load_xmind_xml(zf: zipfile.ZipFile) -> List[Dict[str, Any]]:
    if "content.xml" not in zf.namelist():
        return []

    try:
        root = ET.fromstring(zf.read("content.xml"))
    except ET.ParseError:
        return []

    ns = {"x": root.tag.split("}")[0].strip("{")}
    sheets = []
    for sheet in root.findall("x:sheet", ns):
        title = sheet.findtext("x:title", default="", namespaces=ns).strip() or sheet.get("id") or "sheet"
        root_topic = sheet.find("x:topic", ns)
        if root_topic is None:
            continue
        sheets.append({
            "title": title,
            "rootTopic": xml_topic_to_json(root_topic, ns),
        })
    return sheets


def xml_topic_to_json(elem: ET.Element, ns: Dict[str, str]) -> Dict[str, Any]:
    topic = {"title": (elem.findtext("x:title", default="", namespaces=ns) or "[untitled]").strip()}
    child_topics: List[Dict[str, Any]] = []
    children_elem = elem.find("x:children", ns)
    if children_elem is not None:
        for topics_elem in children_elem.findall("x:topics", ns):
            for child in topics_elem.findall("x:topic", ns):
                child_topics.append(xml_topic_to_json(child, ns))
    if child_topics:
        topic["children"] = {"attached": child_topics}
    return topic


def load_sheets(path: Path) -> List[Dict[str, Any]]:
    with zipfile.ZipFile(path) as zf:
        sheets = load_xmind_json(zf)
        if sheets:
            return sheets
        sheets = load_xmind_xml(zf)
        if sheets:
            return sheets
    raise ValueError("unsupported xmind structure: expected content.json, workbook.json, or readable content.xml")


def render_markdown(sheets: Sequence[Dict[str, Any]], include_summaries: bool) -> str:
    lines: List[str] = []
    for idx, sheet in enumerate(sheets):
        sheet_title = sheet.get("title")
        root_topic = sheet.get("rootTopic")
        if not isinstance(root_topic, dict):
            continue

        if idx > 0:
            lines.append("")
        if isinstance(sheet_title, str) and sheet_title.strip():
            lines.append(f"# Sheet: {' '.join(sheet_title.split())}")
        lines.extend(render_topic_markdown(root_topic, 0, include_summaries))
    return "\n".join(lines)


def render_json(sheets: Sequence[Dict[str, Any]], include_summaries: bool) -> str:
    payload = []
    for sheet in sheets:
        root_topic = sheet.get("rootTopic")
        if not isinstance(root_topic, dict):
            continue
        payload.append({
            "sheet_title": sheet.get("title") or "",
            "root": render_json_outline(root_topic, include_summaries),
        })
    return json.dumps(payload, ensure_ascii=False, indent=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract a readable outline from a .xmind file")
    parser.add_argument("input", type=Path, help="path to .xmind file")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--no-summaries", action="store_true", help="omit summary annotations")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.input.exists():
        print(f"error: file not found: {args.input}", file=sys.stderr)
        return 1

    try:
        sheets = load_sheets(args.input)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    include_summaries = not args.no_summaries
    if args.format == "json":
        print(render_json(sheets, include_summaries))
    else:
        print(render_markdown(sheets, include_summaries))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
