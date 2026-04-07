# Normalized scope-tree schema

Use this schema when creating a real `.xmind` file. The exporter accepts either this json schema or a markdown bullet outline.

## Wrapper object

```json
{
  "title": "smart desk lamp test scope",
  "root": {
    "title": "smart desk lamp test scope",
    "type": "root",
    "children": []
  },
  "warnings": [],
  "stats": {
    "node_count": 0,
    "leaf_count": 0,
    "max_depth": 0
  }
}
```

## Node fields

### Required
- `title`: display text for the XMind topic

### Optional but recommended
- `type`: examples include `module`, `quality`, `risk`, `boundary`, `scenario`, `cross-cutting`
- `children`: array of child nodes
- `note`: short explanation for humans; exported as XMind topic notes
- `source_refs`: list of evidence references such as `PRD-3.2`, `api.md section 5`, `bug export sprint 9`
- `confidence`: `high`, `medium`, or `low`
- `order`: integer used only before export if a custom order is needed

### Extended metadata (P1)
- `priority`: test priority — `P0` (blocker), `P1` (high), `P2` (medium), or `P3` (low)
- `test_type`: list of applicable test types — `functional`, `performance`, `security`, `compatibility`, `stability`, `exploratory`
- `automation_hint`: automation recommendation — `auto` (fully automatable), `semi-auto` (partially automatable), `manual` (must be manual)
- `risk_score`: numeric risk score 0–1000 computed by `scripts/risk_scorer.py` using FMEA-style RPN (severity × probability × detectability)

These fields are preserved during normalization, exported as XMind topic notes, and used by `risk_scorer.py` and `validate_scope_tree.py` for analysis.

## Minimal example

```json
{
  "title": "智能硬件测试范围",
  "root": {
    "title": "智能硬件测试范围",
    "type": "root",
    "children": [
      {
        "title": "功能模块",
        "type": "module",
        "children": [
          {"title": "配网与连接", "priority": "P0", "test_type": ["functional"], "automation_hint": "semi-auto"},
          {"title": "本地交互", "priority": "P1", "test_type": ["functional"], "automation_hint": "manual"}
        ]
      },
      {
        "title": "性能与稳定性",
        "type": "quality",
        "children": [
          {"title": "性能", "priority": "P1", "test_type": ["performance"], "automation_hint": "auto"},
          {"title": "稳定性与恢复", "priority": "P0", "test_type": ["stability"], "automation_hint": "semi-auto"}
        ]
      },
      {
        "title": "版本边界/待确认",
        "type": "boundary",
        "children": []
      }
    ]
  }
}
```

## Exporter behavior

- `title` and `children` drive the actual XMind structure.
- Unknown fields are ignored instead of failing the export.
- Empty `children` is allowed.
- The exporter automatically generates stable ids for the XMind archive.

## Validation expectations

Before export, check for:
- empty titles
- duplicate sibling titles
- excessive depth
- missing version-boundary branch when scope ownership is unclear
- overly flat trees that need another grouping level
