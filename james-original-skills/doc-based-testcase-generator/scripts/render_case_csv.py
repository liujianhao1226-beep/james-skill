#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path
from typing import Optional


DEFAULT_HEADER = [
    "用例编号",
    "需求编号",
    "功能模块",
    "功能类型",
    "用例标题",
    "前置条件",
    "操作步骤",
    "预期结果",
    "自动化标识",
    "优先级",
    "测试结果",
    "备注",
    "测试人员",
    "测试日期",
    "缺陷编号",
    "适用范围",
]

FUNC = "功能"
COMPAT = "兼容性"
PERF = "性能"
NO = "否"


def parse_cases(text: str):
    module = None
    submodule = None
    title = None
    bullets = []
    rows = []

    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("# "):
            continue
        if line.startswith("## "):
            module = line[3:].strip()
            submodule = None
            title = None
            bullets = []
            continue
        if line.startswith("### "):
            submodule = line[4:].strip()
            title = None
            bullets = []
            continue
        if line.startswith("#### "):
            if title:
                rows.append((module, submodule, title, bullets[:]))
            title = line[5:].strip()
            bullets = []
            continue
        if line.startswith("- "):
            bullets.append(line[2:].strip())

    if title:
        rows.append((module, submodule, title, bullets[:]))
    return rows


def trim_label(value: str) -> str:
    pos = value.find("：")
    return value[pos + 1 :].strip() if pos != -1 else value.strip()


def load_header(template: Optional[Path]):
    if template is None:
        return DEFAULT_HEADER
    with template.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        return next(reader)


def classify_case(module: str, submodule: Optional[str], title: str):
    text = " ".join(filter(None, [module, submodule or "", title]))
    if any(token in text for token in ["兼容", "协议", "信道", "SSID", "Wi-Fi"]):
        return COMPAT
    if any(token in text for token in ["性能", "耗时", "压测", "长稳", "稳定性"]):
        return PERF
    return FUNC


def priority_for(module: str, title: str):
    if any(token in module for token in ["AI 语音", "设备添加与配网", "灯控与模式逻辑", "App 控制与跨端同步"]):
        if not any(token in title for token in ["异常", "失败", "超时", "兼容", "断网", "断电", "弱网"]):
            return "P0"
    if any(token in title for token in ["异常", "失败", "超时", "兼容", "断网", "断电", "弱网", "压测", "长时间"]):
        return "P1"
    return "P2"


def render_rows(cases, header, id_prefix):
    for index, (module, submodule, title, bullets) in enumerate(cases, start=1):
        pre = trim_label(bullets[0]) if len(bullets) > 0 else ""
        steps = trim_label(bullets[1]) if len(bullets) > 1 else ""
        expected = trim_label(bullets[2]) if len(bullets) > 2 else ""
        feature_module = module if not submodule else f"{module}-{submodule}"
        row = [""] * len(header)
        mapping = {
            "用例编号": f"{id_prefix}-{index:03d}",
            "需求编号": "",
            "功能模块": feature_module,
            "功能类型": classify_case(module or "", submodule, title),
            "用例标题": title,
            "前置条件": pre,
            "操作步骤": steps,
            "预期结果": expected,
            "自动化标识": NO,
            "优先级": priority_for(module or "", title),
            "测试结果": "",
            "备注": "",
            "测试人员": "",
            "测试日期": "",
            "缺陷编号": "",
            "适用范围": "",
        }
        for idx, name in enumerate(header):
            row[idx] = mapping.get(name, "")
        yield row


def main() -> int:
    parser = argparse.ArgumentParser(description="Render normalized testcase markdown to CSV using a template header.")
    parser.add_argument("--input", required=True, help="Heading-based testcase markdown")
    parser.add_argument("--output", required=True, help="Output CSV path")
    parser.add_argument("--template", help="Optional CSV template path")
    parser.add_argument("--id-prefix", default="TC", help="Case ID prefix")
    args = parser.parse_args()

    src = Path(args.input)
    dst = Path(args.output)
    template = Path(args.template) if args.template else None

    cases = parse_cases(src.read_text(encoding="utf-8"))
    header = load_header(template)

    with dst.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in render_rows(cases, header, args.id_prefix):
            writer.writerow(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
