#!/usr/bin/env python3
import argparse
from pathlib import Path


def convert(text: str, title: str) -> str:
    result = [f"# Sheet: {title}", "", "", f"## {title}", ""]
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("# "):
            continue
        if line.startswith("## "):
            result.append(f"- {line[3:].strip()}")
        elif line.startswith("### "):
            result.append(f"  - {line[4:].strip()}")
        elif line.startswith("#### "):
            result.append(f"    - {line[5:].strip()}")
        elif line.startswith("- "):
            result.append(f"      - {line[2:].strip()}")
    return "\n".join(result) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert heading-based testcase markdown to indented xmind-tool markdown.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--title", required=True)
    args = parser.parse_args()

    src = Path(args.input)
    dst = Path(args.output)
    text = src.read_text(encoding="utf-8")
    dst.write_text(convert(text, args.title), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
