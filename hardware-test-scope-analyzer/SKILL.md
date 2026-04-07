---
name: hardware-test-scope-analyzer
description: Use when analyzing or generating smart-hardware test scope from xmind, prd, requirement tables, interface docs, defect exports, test reports, release notes, or competitor materials, especially when the work should be split by module and reviewed in parallel by senior-test-engineer subagents before exporting a real .xmind file.
---

# Hardware Test Scope Analyzer

Review smart-hardware evidence and produce a reusable testing structure. Support two modes:

1. **Expand existing scope**: compare a current XMind or test-scope document against product evidence.
2. **Create scope from zero**: generate a fresh XMind-ready tree when the user has documents but no existing mind map.

Keep the response in the user's language. When the user writes in Chinese, default to Chinese headings and branch names.

## When To Use

- The user wants to补充、优化或新建测试范围思维导图。
- The sources include `.xmind`, PRD, requirement tables, API/protocol docs, defect lists, reports, release notes, factory docs, or competitor material.
- The product has multiple independent domains such as device, app, cloud, connectivity, voice, AI, OTA, stability, performance, or factory test.
- The scope is large enough that module-by-module parallel review is safer than single-thread drafting.
- The user wants an actual `.xmind` artifact, not only prose.

Do not use this skill when:

- The user only wants final executable testcases rather than a test-scope tree.
- The task is limited to polishing a small existing outline with no real evidence review.
- The user only wants a plain summary of one document.

## Default Workflow

1. Build a source inventory.
   - Separate **current-scope artifacts** from **evidence artifacts**.
   - Current-scope artifacts usually include `.xmind`, current case lists, or an existing test-scope document.
   - Evidence artifacts usually include PRD, requirement tables, interface or protocol documents, defect lists, test reports, release notes, manufacturing docs, and competitor material.
   - Use `references/source-mapping.md` and `references/evidence-to-branch-mapping.md` to decide what each source should contribute.
2. Choose the operating mode.
   - **Existing XMind present**: treat it as the baseline and perform a gap review.
   - **No XMind present**: choose the nearest product archetype from `references/product-archetypes.md`, then build a first draft from documents.
   - **Hybrid product**: start with the universal base tree, then merge the most relevant domain archetypes and prune unsupported branches.
3. Build the product model from the evidence.
   - From PRD and requirement tables, extract user-visible capabilities, modes, parameters, roles, journeys, version scope, and exclusions.
   - From interface or protocol documents, extract states, fields, ranges, retries, timeouts, error codes, sync rules, and offline behavior.
   - From defects and reports, extract hotspots, repeated regressions, ambiguous ownership, and fragile recovery paths.
   - From manufacturing or factory-test material, extract diagnostic, calibration, production test, and traceability requirements.
   - From competitor material, extract benchmark ideas only. Do not silently convert competitor-only features into mandatory scope.
4. Split the review if the scope is large.
5. Build or compare the scope tree.
6. Resolve ambiguity explicitly.
7. Generate the analysis deliverable and, if requested, export the real `.xmind`.

## Multi-agent Review Mode

When the scope is broad, do not let one agent sequentially draft the whole tree. Prefer a module-by-module review using multiple subagents.

### When To Split By Module

Use multi-agent mode when at least one of these is true:

- The scope contains 3 or more major modules with different behaviors.
- The evidence set is large and spans multiple PRDs or multiple detailed specs.
- The product has multiple control ends or system layers, such as device, app, cloud, voice, and OTA.
- The user explicitly asks for “multi-agent”, “分模块”, “资深测试工程师补充”, or a second-pass optimization.

Avoid splitting when:

- The outline is tiny and can be fully reasoned about in one pass.
- The product is so tightly coupled that the whole model must be stabilized first.
- The user only wants one module.

### Module Partition Strategy

Do not split by equal size alone. Split by system boundary or risk domain first.

Recommended partition order:

1. First by top-level domain:
   - 设备本体 / 电控 / 传感 / 音频 / 屏幕
   - 配网 / 连接 / 云端 / 远程控制
   - App / 多端同步 / 账号权限 / 分享
   - 语音 / AI / 场景联动
   - OTA / 诊断 / 产测
   - 性能 / 稳定性 / 兼容性 / 安全性
2. If a top-level domain is still too large, split by second-level functional module.
3. Leave cross-module consistency problems to the main agent for final consolidation.

### Subagent Role

Each subagent acts as a **senior hardware/software test engineer** for its assigned module. It is not a transcription worker.

Each subagent must:

