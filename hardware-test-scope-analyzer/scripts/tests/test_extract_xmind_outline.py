"""Tests for extract_xmind_outline.py — XMind extraction and rendering."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pytest

import sys
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from extract_xmind_outline import (
    iter_child_topics,
    iter_summary_topics,
    load_sheets,
    load_xmind_json,
    load_xmind_xml,
    normalize_sheet_container,
    render_json_outline,
    render_markdown,
    render_topic_markdown,
    topic_title,
)


# ===== normalize_sheet_container =====

class TestNormalizeSheetContainer:
    def test_list_input(self):
        data = [{"title": "sheet1"}, {"title": "sheet2"}]
        result = normalize_sheet_container(data)
        assert len(result) == 2

    def test_list_filters_non_dicts(self):
        data = [{"title": "ok"}, "bad", 42]
        result = normalize_sheet_container(data)
        assert len(result) == 1

    def test_dict_with_rootTopic(self):
        data = {"rootTopic": {"title": "root"}}
        result = normalize_sheet_container(data)
        assert len(result) == 1
        assert result[0] == data

    def test_dict_with_sheets_key(self):
        data = {"sheets": [{"title": "s1"}, {"title": "s2"}]}
        result = normalize_sheet_container(data)
        assert len(result) == 2

    def test_dict_with_worksheets_key(self):
        data = {"worksheets": [{"title": "w1"}]}
        result = normalize_sheet_container(data)
        assert len(result) == 1

    def test_non_dict_input(self):
        assert normalize_sheet_container("string") == []
        assert normalize_sheet_container(42) == []

    def test_empty_dict(self):
        assert normalize_sheet_container({}) == []


# ===== topic_title =====

class TestTopicTitle:
    def test_normal(self):
        assert topic_title({"title": "hello"}) == "hello"

    def test_whitespace_collapsed(self):
        assert topic_title({"title": "  hello   world  "}) == "hello world"

    def test_missing_title(self):
        assert topic_title({}) == "[untitled]"

    def test_empty_title(self):
        assert topic_title({"title": "   "}) == "[untitled]"

    def test_non_string_title(self):
        assert topic_title({"title": 42}) == "[untitled]"


# ===== iter_child_topics =====

class TestIterChildTopics:
    def test_attached(self):
        topic = {"children": {"attached": [{"title": "a"}, {"title": "b"}]}}
        children = list(iter_child_topics(topic))
        assert len(children) == 2

    def test_topics_key(self):
        topic = {"children": {"topics": [{"title": "a"}]}}
        children = list(iter_child_topics(topic))
        assert len(children) == 1

    def test_detached(self):
        topic = {"children": {"detached": [{"title": "d"}]}}
        children = list(iter_child_topics(topic))
        assert len(children) == 1

    def test_mixed_dedup_by_id(self):
        topic = {
            "children": {
                "attached": [{"id": "1", "title": "a"}],
                "topics": [{"id": "1", "title": "a"}, {"id": "2", "title": "b"}],
            }
        }
        children = list(iter_child_topics(topic))
        titles = [c["title"] for c in children]
        assert titles.count("a") == 1
        assert "b" in titles

    def test_no_children(self):
        assert list(iter_child_topics({"title": "leaf"})) == []

    def test_children_not_dict(self):
        assert list(iter_child_topics({"children": "bad"})) == []

    def test_unknown_keys_explored(self):
        topic = {"children": {"custom_key": [{"title": "found"}]}}
        children = list(iter_child_topics(topic))
        assert len(children) == 1


# ===== iter_summary_topics =====

class TestIterSummaryTopics:
    def test_with_summary(self):
        topic = {"children": {"summary": [{"title": "sum1"}]}}
        summaries = list(iter_summary_topics(topic))
        assert len(summaries) == 1

    def test_no_summary(self):
        topic = {"children": {"attached": [{"title": "a"}]}}
        assert list(iter_summary_topics(topic)) == []

    def test_no_children(self):
        assert list(iter_summary_topics({})) == []


# ===== render_topic_markdown =====

class TestRenderTopicMarkdown:
    def test_basic(self):
        topic = {
            "title": "root",
            "children": {
                "attached": [
                    {"title": "child1"},
                    {"title": "child2"},
                ],
            },
        }
        lines = render_topic_markdown(topic, 0, include_summaries=False)
        assert lines[0] == "- root"
        assert lines[1] == "  - child1"
        assert lines[2] == "  - child2"

    def test_depth_indentation(self):
        topic = {"title": "deep"}
        lines = render_topic_markdown(topic, 3, include_summaries=False)
        assert lines[0] == "      - deep"

    def test_summary_included(self):
        topic = {
            "title": "root",
            "children": {
                "attached": [{"title": "child"}],
                "summary": [{"title": "my summary"}],
            },
        }
        lines = render_topic_markdown(topic, 0, include_summaries=True)
        summary_lines = [l for l in lines if "summary" in l.lower()]
        assert len(summary_lines) == 1


# ===== render_json_outline =====

class TestRenderJsonOutline:
    def test_basic_structure(self):
        topic = {
            "title": "root",
            "children": {
                "attached": [{"title": "a"}, {"title": "b"}],
            },
        }
        result = render_json_outline(topic, include_summaries=False)
        assert result["title"] == "root"
        assert len(result["children"]) == 2

    def test_summaries_included(self):
        topic = {
            "title": "root",
            "children": {
                "attached": [],
                "summary": [{"title": "s1"}],
            },
        }
        result = render_json_outline(topic, include_summaries=True)
        assert result["summaries"] == ["s1"]

    def test_summaries_excluded(self):
        topic = {
            "title": "root",
            "children": {
                "summary": [{"title": "s1"}],
            },
        }
        result = render_json_outline(topic, include_summaries=False)
        assert "summaries" not in result


# ===== XML format xmind =====

class TestLoadXmindXml:
    def _make_xml_xmind(self, tmp_path: Path) -> Path:
        """Create a minimal XMind 8 style .xmind with content.xml."""
        ns = "urn:xmind:xmap:xmlns:content:2.0"
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<xmap-content xmlns="{ns}">
  <sheet id="s1">
    <title>Sheet1</title>
    <topic id="t1">
      <title>Root</title>
      <children>
        <topics type="attached">
          <topic id="t2"><title>Child A</title></topic>
          <topic id="t3"><title>Child B</title></topic>
        </topics>
      </children>
    </topic>
  </sheet>
</xmap-content>"""
        path = tmp_path / "legacy.xmind"
        with zipfile.ZipFile(path, "w") as zf:
            zf.writestr("content.xml", xml_content)
        return path

    def test_xml_extraction(self, tmp_path):
        path = self._make_xml_xmind(tmp_path)
        sheets = load_sheets(path)
        assert len(sheets) == 1
        root = sheets[0]["rootTopic"]
        assert root["title"] == "Root"
        children = root["children"]["attached"]
        assert len(children) == 2

    def test_malformed_xml_no_crash(self, tmp_path):
        path = tmp_path / "bad.xmind"
        with zipfile.ZipFile(path, "w") as zf:
            zf.writestr("content.xml", "<not valid xml!!!>>>>>")
        with zipfile.ZipFile(path) as zf:
            result = load_xmind_xml(zf)
            assert result == []


