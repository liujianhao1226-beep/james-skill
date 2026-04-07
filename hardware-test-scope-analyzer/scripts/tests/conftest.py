"""Shared fixtures for hardware-test-scope-analyzer script tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from textwrap import dedent

import pytest

# Make the scripts directory importable
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


# ---------------------------------------------------------------------------
# Markdown fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_markdown() -> str:
    return dedent("""\
        # 智能台灯测试范围

        - 功能模块
          - 配网与连接
            - 正向流程
            - 异常流程
            - 重置与重绑
          - 本地交互
            - 旋钮控制
            - 触摸控制
        - 性能
          - 响应延迟
          - 长时间运行
        - 稳定性与恢复
          - 重启恢复
          - 断电恢复
        - 版本边界/待确认
          - 未来功能A
    """)


@pytest.fixture
def minimal_markdown() -> str:
    return dedent("""\
        - 根节点
          - 子节点A
          - 子节点B
    """)


@pytest.fixture
def tab_indented_markdown() -> str:
    return dedent("""\
        - 根节点
        \t- 子节点A
        \t\t- 孙节点
        \t- 子节点B
    """)


@pytest.fixture
def empty_markdown() -> str:
    return ""


@pytest.fixture
def no_bullet_markdown() -> str:
    return "just some text without bullet points\nanother line"


# ---------------------------------------------------------------------------
# JSON tree fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_json_tree() -> dict:
    return {
        "title": "智能台灯测试范围",
        "root": {
            "title": "智能台灯测试范围",
            "type": "root",
            "children": [
                {
                    "title": "功能模块",
                    "type": "module",
                    "children": [
                        {"title": "配网与连接", "children": []},
                        {"title": "本地交互", "children": []},
                    ],
                },
                {
                    "title": "性能",
                    "type": "quality",
                    "children": [
                        {"title": "响应延迟"},
                        {"title": "长时间运行"},
                    ],
                },
                {
                    "title": "稳定性与恢复",
                    "children": [
                        {"title": "重启恢复"},
                        {"title": "断电恢复"},
                    ],
                },
                {
                    "title": "版本边界/待确认",
                    "type": "boundary",
                    "children": [],
                },
            ],
        },
    }


@pytest.fixture
def minimal_tree() -> dict:
    return {
        "title": "test",
        "root": {
            "title": "test",
            "children": [{"title": "child"}],
        },
    }


@pytest.fixture
def deep_tree() -> dict:
    """A tree deeper than 6 levels to trigger depth warning."""
    node: dict = {"title": "leaf", "children": []}
    for i in range(7, 0, -1):
        node = {"title": f"level-{i}", "children": [node]}
    return {
        "title": "deep",
        "root": node,
    }


@pytest.fixture
def wide_tree() -> dict:
    """A node with >12 children to trigger flattening warning."""
    children = [{"title": f"child-{i}"} for i in range(15)]
    return {
        "title": "wide",
        "root": {
            "title": "wide",
            "children": children,
        },
    }


@pytest.fixture
def full_coverage_tree() -> dict:
    """A tree covering all 14 test domains for validate_scope_tree tests."""
    return {
        "title": "全覆盖测试范围",
        "root": {
            "title": "全覆盖测试范围",
            "type": "root",
            "children": [
                {"title": "核心功能与用户旅程", "children": [
                    {"title": "首次使用流程"},
                    {"title": "模式切换"},
                    {"title": "场景联动"},
                ]},
                {"title": "设备控制与硬件行为", "children": [
                    {"title": "电机控制"},
                    {"title": "传感器校准"},
                ]},
                {"title": "UI与人机交互", "children": [
                    {"title": "触控手势"},
                    {"title": "显示状态"},
                    {"title": "指示灯"},
                ]},
                {"title": "配网与连接", "children": [
                    {"title": "WiFi配网"},
                    {"title": "蓝牙连接"},
                ]},
                {"title": "App云端与账号", "children": [
                    {"title": "远程控制"},
                    {"title": "权限分享"},
                ]},
                {"title": "语音与AI能力", "children": [
                    {"title": "语音唤醒"},
                    {"title": "ASR识别"},
                    {"title": "TTS反馈"},
                ]},
                {"title": "数据同步与跨端一致性", "children": [
                    {"title": "状态同步"},
                    {"title": "跨端一致"},
                ]},
                {"title": "兼容性", "children": [
                    {"title": "机型兼容"},
                    {"title": "系统版本"},
                ]},
                {"title": "性能", "children": [
                    {"title": "响应延迟"},
                    {"title": "CPU内存"},
                ]},
                {"title": "稳定性与恢复", "children": [
                    {"title": "容错恢复"},
                    {"title": "看门狗"},
                ]},
                {"title": "OTA升级与诊断", "children": [
                    {"title": "固件升级"},
                    {"title": "日志诊断"},
                    {"title": "产测支持"},
                ]},
                {"title": "场景链路", "children": [
                    {"title": "端到端流程"},
                ]},
                {"title": "探索性测试", "children": [
                    {"title": "极端操作"},
                    {"title": "滥用场景"},
                ]},
                {"title": "安全与隐私", "children": [
                    {"title": "隐私保护"},
                    {"title": "权限控制"},
                    {"title": "数据加密与合规"},
                ]},
            ],
        },
    }


# ---------------------------------------------------------------------------
# File I/O helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def write_markdown(tmp_path):
    """Write markdown content to a temp .md file and return its path."""
    def _write(content: str, name: str = "outline.md") -> Path:
        p = tmp_path / name
        p.write_text(content, encoding="utf-8")
        return p
    return _write


@pytest.fixture
def write_json(tmp_path):
    """Write a dict as JSON to a temp .json file and return its path."""
    def _write(data: dict, name: str = "tree.json") -> Path:
        p = tmp_path / name
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return p
    return _write
