# Default output template

Adapt the wording to the user's request, but keep this overall structure.

## Chinese default

# 测试范围补充建议

## 模块复评摘要

Only include this section when the scope was reviewed by module or by subagents.

For each reviewed module, briefly state:

- 模块名称
- 主要参考文档
- 该模块新增或强化了什么
- 是否有跨模块问题需要主 agent 最终裁决

Good patterns:

- 按模块列出：配网、App、远程控制、语音、AI、OTA、性能、稳定性、产测等
- 每个模块都指出“主要依据来自哪份 PRD / 接口文档 / 缺陷 / 报告”
- 对于复评新增项，说明是“PRD 直接要求”还是“资深测试工程师视角补充”

## 缺口分析

For each important gap or design choice, cover these fields:

- **缺口点 / 设计点**：缺了什么、为什么要这样组织，或当前分支为什么过浅
- **影响**：为什么这块值得补或必须保留
- **依据**：来自哪份材料或哪类证据
- **建议补法**：建议补成哪一个一级 / 二级 / 三级分支

Good patterns:

- 按模块分组：配网、UI、电控、App、性能、稳定性等
- 对明显空节点，直接给出建议的展开方向
- 对证据不足的项，标记“基于通用智能硬件测试模型的建议”
- 对从零生成，说明所选 archetype 和主要假设

## 风险项

Use a compact prioritized structure such as:

- **高风险**：xxx
  - 原因：xxx
  - 建议优先补充：xxx
- **中风险**：xxx
- **低风险**：xxx

Prefer risk items that are structural, such as cross-end inconsistency, recovery failure, version ambiguity, missing exception paths, or fragile mode switching.

## 补充后的层级目录

Output an XMind-ready hierarchy. Example style:

- 功能
  - 配网与连接
    - 配网入口
    - 正向流程
    - 异常流程
    - 重置与重绑
  - UI与交互
    - 启动与引导
    - 页面状态
    - 本地交互
  - 设备控制
    - 模式与参数
    - 默认值与记忆
    - 恢复逻辑
- App与云
  - 设备管理
  - 状态同步
  - 权限与分享
- 兼容性
- 性能
- 稳定性与恢复
- OTA与诊断
- 场景链路
- 探索性
- 版本边界 / 待确认

## Optional file-export addendum

If the user explicitly asks for a real `.xmind` file, also provide:

- a short note describing the exported title and any kept warnings
- the generated file artifact

## English default

# Test scope expansion proposal

## Module review summary

- module
- key sources
- what was strengthened
- any cross-module issue escalated to the main agent

## Gap analysis

- gap or design choice
- why it matters
- evidence
- recommended branch to add

## Risks

- high
- medium
- low

## Expanded outline

- module
  - submodule
    - details

## Style rules

- Keep the hierarchy concise and reusable.
- Prefer branches that describe systems and dimensions, not one-off cases.
- Add a `version boundary / pending confirmation` branch whenever scope ownership is unclear.
- Add a cross-cutting dimension branch when many modules share the same concerns.
- When multi-agent review is used, keep evidence traceability visible at least at the module-summary level.
