"""Unit tests for scope_tree_lib.py — the core shared library."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scope_tree_lib import (
    ScopeTreeError,
    TreeStats,
    coerce_title,
    collapse_ws,
    collect_warnings,
    compute_stats,
    dedupe_preserve_order,
    ensure_wrapper,
    iter_nodes,
    load_tree_from_path,
    normalize_node,
    parse_markdown_outline,
    prepare_tree,
    save_json,
)


# ===== collapse_ws =====

class TestCollapseWs:
    def test_normal(self):
        assert collapse_ws("hello world") == "hello world"

    def test_multiple_spaces(self):
        assert collapse_ws("  a   b  c  ") == "a b c"

    def test_fullwidth_space(self):
        assert collapse_ws("a\u3000b") == "a b"

    def test_empty(self):
        assert collapse_ws("") == ""

    def test_tabs_and_newlines(self):
        assert collapse_ws("a\tb\nc") == "a b c"


# ===== coerce_title =====

class TestCoerceTitle:
    def test_normal(self):
        assert coerce_title("配网与连接") == "配网与连接"

    def test_strips_whitespace(self):
        assert coerce_title("  hello  world  ") == "hello world"

    def test_empty_raises(self):
        with pytest.raises(ScopeTreeError, match="empty"):
            coerce_title("")

    def test_spaces_only_raises(self):
        with pytest.raises(ScopeTreeError, match="empty"):
            coerce_title("   ")


# ===== normalize_node =====

class TestNormalizeNode:
    def test_string_input(self):
        result = normalize_node("hello")
        assert result == {"title": "hello", "children": []}

    def test_dict_with_title(self):
        result = normalize_node({"title": "test", "children": []})
        assert result["title"] == "test"
        assert result["children"] == []

    def test_missing_title_raises(self):
        with pytest.raises(ScopeTreeError, match="missing.*title"):
            normalize_node({"children": []})

    def test_invalid_type_raises(self):
        with pytest.raises(ScopeTreeError, match="unsupported node type"):
            normalize_node(42)

    def test_preserves_optional_fields(self):
        node = {
            "title": "test",
            "type": "module",
            "note": "some note",
            "source_refs": ["PRD-1"],
            "confidence": "high",
            "order": 1,
        }
        result = normalize_node(node)
        assert result["type"] == "module"
        assert result["note"] == "some note"
        assert result["source_refs"] == ["PRD-1"]
        assert result["confidence"] == "high"
        assert result["order"] == 1

    def test_preserves_p1_extended_fields(self):
        node = {
            "title": "配网与连接",
            "priority": "P0",
            "test_type": ["functional", "stability"],
            "automation_hint": "semi-auto",
            "risk_score": 324.0,
        }
        result = normalize_node(node)
        assert result["priority"] == "P0"
        assert result["test_type"] == ["functional", "stability"]
        assert result["automation_hint"] == "semi-auto"
        assert result["risk_score"] == 324.0

    def test_ignores_unknown_fields(self):
        node = {"title": "test", "unknown_field": "value"}
        result = normalize_node(node)
        assert "unknown_field" not in result

    def test_skips_empty_optional_fields(self):
        node = {"title": "test", "note": "", "type": None}
        result = normalize_node(node)
        assert "note" not in result
        assert "type" not in result

    def test_recursive_children(self):
        node = {
            "title": "parent",
            "children": [
                {"title": "child1", "children": [{"title": "grandchild"}]},
                "child2",
            ],
        }
        result = normalize_node(node)
        assert len(result["children"]) == 2
        assert result["children"][0]["children"][0]["title"] == "grandchild"
        assert result["children"][1]["title"] == "child2"

    def test_none_children_becomes_empty_list(self):
        result = normalize_node({"title": "test", "children": None})
        assert result["children"] == []

    def test_invalid_children_type_raises(self):
        with pytest.raises(ScopeTreeError, match="must be a list"):
            normalize_node({"title": "test", "children": "not a list"})


# ===== ensure_wrapper =====

class TestEnsureWrapper:
    def test_wrapper_format(self, sample_json_tree):
        result = ensure_wrapper(sample_json_tree)
        assert result["title"] == "智能台灯测试范围"
        assert "root" in result
        assert "warnings" in result

    def test_bare_dict(self):
        node = {"title": "test", "children": [{"title": "child"}]}
        result = ensure_wrapper(node)
        assert result["title"] == "test"
        assert result["root"]["title"] == "test"

    def test_list_input(self):
        nodes = [{"title": "a"}, {"title": "b"}]
        result = ensure_wrapper(nodes)
        assert result["root"]["children"][0]["title"] == "a"
        assert result["root"]["children"][1]["title"] == "b"

    def test_title_hint_override(self):
        node = {"title": "original", "children": []}
        result = ensure_wrapper(node, title_hint="override")
        assert result["title"] == "override"

    def test_invalid_input_raises(self):
        with pytest.raises(ScopeTreeError, match="json input"):
            ensure_wrapper("just a string")

    def test_wrapper_with_warnings(self):
        wrapper = {
            "title": "test",
            "root": {"title": "test", "children": []},
            "warnings": ["some warning"],
        }
        result = ensure_wrapper(wrapper)
        assert result["warnings"] == ["some warning"]

    def test_wrapper_warnings_coerced(self):
        wrapper = {
            "title": "test",
            "root": {"title": "test", "children": []},
            "warnings": "single warning",
        }
        result = ensure_wrapper(wrapper)
        assert result["warnings"] == ["single warning"]

    def test_list_with_title_hint(self):
        result = ensure_wrapper([{"title": "a"}], title_hint="custom")
        assert result["title"] == "custom"


# ===== parse_markdown_outline =====

class TestParseMarkdownOutline:
    def test_basic(self, sample_markdown):
        result = parse_markdown_outline(sample_markdown)
        root = result["root"]
        assert root["title"] == "智能台灯测试范围"
        # 4 top-level children
        assert len(root["children"]) == 4

    def test_heading_extracted(self):
        md = "# My Title\n- a\n  - b\n"
        result = parse_markdown_outline(md)
        assert result["title"] == "My Title"

    def test_single_root(self, minimal_markdown):
        result = parse_markdown_outline(minimal_markdown)
        root = result["root"]
        assert root["title"] == "根节点"
        assert len(root["children"]) == 2

    def test_multi_root(self):
        md = "- root1\n  - child1\n- root2\n  - child2\n"
        result = parse_markdown_outline(md)
        # multi-root wraps in a wrapper
        assert len(result["root"]["children"]) == 2

    def test_tab_indent(self, tab_indented_markdown):
        result = parse_markdown_outline(tab_indented_markdown)
        root = result["root"]
        assert root["title"] == "根节点"
        assert len(root["children"]) == 2
        assert len(root["children"][0]["children"]) == 1

    def test_empty_lines_skipped(self):
        md = "- a\n\n\n  - b\n\n- c\n"
        result = parse_markdown_outline(md)
        assert len(result["root"]["children"]) >= 1

    def test_no_bullets_raises(self, no_bullet_markdown):
        with pytest.raises(ScopeTreeError, match="no bullet"):
            parse_markdown_outline(no_bullet_markdown)

    def test_empty_raises(self, empty_markdown):
        with pytest.raises(ScopeTreeError, match="no bullet"):
            parse_markdown_outline(empty_markdown)

    def test_title_hint_overrides_heading(self):
        md = "# Original\n- a\n  - b\n"
        result = parse_markdown_outline(md, title_hint="Override")
        assert result["title"] == "Override"

    def test_numbered_bullets(self):
        md = "1. first\n2. second\n   1. sub\n"
        result = parse_markdown_outline(md)
        assert len(result["root"]["children"]) >= 1

    def test_plus_and_star_bullets(self):
        md = "+ item1\n  * sub1\n  * sub2\n"
        result = parse_markdown_outline(md)
        root = result["root"]
        assert root["title"] == "item1"
        assert len(root["children"]) == 2


# ===== load_tree_from_path =====

class TestLoadTreeFromPath:
    def test_json_auto(self, write_json, sample_json_tree):
        path = write_json(sample_json_tree, "tree.json")
        result = load_tree_from_path(path)
        assert result["title"] == "智能台灯测试范围"

    def test_markdown_auto(self, write_markdown, sample_markdown):
        path = write_markdown(sample_markdown, "outline.md")
        result = load_tree_from_path(path)
        assert "root" in result

    def test_explicit_format(self, write_markdown, sample_markdown):
        path = write_markdown(sample_markdown, "outline.txt")
        result = load_tree_from_path(path, input_format="markdown")
        assert "root" in result

    def test_unsupported_format_raises(self, write_markdown, sample_markdown):
        path = write_markdown(sample_markdown)
        with pytest.raises(ScopeTreeError, match="unsupported"):
            load_tree_from_path(path, input_format="yaml")


# ===== iter_nodes =====

class TestIterNodes:
    def test_traversal_order(self):
        tree = {
            "title": "root",
            "children": [
                {"title": "a", "children": [{"title": "a1", "children": []}]},
                {"title": "b", "children": []},
            ],
        }
        titles = [(n["title"], d) for n, d in iter_nodes(tree)]
        assert titles == [("root", 0), ("a", 1), ("a1", 2), ("b", 1)]

    def test_leaf_node(self):
        node = {"title": "leaf"}
        result = list(iter_nodes(node))
        assert len(result) == 1
        assert result[0] == (node, 0)


# ===== compute_stats =====

class TestComputeStats:
    def test_basic(self, sample_json_tree):
        from scope_tree_lib import normalize_node
        root = normalize_node(sample_json_tree["root"])
        stats = compute_stats(root)
        assert stats.node_count > 0
        assert stats.leaf_count > 0
        assert stats.max_depth >= 2

    def test_single_node(self):
        stats = compute_stats({"title": "alone", "children": []})
        assert stats.node_count == 1
        assert stats.leaf_count == 1
        assert stats.max_depth == 0

    def test_to_dict(self):
        stats = TreeStats(node_count=5, leaf_count=3, max_depth=2)
        d = stats.to_dict()
        assert d == {"node_count": 5, "leaf_count": 3, "max_depth": 2}


# ===== collect_warnings =====

class TestCollectWarnings:
    def test_long_title_warning(self):
        root = normalize_node({
            "title": "root",
            "children": [{"title": "a" * 40}],
        })
        warnings = collect_warnings(root)
        assert any("long node title" in w for w in warnings)

    def test_deep_tree_warning(self, deep_tree):
        root = normalize_node(deep_tree["root"])
        warnings = collect_warnings(root)
        assert any("depth exceeds 6" in w for w in warnings)

    def test_wide_tree_warning(self, wide_tree):
        root = normalize_node(wide_tree["root"])
        warnings = collect_warnings(root)
        assert any("more than 12" in w for w in warnings)

    def test_duplicate_sibling_warning(self):
        root = normalize_node({
            "title": "root",
            "children": [
                {"title": "duplicate"},
                {"title": "Duplicate"},  # case-insensitive
            ],
        })
        warnings = collect_warnings(root)
        assert any("duplicate sibling" in w.lower() for w in warnings)

    def test_missing_version_boundary_warning(self):
        root = normalize_node({
            "title": "root",
            "children": [
                {"title": "功能模块"},
                {"title": "性能"},
                {"title": "稳定性"},
            ],
        })
        warnings = collect_warnings(root)
        assert any("version-boundary" in w for w in warnings)

    def test_missing_quality_branch_warning(self):
        root = normalize_node({
            "title": "root",
            "children": [
                {"title": "功能模块A"},
                {"title": "功能模块B"},
                {"title": "版本边界"},
            ],
        })
        warnings = collect_warnings(root)
        assert any("quality branch" in w for w in warnings)

    def test_small_top_level_warning(self):
        root = normalize_node({
            "title": "root",
            "children": [{"title": "only one"}],
        })
        warnings = collect_warnings(root)
        assert any("very small" in w for w in warnings)

    def test_no_warnings_for_good_tree(self):
        root = normalize_node({
            "title": "root",
            "children": [
                {"title": "功能模块", "children": [
                    {"title": "默认值"},
                    {"title": "异常流"},
                    {"title": "同步"},
                ]},
                {"title": "性能与稳定性"},
                {"title": "兼容性"},
                {"title": "版本边界/待确认"},
            ],
        })
        warnings = collect_warnings(root)
        # Should have no structural warnings (may still have cross-cutting advisory)
        assert not any("depth exceeds" in w for w in warnings)
        assert not any("long node" in w for w in warnings)
        assert not any("duplicate" in w for w in warnings)


# ===== dedupe_preserve_order =====

class TestDedupePreserveOrder:
    def test_basic(self):
        result = dedupe_preserve_order(["a", "b", "a", "c"])
        assert result == ["a", "b", "c"]

    def test_whitespace_normalization(self):
        result = dedupe_preserve_order(["  a  b  ", "a b"])
        assert len(result) == 1

    def test_empty_strings_removed(self):
        result = dedupe_preserve_order(["a", "", "  ", "b"])
        assert result == ["a", "b"]


# ===== prepare_tree =====

class TestPrepareTree:
    def test_full_pipeline(self, sample_json_tree):
        result = prepare_tree(sample_json_tree)
        assert "root" in result
        assert "warnings" in result
        assert "stats" in result
        assert isinstance(result["stats"], dict)
        assert result["stats"]["node_count"] > 0

    def test_adds_warnings(self, deep_tree):
        result = prepare_tree(deep_tree)
        assert len(result["warnings"]) > 0


# ===== save_json =====

class TestSaveJson:
    def test_to_file(self, tmp_path):
        data = {"title": "test", "value": 42}
        output = tmp_path / "out.json"
        save_json(data, output)
        loaded = json.loads(output.read_text(encoding="utf-8"))
        assert loaded == data

    def test_to_stdout(self, capsys):
        data = {"title": "test"}
        save_json(data, None)
        captured = capsys.readouterr()
        assert json.loads(captured.out) == data

    def test_chinese_not_escaped(self, tmp_path):
        data = {"title": "中文标题"}
        output = tmp_path / "out.json"
        save_json(data, output)
        content = output.read_text(encoding="utf-8")
        assert "中文标题" in content
        assert "\\u" not in content
