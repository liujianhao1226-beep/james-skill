#!/usr/bin/env python3
"""FMEA-style risk scorer for smart-hardware scope trees.

Computes a Risk Priority Number (RPN) for each node based on three dimensions:
  - Severity (S):      impact if the area fails in production (1-10)
  - Probability (P):   likelihood the area contains a defect (1-10)
  - Detectability (D): how hard it is to catch the defect before release (1-10)

  RPN = S × P × D   (range 1–1000)

The scorer uses keyword-based heuristics and structural signals to estimate
each dimension automatically.  The user or agent can also supply explicit
values via the node's ``priority`` or ``confidence`` fields.

Usage:
    python3 risk_scorer.py scope-tree.json [--output scored.json] [--json-report] [--top 20]
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from scope_tree_lib import (
    ScopeTreeError,
    iter_nodes,
    load_tree_from_path,
    prepare_tree,
    save_json,
)

# ---------------------------------------------------------------------------
# Severity keyword signals (S dimension)
# Higher severity = larger user / business impact
# ---------------------------------------------------------------------------

SEVERITY_HIGH_KEYWORDS = [
    # Safety / data loss / bricking
    "安全", "隐私", "security", "privacy", "加密", "token",
    "断电", "power loss", "变砖", "brick",
    "数据丢失", "data loss", "擦除",
    # Core user flow
    "配网", "pairing", "绑定", "binding", "ota", "升级", "firmware",
    "开机", "boot", "启动",
]

SEVERITY_MEDIUM_KEYWORDS = [
    "同步", "sync", "状态", "state", "一致", "consistency",
    "恢复", "recovery", "重启", "reboot", "重连", "reconnect",
    "权限", "permission", "分享", "sharing",
    "远程", "remote", "云", "cloud",
    "语音", "voice", "唤醒", "wake",
    "异常", "exception", "错误", "error", "超时", "timeout",
]

SEVERITY_LOW_KEYWORDS = [
    "兼容", "compat", "ui", "显示", "display", "动画", "animation",
    "探索", "exploratory", "竞品", "benchmark",
    "日志", "log", "诊断", "diagnostic",
]

# ---------------------------------------------------------------------------
# Probability keyword signals (P dimension)
# Higher probability = more likely to have defects
# ---------------------------------------------------------------------------

PROBABILITY_HIGH_KEYWORDS = [
    "多端", "跨端", "cross-end", "multi-end",
    "并发", "concurrent", "竞争", "race",
    "状态机", "state machine", "状态转换", "state transition",
    "弱网", "weak network", "断网", "offline",
    "边界", "boundary", "极端", "extreme",
]

PROBABILITY_MEDIUM_KEYWORDS = [
    "参数", "parameter", "范围", "range", "默认", "default",
    "模式", "mode", "互斥", "exclusive",
    "定时", "timer", "计时", "schedule",
    "缓存", "cache", "持久化", "persist",
]

# ---------------------------------------------------------------------------
# Detectability keyword signals (D dimension)
# Higher detectability score = HARDER to detect (confusingly named in FMEA)
# ---------------------------------------------------------------------------

DETECT_HARD_KEYWORDS = [
    # Hard to detect = high D score
    "竞争", "race", "并发", "concurrent",
    "内存泄漏", "memory leak", "泄漏",
    "时序", "timing", "偶现", "intermittent",
    "累积", "accumulate", "漂移", "drift",
    "弱网", "weak network",
]

DETECT_MEDIUM_KEYWORDS = [
    "恢复", "recovery", "重启", "reboot",
    "断电", "power loss", "重连", "reconnect",
    "同步", "sync", "延迟", "latency", "delay",
    "降级", "degradation",
]


# ---------------------------------------------------------------------------
# Structural risk signals
# ---------------------------------------------------------------------------

def _keyword_score(title: str, high_kw: list, med_kw: list, low_kw: list | None = None,
                   high_val: float = 8.0, med_val: float = 5.0, low_val: float = 3.0,
                   base: float = 4.0) -> float:
    """Score a title by keyword matching. Returns highest matching tier."""
    lowered = title.lower()
    for kw in high_kw:
        if kw.lower() in lowered:
            return high_val
    for kw in med_kw:
        if kw.lower() in lowered:
            return med_val
    if low_kw:
        for kw in low_kw:
            if kw.lower() in lowered:
                return low_val
    return base


def _confidence_to_probability_boost(confidence: Optional[str]) -> float:
    """Low confidence → higher probability of defect."""
    if confidence == "low":
        return 2.0
    if confidence == "medium":
        return 1.0
    return 0.0


def _priority_to_severity_override(priority: Optional[str]) -> Optional[float]:
    """If the user already assigned a priority, map it to severity."""
    mapping = {"P0": 10.0, "P1": 8.0, "P2": 5.0, "P3": 3.0}
    return mapping.get(str(priority).upper()) if priority else None


def _is_shallow(node: Dict[str, Any]) -> bool:
    """A node that looks like it should have children but doesn't."""
    children = node.get("children", [])
    if children:
        return False
    title_lower = node.get("title", "").lower()
    shallow_hints = ["性能", "兼容", "稳定", "安全", "ui", "performance",
                     "compatibility", "stability", "security"]
    return any(h in title_lower for h in shallow_hints)


