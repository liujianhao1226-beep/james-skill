#!/usr/bin/env python3
"""Merge and align testcase JSON files into a final balanced deliverable.

Usage:
  python scripts/align_testcases.py a.json b.json -o aligned.json --limit 100
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

BASE_COLUMNS = [
    "所属模块",
    "用例标题",
    "前置条件",
    "步骤",
    "预期",
    "优先级",
    "用例类型",
    "适用阶段",
]

ALIASES = {
    "所属模块": ["所属模块", "module"],
    "用例标题": ["用例标题", "title"],
    "前置条件": ["前置条件", "preconditions"],
    "步骤": ["步骤", "steps"],
    "预期": ["预期", "expected"],
    "优先级": ["优先级", "priority"],
    "用例类型": ["用例类型", "case_type"],
    "适用阶段": ["适用阶段", "stage"],
}

CASE_TYPE_MAP = {
    "功能测试": "功能测试",
    "异常测试": "异常测试",
    "边界测试": "边界测试",
    "场景测试": "场景测试",
    "functional": "功能测试",
    "abnormal": "异常测试",
    "boundary": "边界测试",
    "scenario": "场景测试",
}

PRIORITY_MAP = {
    "P0": "1",
    "P1": "2",
    "P2": "3",
    "p0": "1",
    "p1": "2",
    "p2": "3",
}

TYPE_RANK = {"场景测试": 0, "功能测试": 1, "异常测试": 2, "边界测试": 3}
TRACE_PATTERNS = [
    r"导图映射",
    r"脑图展开",
    r"原路径",
    r"根据节点",
    r"按导图路径",
    r"满足导图要求",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge and align testcase JSON files")
    parser.add_argument("inputs", nargs="+", help="Input JSON file(s)")
    parser.add_argument("-o", "--output", required=True, help="Output JSON path")
    parser.add_argument("--limit", type=int, default=0, help="Limit final case count")
    parser.add_argument("--default-stage", default="", help="Override empty stage values")
    parser.add_argument(
        "--seed-per-module",
        type=int,
        default=1,
        help="Minimum number of seeded cases to keep per top-level module when limiting",
    )
    return parser.parse_args()


def load_cases(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(data, list):
        cases = data
    elif isinstance(data, dict) and isinstance(data.get("cases"), list):
        cases = data["cases"]
    else:
        raise ValueError(f"{path} is not a testcase list or {{'cases': [...]}} object")
    if not all(isinstance(item, dict) for item in cases):
        raise ValueError(f"{path} contains non-object testcase entries")
    return cases


def get_value(case: dict[str, Any], field: str) -> Any:
    for key in ALIASES[field]:
        if key in case:
            return case[key]
    return ""


def clean_text(text: str) -> str:
    text = text.strip()
    for pattern in TRACE_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[ ]+[-][ ]+", "-", text)
    return text.strip(" -")


def normalize_lines(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        items = value
    elif isinstance(value, str):
        items = value.splitlines()
    else:
        items = [str(value)]

    lines: list[str] = []
    for item in items:
        text = str(item).strip()
        if not text:
            continue
        text = re.sub(r"^\d+\.\s*", "", text)
        lines.append(clean_text(text))
    return lines


def normalize_module(value: Any) -> str:
    text = clean_text(str(value))
    if not text:
        return "/未分类"
    text = text.replace("\\", "/")
    text = re.sub(r"/{2,}", "/", text)
    if not text.startswith("/"):
        text = "/" + text
    return text.rstrip("/") or "/未分类"


def normalize_priority(value: Any) -> str:
    text = str(value).strip()
    return PRIORITY_MAP.get(text, text or "2")


def normalize_case_type(value: Any) -> str:
    text = str(value).strip()
    return CASE_TYPE_MAP.get(text, text or "功能测试")


def top_module(module: str) -> str:
    parts = [seg for seg in module.split("/") if seg]
    return parts[0] if parts else "未分类"


def normalize_case(case: dict[str, Any], default_stage: str) -> dict[str, Any]:
    stage = clean_text(str(get_value(case, "适用阶段")))
    return {
        "所属模块": normalize_module(get_value(case, "所属模块")),
        "用例标题": clean_text(str(get_value(case, "用例标题"))),
        "前置条件": normalize_lines(get_value(case, "前置条件")),
        "步骤": normalize_lines(get_value(case, "步骤")),
        "预期": normalize_lines(get_value(case, "预期")),
        "优先级": normalize_priority(get_value(case, "优先级")),
        "用例类型": normalize_case_type(get_value(case, "用例类型")),
        "适用阶段": stage or default_stage or "版本验证阶段",
    }


def case_score(case: dict[str, Any]) -> tuple[int, int, int, int, str, str]:
    priority_rank = {"1": 0, "2": 1, "3": 2}.get(str(case["优先级"]), 9)
    type_rank = TYPE_RANK.get(str(case["用例类型"]), 9)
    step_rank = -len(case["步骤"])
    expected_rank = -len(case["预期"])
    return (
        priority_rank,
        type_rank,
        step_rank,
        expected_rank,
        str(case["所属模块"]),
        str(case["用例标题"]),
    )


def dedupe_cases(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for case in cases:
        key = (str(case["所属模块"]), str(case["用例标题"]))
        current = best_by_key.get(key)
        if current is None or case_score(case) < case_score(current):
            best_by_key[key] = case
    return list(best_by_key.values())


def select_balanced(cases: list[dict[str, Any]], limit: int, seed_per_module: int) -> list[dict[str, Any]]:
    ordered = sorted(cases, key=case_score)
    if limit <= 0 or len(ordered) <= limit:
        return ordered

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in ordered:
        groups[top_module(str(case["所属模块"]))].append(case)

    selected: list[dict[str, Any]] = []
    selected_keys: set[tuple[str, str]] = set()

    for module_name in sorted(groups):
        kept = 0
        for case in groups[module_name]:
            if kept >= seed_per_module or len(selected) >= limit:
                break
            key = (str(case["所属模块"]), str(case["用例标题"]))
            if key in selected_keys:
                continue
            selected.append(case)
            selected_keys.add(key)
            kept += 1

    while len(selected) < limit:
        progressed = False
        for module_name in sorted(groups):
            if len(selected) >= limit:
                break
            while groups[module_name]:
                case = groups[module_name].pop(0)
                key = (str(case["所属模块"]), str(case["用例标题"]))
                if key in selected_keys:
                    continue
                selected.append(case)
                selected_keys.add(key)
                progressed = True
                break
        if not progressed:
            break

    return selected[:limit]


def main() -> None:
    args = parse_args()
    cases: list[dict[str, Any]] = []
    for raw_input in args.inputs:
        path = Path(raw_input)
        for case in load_cases(path):
            normalized = normalize_case(case, args.default_stage)
            if not normalized["用例标题"] or not normalized["步骤"] or not normalized["预期"]:
                continue
            cases.append(normalized)

    aligned = dedupe_cases(cases)
    aligned = select_balanced(aligned, args.limit, max(args.seed_per_module, 0))

    output = Path(args.output)
    output.write_text(
        json.dumps({"cases": aligned}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Aligned {len(cases)} input case(s) into {len(aligned)} final case(s): {output}")


if __name__ == "__main__":
    main()
