"""Tests for build_scope_tree.py CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
BUILD_SCRIPT = SCRIPTS_DIR / "build_scope_tree.py"


def run_build(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(BUILD_SCRIPT)] + args,
        capture_output=True,
        text=True,
        cwd=cwd or SCRIPTS_DIR,
    )


class TestBuildScopeTreeCLI:
    def test_markdown_to_stdout(self, write_markdown, sample_markdown):
        path = write_markdown(sample_markdown)
        result = run_build([str(path)])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "root" in data
        assert "stats" in data
        assert data["stats"]["node_count"] > 0

    def test_json_input(self, write_json, sample_json_tree):
        path = write_json(sample_json_tree)
        result = run_build([str(path)])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["title"] == "智能台灯测试范围"

    def test_title_override(self, write_markdown, sample_markdown):
        path = write_markdown(sample_markdown)
        result = run_build([str(path), "--title", "Custom Title"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["title"] == "Custom Title"

    def test_output_to_file(self, write_markdown, sample_markdown, tmp_path):
        path = write_markdown(sample_markdown)
        outfile = tmp_path / "output.json"
        result = run_build([str(path), "--output", str(outfile)])
        assert result.returncode == 0
        assert outfile.exists()
        data = json.loads(outfile.read_text(encoding="utf-8"))
        assert "root" in data

    def test_file_not_found(self, tmp_path):
        result = run_build([str(tmp_path / "nonexistent.md")])
        assert result.returncode != 0

    def test_invalid_content(self, write_markdown, no_bullet_markdown):
        path = write_markdown(no_bullet_markdown)
        result = run_build([str(path)])
        assert result.returncode != 0

    def test_explicit_format(self, write_markdown, sample_markdown):
        path = write_markdown(sample_markdown, "outline.txt")
        result = run_build([str(path), "--input-format", "markdown"])
        assert result.returncode == 0
