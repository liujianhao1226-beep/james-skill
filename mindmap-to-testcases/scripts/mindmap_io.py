#!/usr/bin/env python3
"""Utilities for extracting normalized root-to-leaf paths from mind map sources."""

from __future__ import annotations

import csv
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

BULLET_RE = re.compile(r"^(?P<indent>[ \t]*)(?P<marker>(?:[-+*])|(?:\d+[.)]))\s+(?P<title>.+?)\s*$")
HEADING_RE = re.compile(r"^(?P<indent>[ \t]*)#{1,6}\s+(?P<title>.+?)\s*$")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
PATH_DELIMS_RE = re.compile(r"\s*(?:->|=>|/|\\|\||→)\s*")

# Annotation prefixes: nodes starting with these are metadata, not test paths.
ANNOTATION_PREFIXES = ("注：", "注:", "备注：", "备注:", "NOTE:", "Note:", "note:",
                       "说明：", "说明:", "TODO:", "TODO：", "FIXME:", "FIXME：",
                       "参考：", "参考:", "提示：", "提示:")

PATH_HEADER_HINTS = {
    "path",
    "路径",
    "层级",
    "tree",
    "outline",
    "module",
    "scene",
    "action",
    "result",
    "节点",
}
LEVEL_HEADER_PATTERNS = [
    re.compile(r"^l\d+$", re.I),
    re.compile(r"^level\s*\d+$", re.I),
    re.compile(r"^层级\d+$"),
    re.compile(r"^第?\d+级$"),
    re.compile(r"^[一二三四五六七八九十]+级$"),
]
TESTCASE_TABLE_HEADERS = {"所属模块", "用例标题", "前置条件", "步骤", "预期"}


class MindmapParseError(ValueError):
    """Raised when a source file cannot be parsed into a path list."""


def collapse_ws(text: Any) -> str:
    return " ".join(str(text or "").replace("\u3000", " ").split())


def is_annotation_node(text: str) -> bool:
    """Return True if the node text is an annotation/comment, not a real test node."""
    stripped = text.strip()
    if not stripped:
        return False
    return any(stripped.startswith(prefix) for prefix in ANNOTATION_PREFIXES)


def is_empty_or_untitled(text: str) -> bool:
    """Return True if the node text is empty or a placeholder."""
    stripped = text.strip()
    return not stripped or stripped == "[untitled]"


def clean_title(value: Any) -> str:
    text = collapse_ws(value)
    if not text:
        raise MindmapParseError("empty node title encountered")
    return text


def path_text(path: Sequence[str]) -> str:
    return " -> ".join(path)


def make_path_record(path: Sequence[str], sheet_title: str | None = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "path": list(path),
        "path_text": path_text(path),
    }
    if sheet_title:
        payload["sheet_title"] = sheet_title
    # Tag paths that end with an annotation node so downstream can handle them.
    if path and is_annotation_node(path[-1]):
        payload["is_annotation"] = True
    return payload


def topic_title(topic: Dict[str, Any]) -> str:
    title = topic.get("title")
    if isinstance(title, str) and title.strip():
        return collapse_ws(title)
    return "[untitled]"


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


def load_xmind_json(zf: zipfile.ZipFile) -> List[Dict[str, Any]]:
    names = set(zf.namelist())
    if "content.json" in names:
        sheets = normalize_sheet_container(json.loads(zf.read("content.json")))
        if sheets:
            return sheets
    if "workbook.json" in names:
        sheets = normalize_sheet_container(json.loads(zf.read("workbook.json")))
        if sheets:
            return sheets
    return []


def xml_topic_to_json(elem: ET.Element, ns: Dict[str, str]) -> Dict[str, Any]:
    title = (elem.findtext("x:title", default="", namespaces=ns) or "[untitled]").strip()
    topic: Dict[str, Any] = {"title": collapse_ws(title)}
    child_topics: List[Dict[str, Any]] = []
    children_elem = elem.find("x:children", ns)
    if children_elem is not None:
        for topics_elem in children_elem.findall("x:topics", ns):
            for child in topics_elem.findall("x:topic", ns):
                child_topics.append(xml_topic_to_json(child, ns))
    if child_topics:
        topic["children"] = {"attached": child_topics}
    return topic