# ---------------------------------------------------------------------------
# Core scoring
# ---------------------------------------------------------------------------

@dataclass
class NodeRiskScore:
    title: str
    path: str
    severity: float
    probability: float
    detectability: float
    rpn: float
    priority_label: str  # P0/P1/P2/P3

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "path": self.path,
            "severity": round(self.severity, 1),
            "probability": round(self.probability, 1),
            "detectability": round(self.detectability, 1),
            "rpn": round(self.rpn, 1),
            "priority": self.priority_label,
        }


def rpn_to_priority(rpn: float) -> str:
    if rpn >= 300:
        return "P0"
    if rpn >= 150:
        return "P1"
    if rpn >= 60:
        return "P2"
    return "P3"


def score_node(node: Dict[str, Any], path: str) -> NodeRiskScore:
    title = node.get("title", "")

    # --- Severity ---
    sev_override = _priority_to_severity_override(node.get("priority"))
    if sev_override is not None:
        severity = sev_override
    else:
        severity = _keyword_score(
            title,
            SEVERITY_HIGH_KEYWORDS,
            SEVERITY_MEDIUM_KEYWORDS,
            SEVERITY_LOW_KEYWORDS,
            high_val=9.0, med_val=6.0, low_val=3.0, base=4.0,
        )

    # --- Probability ---
    probability = _keyword_score(
        title,
        PROBABILITY_HIGH_KEYWORDS,
        PROBABILITY_MEDIUM_KEYWORDS,
        high_val=8.0, med_val=5.0, base=3.0,
    )
    probability = min(10.0, probability + _confidence_to_probability_boost(node.get("confidence")))
    if _is_shallow(node):
        probability = min(10.0, probability + 2.0)

    # --- Detectability (higher = harder to detect) ---
    detectability = _keyword_score(
        title,
        DETECT_HARD_KEYWORDS,
        DETECT_MEDIUM_KEYWORDS,
        high_val=9.0, med_val=6.0, base=3.0,
    )

    rpn = severity * probability * detectability
    return NodeRiskScore(
        title=title,
        path=path,
        severity=severity,
        probability=probability,
        detectability=detectability,
        rpn=rpn,
        priority_label=rpn_to_priority(rpn),
    )


