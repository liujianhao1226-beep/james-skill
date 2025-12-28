#!/usr/bin/env python3
"""
代码复杂度分析脚本
分析圈复杂度、函数长度等指标
"""

import ast
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List


@dataclass
class FunctionMetrics:
    name: str
    file: str
    line: int
    length: int
    complexity: int
    params: int


def calculate_complexity(node: ast.FunctionDef) -> int:
    """计算圈复杂度"""
    complexity = 1  # 基础复杂度

    for child in ast.walk(node):
        # 分支语句
        if isinstance(child, (ast.If, ast.While, ast.For)):
            complexity += 1
        # 异常处理
        elif isinstance(child, ast.ExceptHandler):
            complexity += 1
        # 布尔运算符
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
        # 条件表达式
        elif isinstance(child, ast.IfExp):
            complexity += 1
        # 列表推导式中的条件
        elif isinstance(child, ast.comprehension):
            complexity += len(child.ifs)

    return complexity


def analyze_function(node: ast.FunctionDef, filename: str) -> FunctionMetrics:
    """分析函数指标"""
    # 计算函数长度
    if node.body:
        start_line = node.lineno
        end_line = max(getattr(n, 'end_lineno', n.lineno) 
                       for n in ast.walk(node) 
                       if hasattr(n, 'lineno'))
        length = end_line - start_line + 1
    else:
        length = 1

    return FunctionMetrics(
        name=node.name,
        file=filename,
        line=node.lineno,
        length=length,
        complexity=calculate_complexity(node),
        params=len(node.args.args),
    )


def analyze_file(filepath: str) -> List[FunctionMetrics]:
    """分析文件中的所有函数"""
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"语法错误: {filepath}: {e}")
        return []

    metrics = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            metrics.append(analyze_function(node, filepath))
        elif isinstance(node, ast.AsyncFunctionDef):
            # 处理异步函数
            sync_node = ast.FunctionDef(
                name=node.name,
                args=node.args,
                body=node.body,
                decorator_list=node.decorator_list,
                returns=node.returns,
                lineno=node.lineno,
            )
            metrics.append(analyze_function(sync_node, filepath))

    return metrics


def print_report(all_metrics: List[FunctionMetrics], thresholds: dict):
    """打印分析报告"""
    print("=" * 70)
    print("代码复杂度分析报告")
    print("=" * 70)

    # 按问题严重程度分类
    high_complexity = []
    long_functions = []
    many_params = []

    for m in all_metrics:
        if m.complexity > thresholds["complexity"]:
            high_complexity.append(m)
        if m.length > thresholds["length"]:
            long_functions.append(m)
        if m.params > thresholds["params"]:
            many_params.append(m)

    # 高复杂度函数
    if high_complexity:
        print(f"\n🔴 高复杂度函数 (>{thresholds['complexity']}):")
        print("-" * 70)
        for m in sorted(high_complexity, key=lambda x: -x.complexity):
            print(f"  {m.file}:{m.line} {m.name}() - 复杂度: {m.complexity}")

    # 过长函数
    if long_functions:
        print(f"\n🟡 过长函数 (>{thresholds['length']} 行):")
        print("-" * 70)
        for m in sorted(long_functions, key=lambda x: -x.length):
            print(f"  {m.file}:{m.line} {m.name}() - {m.length} 行")

    # 参数过多
    if many_params:
        print(f"\n🟡 参数过多 (>{thresholds['params']} 个):")
        print("-" * 70)
        for m in sorted(many_params, key=lambda x: -x.params):
            print(f"  {m.file}:{m.line} {m.name}() - {m.params} 个参数")

    # 统计信息
    print("\n" + "=" * 70)
    print("统计信息")
    print("=" * 70)
    print(f"  总函数数: {len(all_metrics)}")
    print(f"  高复杂度: {len(high_complexity)}")
    print(f"  过长函数: {len(long_functions)}")
    print(f"  参数过多: {len(many_params)}")

    if all_metrics:
        avg_complexity = sum(m.complexity for m in all_metrics) / len(all_metrics)
        avg_length = sum(m.length for m in all_metrics) / len(all_metrics)
        print(f"  平均复杂度: {avg_complexity:.1f}")
        print(f"  平均长度: {avg_length:.1f} 行")

    # 返回是否有问题
    return len(high_complexity) + len(long_functions) + len(many_params)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="分析代码复杂度")
    parser.add_argument("path", help="要分析的文件或目录")
    parser.add_argument("--complexity", type=int, default=10, help="复杂度阈值 (默认: 10)")
    parser.add_argument("--length", type=int, default=50, help="函数长度阈值 (默认: 50)")
    parser.add_argument("--params", type=int, default=5, help="参数数量阈值 (默认: 5)")

    args = parser.parse_args()

    thresholds = {
        "complexity": args.complexity,
        "length": args.length,
        "params": args.params,
    }

    path = Path(args.path)
    all_metrics = []

    if path.is_file():
        all_metrics = analyze_file(str(path))
    elif path.is_dir():
        for py_file in path.rglob("*.py"):
            # 跳过测试文件和虚拟环境
            if "test" in str(py_file) or "venv" in str(py_file):
                continue
            all_metrics.extend(analyze_file(str(py_file)))
    else:
        print(f"路径不存在: {path}")
        sys.exit(1)

    issues = print_report(all_metrics, thresholds)
    sys.exit(1 if issues > 0 else 0)


if __name__ == "__main__":
    main()
