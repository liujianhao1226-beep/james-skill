#!/usr/bin/env python3
"""Shared helpers for normalized scope trees and XMind export."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

NODE_KEYS_TO_PRESERVE = {
    "title", "type", "note", "source_refs", "confidence", "order", "children",
    # P1 extensions
    "priority",          # "P0" | "P1" | "P2" | "P3"
    "test_type",         # list of: "functional" | "performance" | "security" | "compatibility" | "stability" | "exploratory"
    "automation_hint",   # "auto" | "manual" | "semi-auto"
    "risk_score",        # float 0-1000 (RPN from risk_scorer)
}

VERSION_BOUNDARY_KEYWORDS = {
    "版本边界",
    "待确认",
    "version boundary",
    "pending confirmation",
    "future",
    "scope boundary",
}

CROSS_CUTTING_KEYWORDS = {
    "默认",
    "边界",
    "异常",
    "同步",
    "恢复",
    "记忆",
    "日志",
    "观测",
    "default",
    "boundary",
    "exception",
    "sync",
    "recovery",
    "restore",
    "logging",
    "observability",
}

QUALITY_DOMAIN_KEYWORDS = {
    "兼容",
    "性能",
    "稳定",
    "恢复",
    "安全",
    "隐私",
    "诊断",
    "ota",
    "compat",
    "performance",
    "stability",
    "security",
    "privacy",
    "diagnostic",
}

BULLET_RE = re.compile(r"^(?P<indent>[ \t]*)(?P<marker>(?:[-+*])|(?:\d+[.)]))\s+(?P<title>.+?)\s*$")
HEADING_RE = re.compile(r"^#{1,6}\s+(?P<title>.+?)\s*$")


class ScopeTreeError(ValueError):
    """Raised when a scope tree cannot be parsed or normalized."""


@dataclass
class TreeStats:
    node_count: int = 0
    leaf_count: int = 0
    max_depth: int = 0

    def to_dict(self) -> Dict[str, int]:
        return {
            "node_count": self.node_count,
            "leaf_count": self.leaf_count,
            "max_depth": self.max_depth,
        }


def collapse_ws(text: str) -> str:
    return " ".join(str(text).replace("\u3000", " ").split())


def coerce_title(value: Any) -> str:
    title = collapse_ws(value)
    if not title:
        raise ScopeTreeError("empty node title encountered")
    return title


def normalize_node(node: Any) -> Dict[str, Any]:
    if isinstance(node, str):
        return {"title": coerce_title(node), "children": []}

    if not isinstance(node, dict):
        raise ScopeTreeError(f"unsupported node type: {type(node).__name__}")

    title = node.get("title")
    if title is None:
        raise ScopeTreeError("node is missing required field 'title'")

    normalized: Dict[str, Any] = {"title": coerce_title(title), "children": []}
    for key in NODE_KEYS_TO_PRESERVE - {"title", "children"}:
        if key in node and node[key] not in (None, "", []):
            normalized[key] = node[key]

    children = node.get("children", [])
    if children is None:
        children = []
    if not isinstance(children, list):
        raise ScopeTreeError(f"children for '{normalized['title']}' must be a list")
    normalized["children"] = [normalize_node(child) for child in children]
    return normalized


def ensure_wrapper(data: Any, title_hint: Optional[str] = None) -> Dict[str, Any]:
    if isinstance(data, dict) and isinstance(data.get("root"), dict):
        root = normalize_node(data["root"])
        title = collapse_ws(data.get("title") or root["title"] or title_hint or "test scope")
        warnings = data.get("warnings") or []
        if not isinstance(warnings, list):
            warnings = [collapse_ws(str(warnings))]
        return {
            "title": title,
            "root": root,
            "warnings": [collapse_ws(str(item)) for item in warnings if collapse_ws(str(item))],
        }

    if isinstance(data, dict):
        node = normalize_node(data)
        title = collapse_ws(title_hint or node["title"])
        return {"title": title, "root": node, "warnings": []}

    if isinstance(data, list):
        children = [normalize_node(item) for item in data]
        title = collapse_ws(title_hint or "test scope")
        return {
            "title": title,
            "root": {"title": title, "type": "root", "children": children},
            "warnings": [],
        }

    raise ScopeTreeError("json input must be a node object, wrapper object, or list of nodes")


def parse_markdown_outline(text: str, title_hint: Optional[str] = None) -> Dict[str, Any]:
    lines = text.splitlines()
    heading_title: Optional[str] = None
    stack: List[Tuple[int, Dict[str, Any]]] = []
    roots: List[Dict[str, Any]] = []

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            continue
        heading_match = HEADING_RE.match(raw_line)
        if heading_match and heading_title is None:
            heading_title = collapse_ws(heading_match.group("title"))
            continue
        bullet_match = BULLET_RE.match(raw_line)
        if not bullet_match:
            continue

        indent_text = bullet_match.group("indent").replace("\t", "    ")
        indent = len(indent_text)
        title = coerce_title(bullet_match.group("title"))
        node = {"title": title, "children": []}

        while stack and indent <= stack[-1][0]:
            stack.pop()

        if stack:
            stack[-1][1]["children"].append(node)
        else:
            roots.append(node)
        stack.append((indent, node))

    if not roots:
        raise ScopeTreeError("no bullet hierarchy found in markdown input")

    if len(roots) == 1:
        root = roots[0]
        title = collapse_ws(title_hint or heading_title or root["title"])
        if title != root["title"]:
            root = {"title": title, "type": root.get("type", "root"), "children": root["children"]}
        return {"title": title, "root": normalize_node(root), "warnings": []}

    title = collapse_ws(title_hint or heading_title or "test scope")
    wrapper = {
        "title": title,
        "root": {"title": title, "type": "root", "children": roots},
        "warnings": [],
    }
    return ensure_wrapper(wrapper, title_hint=title)


def load_tree_from_path(path: Path, input_format: str = "auto", title_hint: Optional[str] = None) -> Dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    chosen = input_format
    if chosen == "auto":
        chosen = "json" if path.suffix.lower() == ".json" else "markdown"

    if chosen == "json":
        data = json.loads(raw)
        return ensure_wrapper(data, title_hint=title_hint)
    if chosen == "markdown":
        return parse_markdown_outline(raw, title_hint=title_hint)
    raise ScopeTreeError(f"unsupported input format: {input_format}")


def iter_nodes(node: Dict[str, Any], depth: int = 0) -> Iterable[Tuple[Dict[str, Any], int]]:
    yield node, depth
    for child in node.get("children", []):
        yield from iter_nodes(child, depth + 1)


def compute_stats(root: Dict[str, Any]) -> TreeStats:
    stats = TreeStats()
    for node, depth in iter_nodes(root):
        stats.node_count += 1
        stats.max_depth = max(stats.max_depth, depth)
        if not node.get("children"):
            stats.leaf_count += 1
    return stats


def _contains_keyword(title: str, keywords: Iterable[str]) -> bool:
    lowered = title.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def collect_warnings(root: Dict[str, Any]) -> List[str]:
    warnings: List[str] = []

    def walk(node: Dict[str, Any], path: List[str], depth: int) -> None:
        title = node["title"]
        children = node.get("children", [])
        if len(title) > 36:
            warnings.append(f"long node title may be hard to read in xmind: {' / '.join(path + [title])}")
        if depth > 6:
            warnings.append(f"tree depth exceeds 6 levels at: {' / '.join(path + [title])}")
        seen = set()
        for child in children:
            child_title = child["title"]
            lowered = child_title.lower()
            if lowered in seen:
                warnings.append(f"duplicate sibling title under {' / '.join(path + [title])}: {child_title}")
            else:
                seen.add(lowered)
        if len(children) > 12:
            warnings.append(f"node has more than 12 direct children and may need grouping: {' / '.join(path + [title])}")
        for child in children:
            walk(child, path + [title], depth + 1)

    walk(root, [], 0)

    top_titles = [child["title"] for child in root.get("children", [])]
    if top_titles:
        if not any(_contains_keyword(title, VERSION_BOUNDARY_KEYWORDS) for title in top_titles):
            warnings.append("top level has no obvious version-boundary branch")
        if not any(_contains_keyword(title, CROSS_CUTTING_KEYWORDS) for _, _depth in iter_nodes(root) for title in [_["title"]]):
            warnings.append("tree has no obvious cross-cutting branch for defaults, exceptions, sync, or recovery")
        if not any(_contains_keyword(title, QUALITY_DOMAIN_KEYWORDS) for title in top_titles):
            warnings.append("top level has no obvious quality branch such as compatibility, performance, stability, or security")
        if len(top_titles) < 3:
            warnings.append("top level is very small; confirm whether more major domains are needed")
    return dedupe_preserve_order(warnings)


def dedupe_preserve_order(items: Iterable[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        normalized = collapse_ws(item)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def prepare_tree(wrapper: Dict[str, Any]) -> Dict[str, Any]:
    wrapped = ensure_wrapper(wrapper, title_hint=wrapper.get("title") if isinstance(wrapper, dict) else None)
    stats = compute_stats(wrapped["root"])
    warnings = dedupe_preserve_order(list(wrapped.get("warnings", [])) + collect_warnings(wrapped["root"]))
    wrapped["warnings"] = warnings
    wrapped["stats"] = stats.to_dict()
    return wrapped


def save_json(data: Dict[str, Any], output: Optional[Path] = None) -> None:
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    if output is None:
        print(payload)
    else:
        output.write_text(payload + "\n", encoding="utf-8")
