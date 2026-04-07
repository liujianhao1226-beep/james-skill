# Evidence-to-branch mapping

Use this file to translate raw project artifacts into mind-map branches.

## Mapping table

| Evidence source | Extract first | Usually changes these branches | Common mistakes |
| --- | --- | --- | --- |
| PRD / MRD / requirement spec | user journeys, actors, version scope, exclusions, user-visible states | feature modules, scenario chains, permissions, version boundary | stopping at feature names and missing recovery / state rules |
| Requirement matrix / parameter table | modes, defaults, ranges, units, step size, ownership | parameterized branches, mode branches, default / memory / boundary sub-branches | copying the table directly without adding state transitions |
| Interface / protocol / API doc | states, commands, fields, retries, timeout, error codes, sync rules | state machine, exception flow, sync, offline behavior, observability | treating backend intent as proven ux behavior |
| Embedded design / board communication doc | master-slave rules, storage, watchdog, boot, reset, logs | embedded, stability, reboot, factory, diagnostics | ignoring persistence and recovery dependencies |
| Defect export / bug tracker | hotspots, repeated regressions, ownership confusion, difficult recovery | risk ranking, regression branches, weak-module expansion | using defects as the only architecture source |
| Test reports | already-covered depth, frequent failures, missing areas, version notes | scope diff, priority, risk items, version boundary | assuming all untested areas are intentionally out of scope |
| Competitor material | benchmark scenarios, alternative organization, expected market baseline | benchmark inspiration, optional scenario ideas | promoting competitor-only features to must-test scope |
| Release notes / changelog | newly changed behavior, removals, known issues | regression, version boundary, migration, upgrade | mixing old and current scope |
| Factory test / calibration / service doc | diagnostics, calibration, traceability, repair flows | production test, manufacturing, serviceability, traceability | forgetting shipment defaults and recovery tools |

## Extraction order

When the evidence set is large, use this order:
1. version boundary and exclusions
2. core capability modules
3. state and parameter model
4. cross-end synchronization
5. exception and recovery
6. performance and stability
7. production / manufacturing / diagnostics
8. benchmark inspiration

## Branch-building rules by source

### From PRD and requirement tables

Always ask:
- what can the user see or trigger
- what modes or roles exist
- what parameters have bounds or defaults
- what version or region limits apply

These usually create:
- feature modules
- scenario chains
- permissions / roles
- version boundary

### From interface or protocol documents

Always ask:
- what is the state machine
- what can timeout or retry
- what error codes or failure classes exist
- what state is shared across device, app, and cloud

These usually create:
- state management
- sync and conflict resolution
- exception flow
- reconnect / reboot / offline recovery
- logging and observability

### From defects and reports

Always ask:
- which modules repeatedly fail
- which failures are hard to recover from
- which changes appear frequently across versions
- which bugs imply a missing structural branch rather than a missing single case

These usually change:
- risk priority
- regression depth
- recovery branches
- cross-cutting checks

### From competitor documents

Use only for:
- missing scenario inspiration
- naming ideas
- future-looking benchmark branches

Do not use competitor evidence alone to justify a mandatory branch unless another project source supports it.
