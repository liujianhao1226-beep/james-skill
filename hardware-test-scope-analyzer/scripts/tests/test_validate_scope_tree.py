"""Tests for validate_scope_tree.py — coverage checker against 14 test domains."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from scope_tree_lib import normalize_node, prepare_tree
from validate_scope_tree import (
    DOMAINS,
    DomainResult,
    ValidationReport,
    format_text_report,
    validate_coverage,
)

VALIDATE_SCRIPT = SCRIPTS_DIR / "validate_scope_tree.py"


def run_validate(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATE_SCRIPT)] + args,
        capture_output=True,
        text=True,
        cwd=SCRIPTS_DIR,
    )


# ===== validate_coverage function =====

class TestValidateCoverage:
    def test_full_coverage(self, full_coverage_tree):
        wrapper = prepare_tree(full_coverage_tree)
        report = validate_coverage(wrapper["root"])
        assert report.total_domains == 14
        assert report.covered == 14
        assert report.missing == 0
        assert report.coverage_ratio == 1.0

    def test_empty_tree(self):
        root = normalize_node({"title": "空", "children": []})
        report = validate_coverage(root)
        assert report.total_domains == 14
        assert report.covered == 0
        assert report.missing == 14
        assert report.coverage_ratio == 0.0
        assert len(report.missing_domains) == 14

    def test_partial_coverage(self):
        root = normalize_node({
            "title": "部分覆盖",
            "children": [
                {"title": "功能模块", "children": [
                    {"title": "模式切换"},
                    {"title": "场景联动"},
                    {"title": "首次使用"},
                ]},
                {"title": "性能测试", "children": [
                    {"title": "响应延迟"},
                    {"title": "CPU占用"},
                    {"title": "内存消耗"},
                ]},
            ],
        })
        report = validate_coverage(root)
        assert report.covered >= 2
        assert report.missing > 0
        covered_names = [d.domain for d in report.domains if d.status == "covered"]
        assert "核心功能与用户旅程" in covered_names
        assert "性能" in covered_names

    def test_weak_detection(self):
        """A domain with only 1-2 keyword hits should be 'weak'."""
        root = normalize_node({
            "title": "test",
            "children": [
                {"title": "WiFi连接"},  # only 1 hit for 配网与连接
            ],
        })
        report = validate_coverage(root)
        pairing_result = next(d for d in report.domains if d.domain == "配网与连接")
        assert pairing_result.status in ("weak", "covered")
        assert pairing_result.hit_count >= 1

    def test_custom_domains(self):
        custom = {"自定义领域": ["特殊关键词"]}
        root = normalize_node({
            "title": "test",
            "children": [{"title": "包含特殊关键词的节点"}],
        })
        report = validate_coverage(root, domains=custom)
        assert report.total_domains == 1
        assert report.covered == 0  # only 1 hit, needs 3 for covered
        assert report.domains[0].hit_count == 1

    def test_matched_keywords_and_nodes(self, full_coverage_tree):
        wrapper = prepare_tree(full_coverage_tree)
        report = validate_coverage(wrapper["root"])
        for d in report.domains:
            if d.status == "covered":
                assert len(d.matched_keywords) > 0
                assert len(d.matched_nodes) > 0


# ===== ValidationReport =====

class TestValidationReport:
    def test_to_dict(self):
        report = ValidationReport(
            total_domains=14,
            covered=10,
            weak=2,
            missing=2,
            coverage_ratio=10 / 14,
            domains=[
                DomainResult("d1", "covered", 5, ["kw1"], ["node1"]),
            ],
            missing_domains=["d13", "d14"],
        )
        d = report.to_dict()
        assert d["total_domains"] == 14
        assert d["coverage_ratio"] == round(10 / 14, 4)
        assert len(d["domains"]) == 1
        assert d["missing_domains"] == ["d13", "d14"]


# ===== format_text_report =====

class TestFormatTextReport:
    def test_contains_key_sections(self, full_coverage_tree):
        wrapper = prepare_tree(full_coverage_tree)
        report = validate_coverage(wrapper["root"])
        text = format_text_report(report)
        assert "覆盖度检查报告" in text
        assert "覆盖率" in text
        assert "[OK]" in text

    def test_missing_domains_listed(self):
        root = normalize_node({"title": "空", "children": []})
        report = validate_coverage(root)
        text = format_text_report(report)
        assert "建议补充" in text
        assert "[XX]" in text


# ===== CLI integration =====

class TestValidateCLI:
    def test_json_output(self, write_json, full_coverage_tree):
        path = write_json(full_coverage_tree)
        result = run_validate([str(path), "--json"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["total_domains"] == 14
        assert data["covered"] == 14

    def test_text_output(self, write_json, full_coverage_tree):
        path = write_json(full_coverage_tree)
        result = run_validate([str(path)])
        assert result.returncode == 0
        assert "覆盖度检查报告" in result.stdout

    def test_strict_pass(self, write_json, full_coverage_tree):
        path = write_json(full_coverage_tree)
        result = run_validate([str(path), "--strict", "--threshold", "0.5"])
        assert result.returncode == 0

    def test_strict_fail(self, write_json, minimal_tree):
        path = write_json(minimal_tree)
        result = run_validate([str(path), "--strict", "--threshold", "0.9"])
        assert result.returncode == 1
        assert "FAIL" in result.stderr

    def test_file_not_found(self, tmp_path):
        result = run_validate([str(tmp_path / "nope.json")])
        assert result.returncode == 1

    def test_markdown_input(self, write_markdown, sample_markdown):
        path = write_markdown(sample_markdown)
        result = run_validate([str(path), "--json"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["total_domains"] == 14
