#!/usr/bin/env python3
"""Validate a scope tree against the 14 test-domain checklist.

Reports per-domain coverage status (covered / weak / missing) and an overall
coverage ratio.  Optionally fails with a non-zero exit code when the ratio is
below a configurable threshold (--strict).
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from scope_tree_lib import ScopeTreeError, iter_nodes, load_tree_from_path, prepare_tree

# ---------------------------------------------------------------------------
# Domain keyword registry — derived from references/test-domain-checklist.md
# Each domain maps to a set of Chinese + English keywords that indicate
# the domain is represented somewhere in the tree.
# ---------------------------------------------------------------------------

DOMAINS: Dict[str, List[str]] = {
    "核心功能与用户旅程": [
        "功能", "用户旅程", "模式", "场景", "首次使用", "首次", "开箱",
        "feature", "journey", "mode", "scene", "first use",
        "核心功能", "主功能", "日常使用",
    ],
    "设备控制与硬件行为": [
        "设备控制", "硬件", "传感", "电控", "校准", "电机", "风扇",
        "加热", "锁", "阀", "马达", "执行器", "输出通道",
        "device control", "hardware", "sensor", "calibration", "actuator",
        "debounce", "drift",
    ],
    "UI与人机交互": [
        "ui", "交互", "触控", "手势", "显示", "指示灯", "屏幕",
        "开机", "引导", "页面", "动画", "旋钮", "按键",
        "interaction", "display", "gesture", "indicator", "onboarding",
        "touch", "knob", "button",
    ],
    "配网与连接": [
        "配网", "连接", "wifi", "蓝牙", "bluetooth", "zigbee",
        "matter", "thread", "pairing", "provisioning", "binding",
        "配对", "绑定", "热点", "信号", "重连",
        "connectivity", "network",
    ],
    "App与云端": [
        "app", "云", "账号", "权限", "远程", "分享", "云端",
        "remote", "cloud", "account", "permission", "sharing",
        "家庭", "成员", "推送", "自动化",
    ],
    "语音与AI": [
        "语音", "唤醒", "asr", "tts", "nlu", "ai", "对话",
        "voice", "wake", "speech", "recognition", "dialogue",
        "远场", "抗噪", "误唤醒",
    ],
    "数据同步与一致性": [
        "同步", "sync", "一致", "状态", "跨端", "多端",
        "state", "consistency", "cross-end", "报告",
        "冲突", "刷新", "上报",
    ],
    "兼容性": [
        "兼容", "compat", "机型", "系统", "版本", "路由器",
        "compatibility", "router", "os", "screen size",
        "locale", "region", "时区", "ipv4", "ipv6",
    ],
    "性能": [
        "性能", "performance", "延迟", "响应", "cpu", "内存",
        "memory", "latency", "启动时间", "配网时间",
        "bandwidth", "功耗", "温度", "battery",
    ],
    "稳定性与恢复": [
        "稳定", "恢复", "recovery", "容错", "看门狗", "watchdog",
        "重启", "断电", "崩溃", "降级",
        "stability", "fault", "reboot", "power loss", "reconnect",
    ],
    "OTA与诊断": [
        "ota", "升级", "诊断", "日志", "产测", "固件",
        "firmware", "upgrade", "rollback", "diagnostic",
        "log", "factory test", "manufacturing", "traceability",
        "工厂", "老化", "校准追溯",
    ],
    "场景链路": [
        "场景链路", "端到端", "end-to-end", "链路", "全流程",
        "scenario chain", "e2e",
    ],
    "探索性测试": [
        "探索", "滥用", "极端", "abuse", "exploratory",
        "rapid", "混合控制", "矛盾", "boundary combination",
    ],
    "安全与隐私": [
        "安全", "隐私", "security", "privacy", "token",
        "加密", "合规", "compliance", "麦克风", "摄像头",
        "数据删除", "权限提示",
    ],
}

# Thresholds for classification
COVERED_THRESHOLD = 3   # >= 3 keyword hits → covered
WEAK_THRESHOLD = 1      # 1-2 hits → weak


@dataclass
class DomainResult:
    domain: str
    status: str  # "covered" | "weak" | "missing"
    hit_count: int
    matched_keywords: List[str] = field(default_factory=list)
    matched_nodes: List[str] = field(default_factory=list)


@dataclass
class ValidationReport:
    total_domains: int
    covered: int
    weak: int
    missing: int
    coverage_ratio: float
    domains: List[DomainResult] = field(default_factory=list)
    missing_domains: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_domains": self.total_domains,
            "covered": self.covered,
            "weak": self.weak,
            "missing": self.missing,
            "coverage_ratio": round(self.coverage_ratio, 4),
            "domains": [
                {
                    "domain": d.domain,
                    "status": d.status,
                    "hit_count": d.hit_count,
                    "matched_keywords": d.matched_keywords,
                    "matched_nodes": d.matched_nodes[:5],  # cap for readability
                }
                for d in self.domains
            ],
            "missing_domains": self.missing_domains,
        }


def validate_coverage(root: Dict[str, Any], domains: Optional[Dict[str, List[str]]] = None) -> ValidationReport:
    """Check how many of the 14 test domains are represented in the tree."""
    if domains is None:
        domains = DOMAINS

    # Collect all node titles lowered for matching
    node_titles: List[str] = []
    for node, _depth in iter_nodes(root):
        node_titles.append(node["title"])

    titles_lowered = [t.lower() for t in node_titles]

    results: List[DomainResult] = []
    covered_count = 0
    weak_count = 0
    missing_count = 0
    missing_list: List[str] = []

    for domain_name, keywords in domains.items():
        hit_count = 0
        matched_kw: List[str] = []
        matched_nd: List[str] = []

        for kw in keywords:
            kw_lower = kw.lower()
            for idx, title_lower in enumerate(titles_lowered):
                if kw_lower in title_lower:
                    hit_count += 1
                    if kw not in matched_kw:
                        matched_kw.append(kw)
                    if node_titles[idx] not in matched_nd:
                        matched_nd.append(node_titles[idx])
                    break  # one hit per keyword is enough

        if hit_count >= COVERED_THRESHOLD:
            status = "covered"
            covered_count += 1
        elif hit_count >= WEAK_THRESHOLD:
            status = "weak"
            weak_count += 1
        else:
            status = "missing"
            missing_count += 1
            missing_list.append(domain_name)

        results.append(DomainResult(
            domain=domain_name,
            status=status,
            hit_count=hit_count,
            matched_keywords=matched_kw,
            matched_nodes=matched_nd,
        ))

    total = len(domains)
    ratio = covered_count / total if total > 0 else 0.0

    return ValidationReport(
        total_domains=total,
        covered=covered_count,
        weak=weak_count,
        missing=missing_count,
        coverage_ratio=ratio,
        domains=results,
        missing_domains=missing_list,
    )


def format_text_report(report: ValidationReport) -> str:
    """Format a human-readable text report."""
    lines: List[str] = []
    lines.append("=" * 60)
    lines.append("测试领域覆盖度检查报告")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"总领域数: {report.total_domains}")
    lines.append(f"已覆盖 (covered): {report.covered}")
    lines.append(f"薄弱 (weak):      {report.weak}")
    lines.append(f"缺失 (missing):   {report.missing}")
    lines.append(f"覆盖率: {report.coverage_ratio:.1%}")
    lines.append("")

    for d in report.domains:
        icon = {"covered": "[OK]", "weak": "[!!]", "missing": "[XX]"}[d.status]
        lines.append(f"  {icon} {d.domain}: {d.status} ({d.hit_count} hits)")
        if d.matched_keywords:
            lines.append(f"       关键词: {', '.join(d.matched_keywords[:5])}")
        if d.matched_nodes:
            lines.append(f"       节点: {', '.join(d.matched_nodes[:3])}")

    if report.missing_domains:
        lines.append("")
        lines.append("建议补充以下领域:")
        for name in report.missing_domains:
            lines.append(f"  - {name}")

    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate scope tree coverage against test-domain checklist")
    parser.add_argument("input", type=Path, help="path to scope tree (json or markdown)")
    parser.add_argument("--input-format", choices=("auto", "markdown", "json"), default="auto")
    parser.add_argument("--title", help="override tree title")
    parser.add_argument("--threshold", type=float, default=0.7,
                        help="minimum coverage ratio for --strict mode (default: 0.7)")
    parser.add_argument("--json", action="store_true", help="output machine-readable JSON")
    parser.add_argument("--strict", action="store_true",
                        help="exit with code 1 if coverage ratio is below threshold")
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

    report = validate_coverage(wrapper["root"])

    if args.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(format_text_report(report))

    if args.strict and report.coverage_ratio < args.threshold:
        print(
            f"\nFAIL: coverage {report.coverage_ratio:.1%} < threshold {args.threshold:.1%}",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
