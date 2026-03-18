#!/usr/bin/env python3
"""
代码静态检查脚本
自动检测常见代码问题
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[int, str]:
    """执行命令并返回结果"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode, result.stdout + result.stderr
    except FileNotFoundError:
        return -1, f"命令未找到: {cmd[0]}"


def check_python(path: str) -> None:
    """检查 Python 代码"""
    print("=" * 50)
    print("Python 代码检查")
    print("=" * 50)

    # Ruff (快速 linter)
    code, output = run_command(["ruff", "check", path])
    if code == 0:
        print("✅ Ruff: 无问题")
    else:
        print("❌ Ruff 发现问题:")
        print(output)

    # MyPy (类型检查)
    code, output = run_command(["mypy", path])
    if code == 0:
        print("✅ MyPy: 类型检查通过")
    else:
        print("⚠️ MyPy 类型问题:")
        print(output)


def check_javascript(path: str) -> None:
    """检查 JavaScript/TypeScript 代码"""
    print("=" * 50)
    print("JavaScript/TypeScript 代码检查")
    print("=" * 50)

    # ESLint
    code, output = run_command(["npx", "eslint", path])
    if code == 0:
        print("✅ ESLint: 无问题")
    else:
        print("❌ ESLint 发现问题:")
        print(output)


def check_security(path: str) -> None:
    """安全检查"""
    print("=" * 50)
    print("安全检查")
    print("=" * 50)

    # 搜索敏感信息
    patterns = [
        ("硬编码密码", r"password\s*=\s*['\"][^'\"]+['\"]"),
        ("硬编码 API Key", r"api_key\s*=\s*['\"][^'\"]+['\"]"),
        ("硬编码 Secret", r"secret\s*=\s*['\"][^'\"]+['\"]"),
    ]

    for name, pattern in patterns:
        code, output = run_command(["grep", "-rn", "-E", pattern, path])
        if code == 0 and output.strip():
            print(f"⚠️ 可能的{name}:")
            print(output)


def main():
    if len(sys.argv) < 2:
        print("用法: python lint_check.py <路径>")
        sys.exit(1)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"路径不存在: {path}")
        sys.exit(1)

    check_python(path)
    check_javascript(path)
    check_security(path)


if __name__ == "__main__":
    main()
