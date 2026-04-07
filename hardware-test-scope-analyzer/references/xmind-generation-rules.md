# XMind generation rules for test-scope trees

Use these rules when drafting a new mind map or expanding an existing one.

## Branch naming

- Prefer short noun phrases over full sentences.
- Keep one node focused on one concept: module, state family, parameter family, or cross-cutting dimension.
- Avoid vague node names such as `other`, `misc`, `logic`, or `optimization`.
- Good examples:
  - `配网与连接`
  - `模式与参数`
  - `默认值与记忆`
  - `异常流`
  - `重启与恢复`
- Bad examples:
  - `这里放一些补充测试点`
  - `各种异常情况`

## Recommended depth

- Level 1: major domains
- Level 2: modules, subsystems, or quality areas
- Level 3: concrete coverage dimensions
- Level 4+: only when the product truly needs deeper mode, parameter, or protocol details

Warn when the tree is deeper than 6 levels unless the product is protocol-heavy.

## Recommended top-level order

For most smart-hardware products:
1. product overview / version boundary
2. feature modules
3. local interaction
4. pairing / connectivity
5. app / cloud / permissions
6. compatibility
7. performance
8. stability / recovery / observability
9. ota / diagnostics / logs
10. security / privacy
11. scenario chains
12. production test / embedded / manufacturing
13. exploratory

It is fine to merge or omit categories when the product does not need them, but keep the overall order stable.

## Cross-cutting dimensions

Whenever a feature branch is too generic, expand it with some of these dimensions:
- default value
- boundary value
- entry / exit conditions
- exception flow
- state sync
- persistence / memory / restore
- mode priority / mutual exclusion
- permission or role difference
- weak-network / offline behavior
- reboot / reconnect / power-loss recovery
- logs / metrics / observability

## Version-boundary rule

Always add a branch such as `版本边界/待确认` or `version boundary / pending confirmation` when:
- sources conflict
- features are future or removed
- ownership is unclear
- the competitor has a feature that the product may not yet support

## Ordering rule inside siblings

Prefer this local order:
1. positive or default flow
2. state and parameter branches
3. exception flow
4. sync and recovery
5. diagnostics or observability

## Flattening rule

If one node has more than about 12 direct children, add an intermediate grouping level unless the children are already a simple parameter checklist.
