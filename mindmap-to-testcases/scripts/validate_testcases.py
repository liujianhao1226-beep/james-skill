#!/usr/bin/env python3
"""Validate structured test cases JSON before CSV/XLSX export.

Usage:
  python scripts/validate_testcases.py input.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

ALIAS_GROUPS = {
    "所属模块": ["所属模块", "module"],
    "用例标题": ["用例标题", "title"],
    "前置条件": ["前置条件", "preconditions"],
    "步骤": ["步骤", "steps"],
    "预期": ["预期", "expected"],
    "优先级": ["优先级", "priority"],
    "用例类型": ["用例类型", "case_type"],
    "适用阶段": ["适用阶段", "stage"],
}

ALLOWED_PRIORITIES = {"1", "2", "3", "P0", "P1", "P2", "p0", "p1", "p2"}
CASE_TYPE_ALIASES = {
    "功能测试": "功能测试",
    "异常测试": "异常测试",
    "边界测试": "边界测试",
    "场景测试": "场景测试",
    "functional": "功能测试",
    "abnormal": "异常测试",
    "boundary": "边界测试",
    "scenario": "场景测试",
}
PLACEHOLDER_RE = re.compile(r"\?{2,}|�")

# Generation trace patterns that should not appear in final deliverables.
TRACE_PATTERNS_RE = re.compile(
    r"导图映射|脑图展开|原路径|根据节点|按导图路径|满足导图要求|与脑图一致|覆盖导图中",
    re.IGNORECASE,
)

# Step text should start with an action verb (Chinese).
STEP_ACTION_VERBS = (
    "打开", "点击", "输入", "选择", "确认", "取消", "关闭", "连接", "断开",
    "重启", "复位", "插入", "拔出", "等待", "检查", "查看", "验证", "登录",
    "退出", "切换", "滑动", "长按", "双击", "拖动", "上传", "下载", "发送",
    "接收", "配置", "设置", "修改", "删除", "添加", "创建", "启动", "停止",
    "升级", "回退", "恢复", "备份", "导入", "导出", "扫描", "搜索", "发现",
    "绑定", "解绑", "配网", "唤醒", "下发", "触发", "开启", "关掉",
    "将", "在", "使用", "通过", "进入", "执行", "操作", "观察",
    "HAC", "AP", "App", "app",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate structured JSON test cases")
    parser.add_argument("input", help="Path to JSON file")
    return parser.parse_args()


def load_cases(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(data, list):
        cases = data
    elif isinstance(data, dict) and isinstance(data.get("cases"), list):
        cases = data["cases"]
    else:
        raise ValueError("input JSON must be a list or an object with a 'cases' list")
    if not all(isinstance(item, dict) for item in cases):
        raise ValueError("each case must be a JSON object")
    return cases


def get_value(case: Dict[str, Any], canonical: str) -> Any:
    for key in ALIAS_GROUPS[canonical]:
        if key in case:
            return case[key]
    return None


def is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list):
        return len([item for item in value if str(item).strip()]) == 0
    return not str(value).strip()


def count_items(value: Any) -> int:
    if isinstance(value, list):
        return len([item for item in value if str(item).strip()])
    if isinstance(value, str):
        return len([line for line in value.splitlines() if line.strip()])
    return 1 if not is_empty(value) else 0


def iter_text_chunks(value: Any) -> Iterable[tuple[int | None, str]]:
    if isinstance(value, list):
        for index, item in enumerate(value, start=1):
            text = str(item).strip()
            if text:
                yield index, text
        return

    text = str(value).strip()
    if not text:
        return

    if isinstance(value, str) and "\n" in value:
        for index, line in enumerate(value.splitlines(), start=1):
            cleaned = line.strip()
            if cleaned:
                yield index, cleaned
        return

    yield None, text


def contains_suspicious_placeholder(text: str) -> bool:
    if not text:
        return False
    if PLACEHOLDER_RE.search(text):
        return True

    question_count = text.count("?")
    if question_count >= 3:
        return True
    if question_count >= 2 and question_count / max(len(text), 1) >= 0.2:
        return True
    return False


def validate_text_field(case: Dict[str, Any], index: int, field: str) -> List[str]:
    value = get_value(case, field)
    errors: List[str] = []
    for item_index, text in iter_text_chunks(value):
        if contains_suspicious_placeholder(text):
            location = f"{field}[{item_index}]" if item_index is not None else field
            preview = text[:40]
            errors.append(f"case {index}: field '{location}' contains suspicious placeholder or garbled text: {preview!r}")
    return errors


def validate_case(case: Dict[str, Any], index: int) -> List[str]:
    errors: List[str] = []
    warnings: List[str] = []
    for field in ALIAS_GROUPS:
        value = get_value(case, field)
        if is_empty(value):
            errors.append(f"case {index}: missing required field '{field}'")

    module = get_value(case, "所属模块")
    if isinstance(module, str) and module.strip() and not module.strip().startswith("/"):
        errors.append(f"case {index}: 所属模块 should start with '/'")

    priority = get_value(case, "优先级")
    if priority is not None and str(priority).strip() and str(priority).strip() not in ALLOWED_PRIORITIES:
        errors.append(f"case {index}: unsupported priority '{priority}'")

    case_type = get_value(case, "用例类型")
    if case_type is not None and str(case_type).strip() and str(case_type).strip() not in CASE_TYPE_ALIASES:
        errors.append(f"case {index}: unsupported case type '{case_type}'")

    steps = get_value(case, "步骤")
    step_count = count_items(steps)
    if step_count < 1:
        errors.append(f"case {index}: 步骤 should contain at least 1 actionable item")
    elif step_count > 15:
        warnings.append(f"case {index}: 步骤 has {step_count} items, consider splitting into multiple cases")

    # Check that steps start with action verbs (warn, not error).
    for item_index, step_text in iter_text_chunks(steps):
        cleaned = re.sub(r"^\d+\.\s*", "", step_text).strip()
        if cleaned and not any(cleaned.startswith(verb) for verb in STEP_ACTION_VERBS):
            warnings.append(f"case {index}: 步骤[{item_index}] may not start with an action verb: {cleaned[:30]!r}")

    expected = get_value(case, "预期")
    if count_items(expected) < 1:
        errors.append(f"case {index}: 预期 should contain at least 1 observable result")

    title = get_value(case, "用例标题")
    if isinstance(title, str):
        title_text = title.strip()
        if len(title_text) > 120:
            errors.append(f"case {index}: 用例标题 is too long (>120 chars)")
        # Expanded result-oriented outcome keywords for IoT domain.
        result_keywords = (
            "-", "成功", "失败", "不支持", "正常", "异常", "生效", "不生效",
            "同步", "恢复", "保留", "丢失", "响应", "无响应", "显示", "不显示",
            "上线", "离线", "超时", "中断", "一致", "不一致", "崩溃", "闪烁",
            "可控制", "不可控制", "可上网", "不可上网",
        )
        if not any(kw in title_text for kw in result_keywords):
            warnings.append(f"case {index}: 用例标题 should usually include a result-oriented outcome")
        # Check for generation trace patterns in title.
        if TRACE_PATTERNS_RE.search(title_text):
            errors.append(f"case {index}: 用例标题 contains generation trace text that should be removed")

    # Check for generation traces in steps and expected.
    for field in ("步骤", "预期"):
        for item_index, text in iter_text_chunks(get_value(case, field)):
            if TRACE_PATTERNS_RE.search(text):
                location = f"{field}[{item_index}]" if item_index is not None else field
                errors.append(f"case {index}: {location} contains generation trace text: {text[:40]!r}")

    # Check preconditions don't contain action verbs (they should be static conditions).
    preconditions = get_value(case, "前置条件")
    action_in_precondition = ("点击", "输入", "滑动", "下发", "发起", "执行操作")
    for item_index, text in iter_text_chunks(preconditions):
        cleaned = re.sub(r"^\d+\.\s*", "", text).strip()
        if cleaned and any(cleaned.startswith(verb) for verb in action_in_precondition):
            warnings.append(f"case {index}: 前置条件[{item_index}] looks like an action step, not a precondition: {cleaned[:30]!r}")

    for field in ("所属模块", "用例标题", "前置条件", "步骤", "预期", "适用阶段"):
        errors.extend(validate_text_field(case, index, field))

    return errors + warnings


def main() -> None:
    args = parse_args()
    cases = load_cases(Path(args.input))

    errors: List[str] = []
    unique_keys: Dict[str, int] = {}
    for index, case in enumerate(cases, start=1):
        errors.extend(validate_case(case, index))
        module = str(get_value(case, "所属模块") or "").strip()
        title = str(get_value(case, "用例标题") or "").strip()
        key = f"{module}||{title}"
        if module and title:
            unique_keys[key] = unique_keys.get(key, 0) + 1

    for key, count in unique_keys.items():
        if count > 1:
            module, title = key.split("||", 1)
            errors.append(f"duplicate case detected under {module}: {title}")

    if errors:
        print("Validation failed:")
        for item in errors:
            print(f"- {item}")
        sys.exit(1)

    print(f"Validation passed: {len(cases)} case(s)")


if __name__ == "__main__":
    main()
