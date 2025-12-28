#!/usr/bin/env python3
"""
测试运行脚本
支持多种运行模式和报告格式
"""

import subprocess
import sys
import os
from pathlib import Path


def run_pytest(
    path: str = ".",
    verbose: bool = True,
    coverage: bool = False,
    markers: str = None,
    parallel: bool = False,
    fail_fast: bool = False,
    html_report: bool = False,
) -> int:
    """运行 pytest"""
    cmd = ["pytest", path]

    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend(["--cov=.", "--cov-report=term-missing"])
        if html_report:
            cmd.append("--cov-report=html")

    if markers:
        cmd.extend(["-m", markers])

    if parallel:
        cmd.extend(["-n", "auto"])

    if fail_fast:
        cmd.append("-x")

    if html_report and not coverage:
        cmd.append("--html=report.html")

    print(f"运行命令: {' '.join(cmd)}")
    print("=" * 50)

    result = subprocess.run(cmd)
    return result.returncode


def run_jest(path: str = ".", coverage: bool = False) -> int:
    """运行 Jest"""
    cmd = ["npx", "jest", path]

    if coverage:
        cmd.append("--coverage")

    print(f"运行命令: {' '.join(cmd)}")
    print("=" * 50)

    result = subprocess.run(cmd)
    return result.returncode


def run_go_test(path: str = "./...", coverage: bool = False, verbose: bool = True) -> int:
    """运行 Go 测试"""
    cmd = ["go", "test", path]

    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend(["-coverprofile=coverage.out"])

    print(f"运行命令: {' '.join(cmd)}")
    print("=" * 50)

    result = subprocess.run(cmd)

    if coverage and result.returncode == 0:
        subprocess.run(["go", "tool", "cover", "-html=coverage.out", "-o", "coverage.html"])

    return result.returncode


def detect_test_framework() -> str:
    """检测项目使用的测试框架"""
    if Path("pytest.ini").exists() or Path("pyproject.toml").exists():
        return "pytest"
    if Path("package.json").exists():
        return "jest"
    if Path("go.mod").exists():
        return "go"
    return "pytest"  # 默认


def main():
    import argparse

    parser = argparse.ArgumentParser(description="运行测试")
    parser.add_argument("path", nargs="?", default=".", help="测试路径")
    parser.add_argument("-c", "--coverage", action="store_true", help="生成覆盖率报告")
    parser.add_argument("-m", "--markers", help="运行指定标记的测试")
    parser.add_argument("-p", "--parallel", action="store_true", help="并行运行")
    parser.add_argument("-x", "--fail-fast", action="store_true", help="失败时停止")
    parser.add_argument("--html", action="store_true", help="生成 HTML 报告")
    parser.add_argument("-f", "--framework", choices=["pytest", "jest", "go"], help="测试框架")

    args = parser.parse_args()

    framework = args.framework or detect_test_framework()
    print(f"使用测试框架: {framework}")

    if framework == "pytest":
        exit_code = run_pytest(
            path=args.path,
            coverage=args.coverage,
            markers=args.markers,
            parallel=args.parallel,
            fail_fast=args.fail_fast,
            html_report=args.html,
        )
    elif framework == "jest":
        exit_code = run_jest(path=args.path, coverage=args.coverage)
    elif framework == "go":
        exit_code = run_go_test(path=args.path, coverage=args.coverage)
    else:
        print(f"未知框架: {framework}")
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