- Focus only on its assigned module.
- Read the relevant PRD sections and related supporting documents for that module.
- Use current XMind or current scope doc as baseline when available.
- Expand missing branches and weak branches.
- Add high-value supplement branches from a senior test-engineering perspective.
- Explicitly review abnormal flow, boundary values, state transitions, persistence, recovery, weak network, reboot, power loss, sync, permissions, and concurrency where relevant.
- Mark assumptions and unresolved conflicts instead of inventing unsupported requirements.

### Evidence Assignment Rule

Do not give every subagent every document blindly. Assign evidence by module relevance.

For each module, provide the subagent with:

- The relevant PRD chapter or feature section.
- The matching requirement table, parameter sheet, or ownership table if present.
- The interface / protocol / API material that governs that module.
- The defects, test reports, and release notes that mention that module.
- Any cross-end or cross-module rule documents that affect consistency.

If a document spans all modules, the main agent should summarize the globally shared rules once and pass only the relevant subset to each subagent.

### Subagent Deliverables

Each subagent should return:

1. **Module gap review**
   - What is missing or under-expanded
   - Why it matters
   - Which document supports the recommendation
2. **Module-optimized outline**
   - XMind-ready hierarchy for that module
3. **Senior-review supplements**
   - High-value additions beyond literal PRD wording
   - Typical hidden risks or fragile links
   - Assumptions or conflicts needing main-agent arbitration

### Main-agent Merge Rules

The main agent must not just concatenate module outlines. It must:

- Merge module trees into one stable XMind hierarchy.
- Remove overlap and rename branches for consistency.
- Preserve a stable top-level order.
- Reconcile shared concerns such as sync, state ownership, and recovery behavior.
- Keep evidence traceability for each major addition.
- Separate three kinds of items:
  - already covered
  - recommended to add
  - version boundary / pending confirmation

### Cross-module Final Review

Before export, the main agent must run one more cross-module review for:

- Device / App / Cloud / Voice state consistency
- Multi-end conflict resolution
- Power loss, reboot, reconnect, and OTA recovery
- Permission and sharing boundaries
- Cross-version ownership ambiguity
- Long-path scenario chains across modules

## PRD And Evidence Review Rules

The skill should not rely on the mind map alone. Each major branch recommendation should be backed by one or more sources when possible.

### From PRD and feature specs

Always extract:

- user-visible features
- user journeys
- roles and permissions
- mode or scene definitions
- parameters and ranges
- version boundaries and exclusions

### From requirement tables

Always look for:

- defaults
- numeric limits
- units
- enum values
- mutually exclusive modes
- ownership and applicability

### From interface / protocol / API docs

Always look for:

- states and state transitions
- request and response fields
- retries and timeouts
- error codes
- reporting cadence
- offline behavior
- sync and eventual-consistency rules

### From defect lists and reports

Use them to raise priority and detect fragile branches, especially:

- stale-state problems
- recovery failure after reconnect or reboot
- missing exception handling
- hidden coupling across module boundaries
- regressions around upgrades, migration, or data persistence

### From release notes and scope notes

Use them to decide whether something is a missing branch or a version-boundary item.

### From competitor materials

Use competitor features only as benchmark inspiration. They do not become mandatory branches unless product evidence supports them.

## Build Or Compare The Scope Tree

- Use `references/test-domain-checklist.md` to check first-level and second-level coverage.
- Use `references/xmind-generation-rules.md` to keep branch naming, ordering, and depth consistent.
- For from-zero generation, organize the tree around architecture, user journeys, cross-cutting dimensions, and version boundaries.
- For diff mode, compare the current scope against the product model and mark what is already covered vs. recommended to add.

## From-zero XMind Creation Workflow

When the user wants an actual `.xmind` file, do not stop at prose.

1. Analyze the documents and draft a clean bullet hierarchy or normalized tree.
2. If needed, consult:
   - `references/product-archetypes.md`
   - `references/evidence-to-branch-mapping.md`
   - `references/xmind-schema.md`
   - `references/xmind-generation-rules.md`
3. Save the outline as either:
   - markdown bullets, or
   - normalized json following `references/xmind-schema.md`
4. Normalize and validate it:
   - `python3 scripts/build_scope_tree.py outline.md --title "..." --output scope-tree.json`
5. Export the actual XMind file:
   - `python3 scripts/export_xmind.py scope-tree.json output.xmind`
6. Verify the generated file:
   - `python3 scripts/extract_xmind_outline.py output.xmind`
   - ensure the extracted hierarchy matches the intended structure

Use `scripts/build_scope_tree.py` when the hierarchy exists only as text. Use `scripts/export_xmind.py` when the user explicitly wants a real `.xmind` artifact.