def score_tree(root: Dict[str, Any]) -> Tuple[List[NodeRiskScore], Dict[str, Any]]:
    """Score every node and return (scores_list, annotated_root_copy).

    The annotated copy has ``risk_score`` and auto-computed ``priority``
    written back onto each node (non-destructive copy).
    """
    scores: List[NodeRiskScore] = []

    def walk(node: Dict[str, Any], path_parts: List[str]) -> Dict[str, Any]:
        path = " / ".join(path_parts + [node["title"]])
        result = score_node(node, path)
        scores.append(result)

        # Build annotated copy
        annotated = dict(node)
        annotated["risk_score"] = round(result.rpn, 1)
        if not annotated.get("priority"):
            annotated["priority"] = result.priority_label
        annotated["children"] = [
            walk(child, path_parts + [node["title"]])
            for child in node.get("children", [])
        ]
        return annotated

    annotated_root = walk(root, [])
    scores.sort(key=lambda s: s.rpn, reverse=True)
    return scores, annotated_root


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------

@dataclass
class RiskReport:
    total_nodes: int
    p0_count: int
    p1_count: int
    p2_count: int
    p3_count: int
    top_risks: List[NodeRiskScore]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_nodes": self.total_nodes,
            "distribution": {
                "P0": self.p0_count,
                "P1": self.p1_count,
                "P2": self.p2_count,
                "P3": self.p3_count,
            },
            "top_risks": [s.to_dict() for s in self.top_risks],
        }


def build_report(scores: List[NodeRiskScore], top_n: int = 20) -> RiskReport:
    return RiskReport(
        total_nodes=len(scores),
        p0_count=sum(1 for s in scores if s.priority_label == "P0"),
        p1_count=sum(1 for s in scores if s.priority_label == "P1"),
        p2_count=sum(1 for s in scores if s.priority_label == "P2"),
        p3_count=sum(1 for s in scores if s.priority_label == "P3"),
        top_risks=scores[:top_n],
    )


def format_text_report(report: RiskReport) -> str:
    lines = [
        "=" * 60,
        "风险量化评估报告 (FMEA-style RPN)",
        "=" * 60,
        "",
        f"总节点数: {report.total_nodes}",
        f"优先级分布: P0={report.p0_count}  P1={report.p1_count}  P2={report.p2_count}  P3={report.p3_count}",
        "",
        "RPN = 严重度(S) × 发生概率(P) × 检测难度(D)",
        "  P0: RPN >= 300  |  P1: 150-299  |  P2: 60-149  |  P3: < 60",
        "",
        f"Top {len(report.top_risks)} 高风险节点:",
        "-" * 60,
    ]
    for i, s in enumerate(report.top_risks, 1):
        lines.append(
            f"  {i:2d}. [{s.priority_label}] RPN={s.rpn:6.1f}  "
            f"S={s.severity:.0f} P={s.probability:.0f} D={s.detectability:.0f}  "
            f"{s.title}"
        )
        lines.append(f"      路径: {s.path}")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute FMEA-style risk scores (RPN) for scope-tree nodes"
    )
    parser.add_argument("input", type=Path, help="scope tree (json or markdown)")
    parser.add_argument("--input-format", choices=("auto", "markdown", "json"), default="auto")
    parser.add_argument("--title", help="override tree title")
    parser.add_argument("--output", type=Path, help="write annotated tree with risk_score to this json file")
    parser.add_argument("--json-report", action="store_true", help="output risk report as JSON")
    parser.add_argument("--top", type=int, default=20, help="number of top risks to show (default: 20)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.input.exists():
        print(f"error: file not found: {args.input}", file=sys.stderr)
        return 1

    try:
        wrapper = load_tree_from_path(args.input, input_format=args.input_format, title_hint=args.title)
        wrapper = prepare_tree(wrapper)
    except ScopeTreeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    scores, annotated_root = score_tree(wrapper["root"])
    report = build_report(scores, top_n=args.top)

    # Output annotated tree if requested
    if args.output:
        wrapper["root"] = annotated_root
        save_json(wrapper, args.output)

    # Output report
    if args.json_report:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(format_text_report(report))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
