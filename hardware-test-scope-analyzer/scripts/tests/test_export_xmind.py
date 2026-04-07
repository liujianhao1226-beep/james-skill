"""Tests for export_xmind.py — XMind export and round-trip verification."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from scope_tree_lib import normalize_node, prepare_tree

# Import export functions
import sys
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from export_xmind import build_sheet, topic_to_xmind, write_xmind
from extract_xmind_outline import load_sheets, render_json_outline


class TestTopicToXmind:
    def test_root_has_structure_class(self):
        node = normalize_node({"title": "root", "children": [{"title": "child"}]})
        topic = topic_to_xmind(node, is_root=True)
        assert topic["structureClass"] == "org.xmind.ui.logic.right"
        assert topic["title"] == "root"
        assert "id" in topic

    def test_non_root_no_structure_class(self):
        node = normalize_node({"title": "child", "children": []})
        topic = topic_to_xmind(node, is_root=False)
        assert "structureClass" not in topic

    def test_children_attached(self):
        node = normalize_node({
            "title": "parent",
            "children": [{"title": "a"}, {"title": "b"}],
        })
        topic = topic_to_xmind(node, is_root=False)
        attached = topic["children"]["attached"]
        assert len(attached) == 2
        assert attached[0]["title"] == "a"

    def test_no_children_key_when_empty(self):
        node = normalize_node({"title": "leaf", "children": []})
        topic = topic_to_xmind(node)
        assert "children" not in topic

    def test_recursive_depth(self):
        node = normalize_node({
            "title": "l1",
            "children": [{"title": "l2", "children": [{"title": "l3"}]}],
        })
        topic = topic_to_xmind(node)
        l2 = topic["children"]["attached"][0]
        l3 = l2["children"]["attached"][0]
        assert l3["title"] == "l3"


class TestBuildSheet:
    def test_sheet_structure(self, sample_json_tree):
        wrapper = prepare_tree(sample_json_tree)
        sheet = build_sheet(wrapper)
        assert sheet["class"] == "sheet"
        assert "rootTopic" in sheet
        assert "id" in sheet

    def test_sheet_title_override(self, sample_json_tree):
        wrapper = prepare_tree(sample_json_tree)
        sheet = build_sheet(wrapper, sheet_title="Custom Sheet")
        assert sheet["title"] == "Custom Sheet"


class TestWriteXmind:
    def test_creates_valid_zip(self, sample_json_tree, tmp_path):
        wrapper = prepare_tree(sample_json_tree)
        output = tmp_path / "test.xmind"
        write_xmind(wrapper, output)
        assert output.exists()
        assert zipfile.is_zipfile(output)

    def test_zip_contents(self, sample_json_tree, tmp_path):
        wrapper = prepare_tree(sample_json_tree)
        output = tmp_path / "test.xmind"
        write_xmind(wrapper, output)
        with zipfile.ZipFile(output) as zf:
            names = set(zf.namelist())
            assert "content.json" in names
            assert "metadata.json" in names
            assert "manifest.json" in names

    def test_content_json_structure(self, sample_json_tree, tmp_path):
        wrapper = prepare_tree(sample_json_tree)
        output = tmp_path / "test.xmind"
        write_xmind(wrapper, output)
        with zipfile.ZipFile(output) as zf:
            content = json.loads(zf.read("content.json"))
            assert isinstance(content, list)
            assert len(content) == 1
            sheet = content[0]
            assert sheet["class"] == "sheet"
            assert "rootTopic" in sheet

    def test_creates_parent_dirs(self, sample_json_tree, tmp_path):
        wrapper = prepare_tree(sample_json_tree)
        output = tmp_path / "subdir" / "deep" / "test.xmind"
        write_xmind(wrapper, output)
        assert output.exists()


class TestRoundTrip:
    """Export to .xmind then extract back and compare."""

    def _collect_titles(self, node: dict, depth: int = 0) -> list[tuple[str, int]]:
        """Collect (title, depth) pairs via DFS."""
        result = [(node["title"], depth)]
        for child in node.get("children", []):
            result.extend(self._collect_titles(child, depth + 1))
        return result

    def test_roundtrip_json_tree(self, sample_json_tree, tmp_path):
        wrapper = prepare_tree(sample_json_tree)
        xmind_path = tmp_path / "roundtrip.xmind"
        write_xmind(wrapper, xmind_path)

        # Extract back
        sheets = load_sheets(xmind_path)
        assert len(sheets) == 1
        root_topic = sheets[0]["rootTopic"]
        extracted = render_json_outline(root_topic, include_summaries=False)

        # Compare titles at each level
        original_titles = self._collect_titles(wrapper["root"])
        extracted_titles = self._collect_titles(extracted)
        assert len(original_titles) == len(extracted_titles)
        for (orig_t, orig_d), (ext_t, ext_d) in zip(original_titles, extracted_titles):
            assert orig_t == ext_t
            assert orig_d == ext_d

    def test_roundtrip_from_markdown(self, sample_markdown, tmp_path):
        from scope_tree_lib import parse_markdown_outline

        wrapper = parse_markdown_outline(sample_markdown)
        wrapper = prepare_tree(wrapper)
        xmind_path = tmp_path / "from_md.xmind"
        write_xmind(wrapper, xmind_path)

        sheets = load_sheets(xmind_path)
        root_topic = sheets[0]["rootTopic"]
        extracted = render_json_outline(root_topic, include_summaries=False)

        original_titles = self._collect_titles(wrapper["root"])
        extracted_titles = self._collect_titles(extracted)
        assert len(original_titles) == len(extracted_titles)

    def test_roundtrip_deep_tree(self, deep_tree, tmp_path):
        wrapper = prepare_tree(deep_tree)
        xmind_path = tmp_path / "deep.xmind"
        write_xmind(wrapper, xmind_path)

        sheets = load_sheets(xmind_path)
        extracted = render_json_outline(sheets[0]["rootTopic"], include_summaries=False)

        original_titles = self._collect_titles(wrapper["root"])
        extracted_titles = self._collect_titles(extracted)
        assert len(original_titles) == len(extracted_titles)