## Analysis Rules

- Prefer structural completeness over a giant flat list of cases.
- Do not stop at generic branch names such as `UI`, `performance`, or `compatibility`. Expand them into concrete subdomains.
- For every stateful function, check at least: default value, entry and exit logic, boundary values, exception flow, persistence, and recovery after reboot or network change.
- For every multi-end feature, check at least: device state, app state, cloud state, sync timing, conflict resolution, and stale-data refresh.
- For every parameterized feature, look for numeric ranges, units, step size, mutually exclusive modes, and restored previous state.
- Use defect evidence to increase priority, not to replace the architecture review.
- When the current outline is thin but the product evidence is rich, propose the missing branches instead of asking the user to reorganize first.
- When the evidence is thin, produce a best-effort baseline outline and mark assumptions clearly.
- When generating a new mind map, keep one stable top-level order so later versions are diff-friendly.
- Add a `version boundary / pending confirmation` branch whenever scope ownership is unclear.
- Add cross-cutting dimensions whenever several modules share the same concerns.

## Handling Common Request Shapes

### If the user provides only an existing XMind

Perform a checklist-driven expansion.

- Extract the current outline with `scripts/extract_xmind_outline.py`.
- Find obviously missing branches and weakly expanded branches.
- Mark recommendations as assumptions when supporting product evidence is unavailable.

### If the user provides XMind plus supporting documents

Perform an evidence-based gap review.

- Use the XMind as the baseline.
- Use PRD, requirements, API, defects, reports, and competitor notes to prove what is missing or high risk.
- Prioritize additions that are both user-visible and systemically risky.
- If the scope is large, split the review by module and merge the optimized module trees afterward.

### If the user provides no XMind

Create a baseline smart-hardware test-scope tree.

- Choose the nearest archetype and note the choice.
- Organize it around architecture, journeys, cross-cutting checks, and version boundaries.
- State that it is a proposed outline, not a diff against an existing one.
- If the user wants a real file, export the outline to `.xmind`.

## Output Requirements

Use the user's language.

When writing Chinese, default to these top-level sections:

1. `测试范围补充建议`
2. `缺口分析`
3. `风险项`
4. `补充后的层级目录`

When multi-agent mode is used, also include a compact `模块复评摘要` section that states:

- which modules were reviewed
- what each subagent added or strengthened
- which cross-module issues were escalated to the main agent

When the user asks for from-zero generation, treat `缺口分析` as a coverage-rationale section that explains why the proposed branches exist, what assumptions were used, and which documents they came from.

Within `缺口分析`, prefer compact entries that answer four questions:

- what is missing, under-expanded, or assumed
- why it matters
- which source supports the recommendation
- how it should be represented in the outline

Within `风险项`, rank items as high / medium / low or P0 / P1 / P2. Focus on failure severity, coupling, change frequency, and defect history.

Within `补充后的层级目录`, output a clean XMind-ready hierarchy instead of long prose. Keep branch names concise and reusable.

If the user explicitly asks for a file, also return the generated `.xmind` artifact and mention any validator warnings that were kept.

## Useful Bundled Resources

- `scripts/extract_xmind_outline.py`: extract readable outlines from existing `.xmind` files.
- `scripts/build_scope_tree.py`: normalize markdown or json outlines into a validated tree.
- `scripts/export_xmind.py`: export a normalized tree or markdown outline into a real `.xmind` file. Metadata fields (`priority`, `test_type`, `automation_hint`, `risk_score`, `source_refs`) are exported as XMind topic notes.
- `scripts/validate_scope_tree.py`: validate a scope tree against the 14 test-domain checklist and report per-domain coverage.
- `scripts/risk_scorer.py`: compute FMEA-style risk scores (RPN) for scope-tree nodes based on severity, probability, and detectability signals.
- `references/source-mapping.md`: how to interpret each artifact type and handle conflicts.
- `references/evidence-to-branch-mapping.md`: how each evidence source should change the tree.
- `references/product-archetypes.md`: reusable starting skeletons for common smart-hardware products.
- `references/test-domain-checklist.md`: reusable smart-hardware coverage checklist.
- `references/xmind-schema.md`: normalized json schema for scope trees, including extended metadata fields (`priority`, `test_type`, `automation_hint`, `risk_score`).
- `references/xmind-generation-rules.md`: branch naming, ordering, and depth rules.
- `references/risk-signals.md`: patterns that indicate hidden or high-priority scope gaps, including quantitative FMEA risk scoring model.
- `references/output-template.md`: default response structure.