# ===== load_sheets =====

class TestLoadSheets:
    def test_json_xmind(self, sample_json_tree, tmp_path):
        from export_xmind import write_xmind
        from scope_tree_lib import prepare_tree

        wrapper = prepare_tree(sample_json_tree)
        xmind_path = tmp_path / "test.xmind"
        write_xmind(wrapper, xmind_path)

        sheets = load_sheets(xmind_path)
        assert len(sheets) >= 1

    def test_unsupported_raises(self, tmp_path):
        path = tmp_path / "empty.xmind"
        with zipfile.ZipFile(path, "w") as zf:
            zf.writestr("random.txt", "nothing")
        with pytest.raises(ValueError, match="unsupported"):
            load_sheets(path)


# ===== render_markdown =====

class TestRenderMarkdown:
    def test_single_sheet(self):
        sheets = [{
            "title": "Sheet1",
            "rootTopic": {
                "title": "Root",
                "children": {"attached": [{"title": "A"}]},
            },
        }]
        md = render_markdown(sheets, include_summaries=False)
        assert "- Root" in md
        assert "  - A" in md

    def test_multiple_sheets(self):
        sheets = [
            {"title": "S1", "rootTopic": {"title": "R1"}},
            {"title": "S2", "rootTopic": {"title": "R2"}},
        ]
        md = render_markdown(sheets, include_summaries=False)
        assert "# Sheet: S1" in md
        assert "# Sheet: S2" in md
        assert "- R1" in md
        assert "- R2" in md

    def test_no_rootTopic_skipped(self):
        sheets = [{"title": "bad"}]
        md = render_markdown(sheets, include_summaries=False)
        assert md == ""
