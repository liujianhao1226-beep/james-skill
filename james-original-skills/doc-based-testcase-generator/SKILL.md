---
name: doc-based-testcase-generator
description: Use when a user wants executable testcase tables, CSV output, or template-aligned testcase rows from requirement documents, especially when they mention Excel, CSV, 模板, 表格, 执行用例, or want a table instead of an XMind mindmap.
---

# doc-based-testcase-generator

Generate structured testcase tables from requirement sources.

## Use This Skill For

- CSV / Excel 风格测试用例
- 按现有模板列结构输出
- 需要 `用例编号 / 功能模块 / 前置条件 / 操作步骤 / 预期结果 / 优先级` 这样的执行型行数据

## Do Not Use This Skill For

- XMind / 思维导图输出
- 只想做测试范围脑图，不需要表格
- 只想总结报告，不是生成待执行用例

## Source Selection

Use the same primary/secondary split as the XMind skill:

1. Primary: PRD, requirement sheets, spec docs, interface docs
2. Secondary: testcase reports, existing outlines, bug reports

Rules:

- Prefer requirement spreadsheets over reports when both exist.
- Reports can补充场景，但不要让报告结构直接决定表格结构。
- If the source is already a testcase mindmap in heading Markdown, render it directly to CSV with the bundled script.

## Normalized Intermediate Format

This skill works best when testcase content is first drafted in normalized Markdown:

```markdown
## 模块
### 子模块
#### 用例标题
- 前置：...
- 操作：...
- 预期：...
```

The bundled renderer maps one `####` block to one table row.

## Template-Aligned Output

If the user provides a CSV template, render cases with:

```bash
python scripts/render_case_csv.py \
  --input cases.md \
  --template template.csv \
  --output cases.csv \
  --id-prefix TC
```

What the renderer guarantees:

- preserves template header order
- keeps trailing execution columns empty
- writes UTF-8 BOM CSV for spreadsheet compatibility
- strips `前置：/操作：/预期：` labels from cell content
- generates stable case IDs with a chosen prefix

## Default Column Contract

If no template is provided, use:

- 用例编号
- 需求编号
- 功能模块
- 功能类型
- 用例标题
- 前置条件
- 操作步骤
- 预期结果
- 自动化标识
- 优先级
- 测试结果
- 备注
- 测试人员
- 测试日期
- 缺陷编号
- 适用范围

## Classification Rules

- `功能类型`: default to `功能`; use `兼容性` or `性能` only when the testcase is clearly in those buckets
- `优先级`: default to P1/P2 unless the source clearly indicates a P0 core path
- `自动化标识`: default to `否` unless the user explicitly wants automation candidates marked

## Recommended Workflow

1. Pick primary requirement sources.
2. Draft or reuse normalized Markdown testcase content.
3. If the user has a template, render with the bundled script.
4. Spot-check IDs, module names, priority, and trailing empty columns.
5. Save the final CSV only if the user asks for a file.

## References

- `references/api-testcases-standard.md`
- `references/functional-testcases-standard.md`
- `references/performance-testcases-standard.md`
- `references/automation-testcases-standard.md`
