---
name: prd-to-xmind-testcases
description: Use when a user wants requirement documents turned into XMind-friendly testcase mindmaps or Markdown outlines, especially when they mention XMind, 思维导图, 脑图, 导入 XMind, or want a .xmind-style structure instead of a testcase table.
---

# prd-to-xmind-testcases

Generate testcase mindmaps from requirement sources.

## Use This Skill For

- XMind / 思维导图 / 脑图形式的测试用例
- PRD、需求说明、规格表整理成模块化测试覆盖树
- 需要后续继续转成 `.xmind` 文件

## Do Not Use This Skill For

- 执行型 CSV / Excel 用例表
- 需要严格贴合模板列结构的测试用例
- 单纯整理测试报告，不是从需求反推用例

## Source Selection

Pick sources in this order:

1. Primary: PRD, requirement sheets, spec docs, interface docs
2. Secondary: existing testcase outlines, testcase reports, bug reports
3. Exclude as primary: 已执行测试报告、冒烟报告、行业研究报告

Rules:

- If a requirement spreadsheet exists, prefer it as the primary source.
- Use reports only to补充真实场景、命名口径、历史回归点.
- Do not turn management branches such as `横切维度` or `版本边界/需求待确认` into top-level testcase modules. Use them as expansion rules across modules.

## Supported Inputs

- Directly readable with bundled script: `.md`, `.txt`, `.csv`, `.xlsx`, `.docx`
- `.pdf`: only if the environment already has a usable extractor; otherwise ask for text or another source format

To flatten structured inputs into plain text:

```bash
python scripts/extract_requirements.py --input requirements.xlsx --output requirements.txt
```

## Output Modes

This skill has two output contracts. Pick the one that matches the downstream tool.

### Mode 1: XMind Markdown Import

Use this when the user wants Markdown that can be imported by XMind desktop.

Shape:

```markdown
# 测试用例标题
## 模块
### 功能/子模块
#### 测试点
- 前置：...
- 操作：...
- 预期：...
```

### Mode 2: XMind-Tool Compatible Markdown

Use this when the downstream tool expects a root topic plus indented list format, for example an `.xmind` creator/updater that reads list indentation instead of heading levels.

Convert heading-based Markdown with:

```bash
python scripts/convert_headings_to_xmind_tool_md.py \
  --input cases.md \
  --output cases.xmind-tool.md \
  --title "测试用例导图"
```

Shape:

```markdown
# Sheet: 测试用例导图

## 测试用例导图

- 模块
  - 功能/子模块
    - 测试点
      - 前置：...
      - 操作：...
      - 预期：...
```

## Generation Rules

- Root: product, feature set, or test scope name
- Level 1: modules
- Level 2: functions or submodules
- Level 3: testcase titles
- Level 4 bullets: `前置` / `操作` / `预期`

Coverage rules:

- Prefer concrete testable behavior over abstract labels
- Keep one testcase per `####` node
- Split happy path, boundary, and abnormal flow into separate testcases
- If the source is weak but reports expose critical product logic, keep the logic but do not reframe a report artifact as a requirement

## Recommended Workflow

1. Identify primary and secondary sources.
2. Flatten spreadsheets or docx inputs if needed.
3. Draft heading-based Markdown outline.
4. Review whether module boundaries match the real product, not the report structure.
5. If the user wants actual `.xmind`, convert to xmind-tool compatible Markdown and pass it to the downstream xmind creator.

## References

- `references/通用测试用例设计策略.md`
- `references/api-testcases-standard.md`
- `references/functional-testcases-standard.md`
- `references/performance-testcases-standard.md`
