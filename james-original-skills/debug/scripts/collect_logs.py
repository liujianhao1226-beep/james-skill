#!/usr/bin/env python3
"""
日志收集和分析脚本
帮助快速定位问题
"""

import re
import sys
from pathlib import Path
from collections import Counter
from datetime import datetime


def parse_log_line(line: str) -> dict | None:
    """解析日志行，提取时间戳、级别、消息"""
    # 常见日志格式: 2024-01-01 10:00:00 ERROR message
    pattern = r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(\w+)\s+(.*)"
    match = re.match(pattern, line)
    if match:
        return {
            "timestamp": match.group(1),
            "level": match.group(2),
            "message": match.group(3),
        }
    return None


def analyze_logs(log_file: str, level: str = None) -> None:
    """分析日志文件"""
    path = Path(log_file)
    if not path.exists():
        print(f"文件不存在: {log_file}")
        return

    errors = []
    level_counts = Counter()

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line_num, line in enumerate(f, 1):
            parsed = parse_log_line(line.strip())
            if parsed:
                level_counts[parsed["level"]] += 1
                if parsed["level"] in ("ERROR", "CRITICAL", "FATAL"):
                    errors.append((line_num, parsed))
            elif level and level.upper() in line.upper():
                errors.append((line_num, {"message": line.strip()}))

    # 输出统计
    print("=" * 50)
    print("日志统计")
    print("=" * 50)
    for lvl, count in level_counts.most_common():
        print(f"  {lvl}: {count}")

    # 输出错误
    if errors:
        print("\n" + "=" * 50)
        print(f"错误列表 (共 {len(errors)} 条)")
        print("=" * 50)
        for line_num, entry in errors[:20]:  # 只显示前 20 条
            msg = entry.get("message", "")[:100]
            print(f"  Line {line_num}: {msg}")
        if len(errors) > 20:
            print(f"  ... 还有 {len(errors) - 20} 条错误")


def grep_logs(log_file: str, pattern: str) -> None:
    """在日志中搜索模式"""
    path = Path(log_file)
    if not path.exists():
        print(f"文件不存在: {log_file}")
        return

    print(f"搜索: {pattern}")
    print("=" * 50)
    
    count = 0
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line_num, line in enumerate(f, 1):
            if re.search(pattern, line, re.IGNORECASE):
                print(f"Line {line_num}: {line.strip()[:100]}")
                count += 1
                if count >= 50:
                    print("... 结果过多，只显示前 50 条")
                    break
    
    print(f"\n共找到 {count} 条匹配")


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python collect_logs.py <日志文件>              # 分析日志")
        print("  python collect_logs.py <日志文件> <搜索模式>   # 搜索日志")
        sys.exit(1)

    log_file = sys.argv[1]
    
    if len(sys.argv) >= 3:
        grep_logs(log_file, sys.argv[2])
    else:
        analyze_logs(log_file)


if __name__ == "__main__":
    main()