def load_xmind_xml(zf: zipfile.ZipFile) -> List[Dict[str, Any]]:
    if "content.xml" not in zf.namelist():
        return []
    try:
        root = ET.fromstring(zf.read("content.xml"))
    except ET.ParseError as exc:
        raise MindmapParseError(f"unable to parse content.xml: {exc}") from exc

    ns = {"x": root.tag.split("}")[0].strip("{")} if "}" in root.tag else {"x": ""}
    sheets = []
    for sheet in root.findall("x:sheet", ns):
        title = sheet.findtext("x:title", default="", namespaces=ns).strip() or sheet.get("id") or "sheet"
        root_topic = sheet.find("x:topic", ns)
        if root_topic is None:
            continue
        sheets.append({"title": title, "rootTopic": xml_topic_to_json(root_topic, ns)})
    return sheets


def extract_topic_paths(
    topic: Dict[str, Any],
    prefix: Sequence[str] | None = None,
    sheet_title: str | None = None,
) -> List[Dict[str, Any]]:
    current_prefix = list(prefix or [])
    current_prefix.append(topic_title(topic))
    children = list(iter_child_topics(topic))
    if not children:
        return [make_path_record(current_prefix, sheet_title=sheet_title)]

    records: List[Dict[str, Any]] = []
    for child in children:
        records.extend(extract_topic_paths(child, current_prefix, sheet_title=sheet_title))
    return records


def parse_xmind(path: Path, strip_root: bool = False) -> Dict[str, Any]:
    try:
        with zipfile.ZipFile(path) as zf:
            sheets = load_xmind_json(zf)
            if not sheets:
                sheets = load_xmind_xml(zf)
    except zipfile.BadZipFile as exc:
        raise MindmapParseError(f"invalid xmind file: {exc}") from exc

    if not sheets:
        raise MindmapParseError("unsupported xmind structure: expected content.json, workbook.json, or content.xml")

    from collections import Counter
    groups: List[Dict[str, Any]] = []
    total_paths = 0
    total_annotations = 0
    all_depths: List[int] = []

    for sheet in sheets:
        root_topic = sheet.get("rootTopic")
        if not isinstance(root_topic, dict):
            continue
        sheet_title = collapse_ws(sheet.get("title") or "") or None
        paths = extract_topic_paths(root_topic, sheet_title=sheet_title)

        if strip_root and paths:
            root_title = topic_title(root_topic)
            for record in paths:
                if record["path"] and record["path"][0] == root_title:
                    record["path"] = record["path"][1:]
                    record["path_text"] = path_text(record["path"])

        total_paths += len(paths)
        total_annotations += sum(1 for r in paths if r.get("is_annotation"))
        all_depths.extend(len(r["path"]) for r in paths)

        groups.append(
            {
                "sheet_title": sheet_title or "",
                "root_title": topic_title(root_topic),
                "path_count": len(paths),
                "paths": paths,
            }
        )

    if not groups:
        raise MindmapParseError("no readable root topics found in xmind file")

    depth_dist = dict(sorted(Counter(all_depths).items()))
    return {
        "source_file": path.name,
        "source_type": "xmind",
        "stats": {
            "total_paths": total_paths,
            "annotation_paths": total_annotations,
            "depth_distribution": depth_dist,
        },
        "groups": groups,
    }


def add_child(parent: Dict[str, Any] | None, node: Dict[str, Any], roots: List[Dict[str, Any]]) -> None:
    if parent is None:
        roots.append(node)
    else:
        parent.setdefault("children", []).append(node)


def outline_to_tree(text: str, title_hint: str | None = None) -> Dict[str, Any]:
    roots: List[Dict[str, Any]] = []
    heading_stack: List[Tuple[int, Dict[str, Any]]] = []
    bullet_stack: List[Tuple[int, Dict[str, Any]]] = []
    saw_structure = False

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        if line.strip().startswith("```"):
            continue

        heading_match = HEADING_RE.match(line)
        if heading_match:
            saw_structure = True
            level = len(line) - len(line.lstrip("#"))
            title = clean_title(heading_match.group("title"))
            node = {"title": title, "children": []}
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            parent = heading_stack[-1][1] if heading_stack else None
            add_child(parent, node, roots)
            heading_stack.append((level, node))
            bullet_stack = []
            continue

        bullet_match = BULLET_RE.match(line)
        if bullet_match:
            saw_structure = True
            indent = len(bullet_match.group("indent").replace("\t", "    "))
            title = clean_title(bullet_match.group("title"))
        else:
            saw_structure = True
            indent = len(line) - len(line.lstrip(" \t"))
            title = clean_title(line.strip())

        node = {"title": title, "children": []}
        while bullet_stack and indent <= bullet_stack[-1][0]:
            bullet_stack.pop()
        if bullet_stack:
            parent = bullet_stack[-1][1]
        elif heading_stack:
            parent = heading_stack[-1][1]
        else:
            parent = None
        add_child(parent, node, roots)
        bullet_stack.append((indent, node))

    if not saw_structure or not roots:
        raise MindmapParseError("no outline hierarchy found in text input")

    if len(roots) == 1:
        root = roots[0]
        return {"title": root["title"], "root": root}

    title = title_hint or "mindmap"
    return {"title": title, "root": {"title": title, "children": roots}}


