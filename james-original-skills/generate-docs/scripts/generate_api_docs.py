#!/usr/bin/env python3
"""
API 文档生成脚本
从代码注释自动生成 API 文档
"""

import ast
import sys
from pathlib import Path
from typing import Optional


def extract_docstring(node) -> Optional[str]:
    """提取节点的 docstring"""
    return ast.get_docstring(node)


def parse_function(node: ast.FunctionDef) -> dict:
    """解析函数定义"""
    # 获取参数
    args = []
    for arg in node.args.args:
        arg_info = {"name": arg.arg}
        if arg.annotation:
            arg_info["type"] = ast.unparse(arg.annotation)
        args.append(arg_info)

    # 获取返回类型
    returns = None
    if node.returns:
        returns = ast.unparse(node.returns)

    return {
        "name": node.name,
        "docstring": extract_docstring(node),
        "args": args,
        "returns": returns,
        "decorators": [ast.unparse(d) for d in node.decorator_list],
    }


def parse_class(node: ast.ClassDef) -> dict:
    """解析类定义"""
    methods = []
    for item in node.body:
        if isinstance(item, ast.FunctionDef):
            methods.append(parse_function(item))

    return {
        "name": node.name,
        "docstring": extract_docstring(node),
        "methods": methods,
        "bases": [ast.unparse(b) for b in node.bases],
    }


def parse_module(file_path: str) -> dict:
    """解析 Python 模块"""
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    module_doc = extract_docstring(tree)
    functions = []
    classes = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(parse_function(node))
        elif isinstance(node, ast.ClassDef):
            classes.append(parse_class(node))

    return {
        "file": file_path,
        "docstring": module_doc,
        "functions": functions,
        "classes": classes,
    }


def generate_markdown(module_info: dict) -> str:
    """生成 Markdown 文档"""
    lines = []
    
    # 模块标题
    module_name = Path(module_info["file"]).stem
    lines.append(f"# {module_name}")
    lines.append("")
    
    if module_info["docstring"]:
        lines.append(module_info["docstring"])
        lines.append("")

    # 类文档
    for cls in module_info["classes"]:
        lines.append(f"## class {cls['name']}")
        if cls["bases"]:
            lines.append(f"继承自: {', '.join(cls['bases'])}")
        lines.append("")
        
        if cls["docstring"]:
            lines.append(cls["docstring"])
            lines.append("")

        for method in cls["methods"]:
            if method["name"].startswith("_") and method["name"] != "__init__":
                continue  # 跳过私有方法
            
            # 方法签名
            args_str = ", ".join(
                f"{a['name']}: {a.get('type', 'Any')}" for a in method["args"]
            )
            returns = f" -> {method['returns']}" if method["returns"] else ""
            lines.append(f"### {method['name']}({args_str}){returns}")
            lines.append("")
            
            if method["docstring"]:
                lines.append(method["docstring"])
                lines.append("")

    # 函数文档
    if module_info["functions"]:
        lines.append("## Functions")
        lines.append("")
        
        for func in module_info["functions"]:
            if func["name"].startswith("_"):
                continue
                
            args_str = ", ".join(
                f"{a['name']}: {a.get('type', 'Any')}" for a in func["args"]
            )
            returns = f" -> {func['returns']}" if func["returns"] else ""
            lines.append(f"### {func['name']}({args_str}){returns}")
            lines.append("")
            
            if func["docstring"]:
                lines.append(func["docstring"])
                lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("用法: python generate_api_docs.py <python_file> [output_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not Path(input_file).exists():
        print(f"文件不存在: {input_file}")
        sys.exit(1)

    module_info = parse_module(input_file)
    markdown = generate_markdown(module_info)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown)
        print(f"文档已生成: {output_file}")
    else:
        print(markdown)


if __name__ == "__main__":
    main()
