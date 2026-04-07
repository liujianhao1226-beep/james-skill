"""Tests for risk_scorer.py — FMEA-style RPN risk scoring."""

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
from risk_scorer import (
    NodeRiskScore,
    RiskReport,
    build_report,
    format_text_report,
    rpn_to_priority,
    score_node,
    score_tree,
)

# Reuse _build_notes_plain from export_xmind for the notes test
from export_xmind import _build_notes_plain as export_build_notes

RISK_SCRIPT = SCRIPTS_DIR / "risk_scorer.py"


def run_scorer(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(RISK_SCRIPT)] + args,
        capture_output=True,
        text=True,
        cwd=SCRIPTS_DIR,
    )


# ===== rpn_to_priority =====

class TestRpnToPriority:
    def test_p0(self):
        assert rpn_to_priority(300) == "P0"
        assert rpn_to_priority(1000) == "P0"

    def test_p1(self):
        assert rpn_to_priority(150) == "P1"
        assert rpn_to_priority(299) == "P1"

    def test_p2(self):
        assert rpn_to_priority(60) == "P2"
        assert rpn_to_priority(149) == "P2"

    def test_p3(self):
        assert rpn_to_priority(59) == "P3"
        assert rpn_to_priority(1) == "P3"


# ===== score_node =====

class TestScoreNode:
    def test_security_node_high_severity(self):
        node = normalize_node({"title": "安全与隐私", "children": []})
        result = score_node(node, "root / 安全与隐私")
        assert result.severity >= 8.0

    def test_ui_node_low_severity(self):
        node = normalize_node({"title": "UI显示效果", "children": []})
        result = score_node(node, "root / UI显示效果")
        assert result.severity <= 4.0

    def test_concurrent_high_probability(self):
        node = normalize_node({"title": "多端并发控制", "children": []})
        result = score_node(node, "root / 多端并发控制")
        assert result.probability >= 7.0

    def test_race_condition_hard_detect(self):
        node = normalize_node({"title": "竞争条件与时序问题", "children": []})
        result = score_node(node, "root / 竞争条件与时序问题")
        assert result.detectability >= 8.0

    def test_priority_override_severity(self):
        node = normalize_node({"title": "普通功能", "priority": "P0", "children": []})
        result = score_node(node, "root / 普通功能")
        assert result.severity == 10.0

    def test_low_confidence_boosts_probability(self):
        base = normalize_node({"title": "测试点", "children": []})
        low_conf = normalize_node({"title": "测试点", "confidence": "low", "children": []})
        base_score = score_node(base, "root / 测试点")
        low_score = score_node(low_conf, "root / 测试点")
        assert low_score.probability > base_score.probability

    def test_shallow_node_boosts_probability(self):
        """A node named '性能' with no children should get boosted probability."""
        shallow = normalize_node({"title": "性能", "children": []})
        result = score_node(shallow, "root / 性能")
        assert result.probability >= 5.0

    def test_rpn_calculated(self):
        node = normalize_node({"title": "配网断电恢复并发", "children": []})
        result = score_node(node, "root / test")
        assert result.rpn == result.severity * result.probability * result.detectability

    def test_priority_label_matches_rpn(self):
        node = normalize_node({"title": "简单节点", "children": []})
        result = score_node(node, "root / 简单节点")
        assert result.priority_label == rpn_to_priority(result.rpn)


# ===== score_tree =====

class TestScoreTree:
    def test_scores_all_nodes(self, sample_json_tree):
        wrapper = prepare_tree(sample_json_tree)
        scores, annotated = score_tree(wrapper["root"])
        # Should have a score for every node
        node_count = wrapper["stats"]["node_count"]
        assert len(scores) == node_count

    def test_annotated_tree_has_risk_score(self, sample_json_tree):
        wrapper = prepare_tree(sample_json_tree)
        _, annotated = score_tree(wrapper["root"])
        assert "risk_score" in annotated
        assert "priority" in annotated
        for child in annotated["children"]:
            assert "risk_score" in child

    def test_scores_sorted_descending(self, sample_json_tree):
        wrapper = prepare_tree(sample_json_tree)
        scores, _ = score_tree(wrapper["root"])
        for i in range(len(scores) - 1):
            assert scores[i].rpn >= scores[i + 1].rpn

    def test_security_ranks_higher_than_ui(self):
        tree = normalize_node({
            "title": "root",
            "children": [
                {"title": "安全与加密"},
                {"title": "UI动画效果"},
            ],
        })
        scores, _ = score_tree(tree)
        security_score = next(s for s in scores if "安全" in s.title)
        ui_score = next(s for s in scores if "UI" in s.title)
        assert security_score.rpn > ui_score.rpn