def iter_leaf_paths(node: Dict[str, Any], prefix: Sequence[str] | None = None) -> List[List[str]]:
    title = node.get("title", "")
    # Skip empty/untitled nodes entirely — they produce noise paths.
    if is_empty_or_untitled(title):
        return []
    current = list(prefix or [])
    current.append(clean_title(title))
    children = node.get("children") or []
    # If this node is an annotation, keep it as a leaf but don't recurse further.
    if is_annotation_node(title):
        return [current]
    if not children:
        return [current]
    paths: List[List[str]] = []
    for child in children:
        if isinstance(child, dict):
            paths.extend(iter_leaf_paths(child, current))
    # If all children were filtered out, this node itself becomes a leaf.
    if not paths:
        return [current]
    return paths


def parse_outline(path: Path, strip_root: bool = False) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    title_hint = path.stem
    wrapper = outline_to_tree(text, title_hint=title_hint)
    root = wrapper["root"]
    paths = [make_path_record(items) for items in iter_leaf_paths(root)]

    if strip_root and paths:
        root_title = root["title"]
        for record in paths:
            if record["path"] and record["path"][0] == root_title:
                record["path"] = record["path"][1:]
                record["path_text"] = path_text(record["path"])

    from collections import Counter
    depth_dist = dict(sorted(Counter(len(r["path"]) for r in paths).items()))
    annotation_count = sum(1 for r in paths if r.get("is_annotation"))

    return {
        "source_file": path.name,
        "source_type": "outline",
        "stats": {
            "total_paths": len(paths),
            "annotation_paths": annotation_count,
            "depth_distribution": depth_dist,
        },
        "groups": [
            {
                "sheet_title": title_hint,
                "root_title": root["title"],
                "path_count": len(paths),
                "paths": paths,
            }
        ],
    }


def local_name(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def find_first_descendant(elem: ET.Element, tag_name: str) -> ET.Element | None:
    for candidate in elem.iter():
        if local_name(candidate.tag) == tag_name:
            return candidate
    return None


def freemind_node_title(elem: ET.Element) -> str:
    for attr in ("TEXT", "text", "LOCALIZED_TEXT", "localized_text"):
        text = collapse_ws(elem.get(attr))
        if text:
            return text

    for child in list(elem):
        if local_name(child.tag) != "richcontent":
            continue
        content_type = str(child.get("TYPE") or child.get("type") or "").upper()
        if content_type != "NODE":
            continue
        text = collapse_ws(" ".join(part.strip() for part in child.itertext() if part and part.strip()))
        if text:
            return text
    return "[untitled]"


def freemind_node_to_tree(elem: ET.Element) -> Dict[str, Any] | None:
    title = freemind_node_title(elem)
    # Skip nodes with empty or untitled text.
    if is_empty_or_untitled(title):
        return None
    node: Dict[str, Any] = {"title": title}
    children: List[Dict[str, Any]] = []
    for child in list(elem):
        if local_name(child.tag) == "node":
            child_node = freemind_node_to_tree(child)
            if child_node is not None:
                children.append(child_node)
    if children:
        node["children"] = children
    return node


def parse_freemind(path: Path, strip_root: bool = False) -> Dict[str, Any]:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise MindmapParseError(f"unable to parse .mm xml: {exc}") from exc

    root_node = find_first_descendant(root, "node")
    if root_node is None:
        raise MindmapParseError("no <node> element found in .mm file")

    topic = freemind_node_to_tree(root_node)
    if topic is None:
        raise MindmapParseError("root node is empty in .mm file")
    paths = [make_path_record(items, sheet_title=path.stem) for items in iter_leaf_paths(topic)]
    if not paths:
        raise MindmapParseError("no valid root-to-leaf paths found in .mm file")

    # Optionally strip the root node (document title) from every path.
    if strip_root and paths:
        root_title = topic["title"]
        for record in paths:
            if record["path"] and record["path"][0] == root_title:
                record["path"] = record["path"][1:]
                record["path_text"] = path_text(record["path"])

    # Compute depth statistics for diagnostics.
    from collections import Counter
    depth_dist = dict(sorted(Counter(len(r["path"]) for r in paths).items()))
    annotation_count = sum(1 for r in paths if r.get("is_annotation"))

    return {
        "source_file": path.name,
        "source_type": "freemind",
        "stats": {
            "total_paths": len(paths),
            "annotation_paths": annotation_count,
            "depth_distribution": depth_dist,
        },
        "groups": [
            {
                "sheet_title": path.stem,
                "root_title": topic["title"],
                "path_count": len(paths),
                "paths": paths,
            }
        ],
    }


def header_looks_like_level(name: str) -> bool:
    normalized = collapse_ws(name).lower().replace("_", "").replace("-", "")
    if normalized in PATH_HEADER_HINTS:
        return True
    return any(pattern.match(normalized) for pattern in LEVEL_HEADER_PATTERNS)


def is_testcase_table(headers: Sequence[str]) -> bool:
    header_set = {collapse_ws(item) for item in headers if collapse_ws(item)}
    return TESTCASE_TABLE_HEADERS.issubset(header_set)


def choose_csv_path_columns(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> List[int]:
    indexed_headers = [(idx, collapse_ws(name)) for idx, name in enumerate(headers)]
    explicit = [idx for idx, name in indexed_headers if header_looks_like_level(name)]
    if explicit:
        return explicit

    if not rows:
        return []

    max_cols = max(len(row) for row in rows)
    non_empty_ratio: List[Tuple[int, float]] = []
    for idx in range(max_cols):
        non_empty = 0
        for row in rows:
            if idx < len(row) and collapse_ws(row[idx]):
                non_empty += 1
        non_empty_ratio.append((idx, non_empty / max(len(rows), 1)))

    candidates = [idx for idx, ratio in non_empty_ratio if ratio >= 0.1]
    return candidates[:8]


def split_path_cell(value: str) -> List[str]:
    text = collapse_ws(value)
    if not text:
        return []
    if PATH_DELIMS_RE.search(text):
        return [part for part in (collapse_ws(item) for item in PATH_DELIMS_RE.split(text)) if part]
    return [text]


def parse_csv(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        raise MindmapParseError("csv file is empty")

    headers = [collapse_ws(item) for item in rows[0]]
    data_rows = rows[1:] if headers else rows

    if is_testcase_table(headers):
        raise MindmapParseError(
            "csv appears to already be a testcase table; use it as a style/reference sample instead of parsing it as a mind map source"
        )

    path_columns = choose_csv_path_columns(headers, data_rows)
    if not path_columns:
        raise MindmapParseError("unable to infer hierarchy columns from csv")

    paths: List[Dict[str, Any]] = []
    for row in data_rows:
        parts: List[str] = []
        for idx in path_columns:
            if idx >= len(row):
                continue
            parts.extend(split_path_cell(row[idx]))
        parts = [part for part in parts if part]
        if len(parts) >= 2:
            paths.append(make_path_record(parts))

    if not paths:
        raise MindmapParseError("no valid root-to-leaf paths found in csv")

    return {
        "source_file": path.name,
        "source_type": "csv",
        "groups": [
            {
                "sheet_title": path.stem,
                "root_title": paths[0]["path"][0],
                "path_count": len(paths),
                "paths": paths,
            }
        ],
    }


def parse_source(path: Path, input_format: str = "auto", strip_root: bool = False) -> Dict[str, Any]:
    suffix = path.suffix.lower()
    if input_format == "auto":
        if suffix == ".xmind":
            input_format = "xmind"
        elif suffix == ".mm":
            input_format = "freemind"
        elif suffix in {".md", ".markdown", ".txt"}:
            input_format = "outline"
        elif suffix == ".csv":
            input_format = "csv"
        elif suffix in IMAGE_SUFFIXES:
            input_format = "image"
        else:
            raise MindmapParseError(f"unsupported input suffix: {suffix or '[none]'}")

    if input_format == "xmind":
        return parse_xmind(path, strip_root=strip_root)
    if input_format in {"freemind", "mm"}:
        return parse_freemind(path, strip_root=strip_root)
    if input_format in {"outline", "markdown", "text"}:
        return parse_outline(path, strip_root=strip_root)
    if input_format == "csv":
        return parse_csv(path)
    if input_format == "image":
        raise MindmapParseError(
            "image inputs should be read with vision first; this script only normalizes xmind, freemind .mm, outline text, and csv sources"
        )
    raise MindmapParseError(f"unsupported input format: {input_format}")