# ===== build_report =====

class TestBuildReport:
    def test_distribution(self, sample_json_tree):
        wrapper = prepare_tree(sample_json_tree)
        scores, _ = score_tree(wrapper["root"])
        report = build_report(scores, top_n=5)
        assert report.total_nodes == len(scores)
        assert report.p0_count + report.p1_count + report.p2_count + report.p3_count == report.total_nodes
        assert len(report.top_risks) <= 5

    def test_to_dict(self, sample_json_tree):
        wrapper = prepare_tree(sample_json_tree)
        scores, _ = score_tree(wrapper["root"])
        report = build_report(scores)
        d = report.to_dict()
        assert "distribution" in d
        assert "top_risks" in d
        assert d["distribution"]["P0"] == report.p0_count


# ===== format_text_report =====

class TestFormatTextReport:
    def test_contains_key_sections(self, sample_json_tree):
        wrapper = prepare_tree(sample_json_tree)
        scores, _ = score_tree(wrapper["root"])
        report = build_report(scores)
        text = format_text_report(report)
        assert "风险量化评估报告" in text
        assert "RPN" in text
        assert "P0" in text or "P1" in text or "P2" in text or "P3" in text


# ===== export_xmind notes integration =====

class TestExportNotes:
    def test_notes_with_metadata(self):
        node = {
            "title": "test",
            "note": "Some note",
            "priority": "P1",
            "test_type": ["functional", "performance"],
            "automation_hint": "auto",
            "risk_score": 180.0,
            "source_refs": ["PRD-1", "API-2"],
        }
        notes = export_build_notes(node)
        assert "Some note" in notes
        assert "优先级: P1" in notes
        assert "测试类型: functional, performance" in notes
        assert "自动化建议: auto" in notes
        assert "风险分: 180.0" in notes
        assert "依据: PRD-1, API-2" in notes

    def test_notes_empty_when_no_metadata(self):
        node = {"title": "bare"}
        notes = export_build_notes(node)
        assert notes == ""

    def test_notes_partial(self):
        node = {"title": "test", "priority": "P0"}
        notes = export_build_notes(node)
        assert "优先级: P0" in notes
        assert "测试类型" not in notes


# ===== CLI integration =====

class TestRiskScorerCLI:
    def test_text_output(self, write_json, sample_json_tree):
        path = write_json(sample_json_tree)
        result = run_scorer([str(path)])
        assert result.returncode == 0
        assert "风险量化评估报告" in result.stdout

    def test_json_report(self, write_json, sample_json_tree):
        path = write_json(sample_json_tree)
        result = run_scorer([str(path), "--json-report"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "distribution" in data
        assert "top_risks" in data

    def test_output_annotated_tree(self, write_json, sample_json_tree, tmp_path):
        path = write_json(sample_json_tree)
        outpath = tmp_path / "scored.json"
        result = run_scorer([str(path), "--output", str(outpath)])
        assert result.returncode == 0
        assert outpath.exists()
        scored = json.loads(outpath.read_text(encoding="utf-8"))
        assert "risk_score" in scored["root"]

    def test_top_flag(self, write_json, sample_json_tree):
        path = write_json(sample_json_tree)
        result = run_scorer([str(path), "--json-report", "--top", "3"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data["top_risks"]) <= 3

    def test_file_not_found(self, tmp_path):
        result = run_scorer([str(tmp_path / "nope.json")])
        assert result.returncode == 1

    def test_markdown_input(self, write_markdown, sample_markdown):
        path = write_markdown(sample_markdown)
        result = run_scorer([str(path), "--json-report"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["total_nodes"] > 0
