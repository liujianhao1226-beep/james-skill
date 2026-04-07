# Risk signals for hidden test-scope gaps

Use these signals to prioritize what should be added first.

## High-priority signals

- The outline has a top-level node like `ui`, `performance`, or `compatibility` with no meaningful second level.
- A feature has numeric parameters or multiple modes, but the outline does not mention ranges, defaults, step size, mutual exclusion, or restore behavior.
- The product spans device + app + cloud + voice, but the outline covers only one end.
- The defect list clusters around a branch that is barely represented in the current scope.
- Pairing, upgrade, permissions, or sync are present in the product but absent or only named superficially in the outline.
- The product depends on network, cloud, or sensors, but there is no recovery branch for weak network, reconnect, reboot, or false trigger.
- Special modes exist, but entry, interruption, exit, and resume logic are missing.

## Medium-priority signals

- The current scope reflects only positive flow and omits invalid input, timeout, cancellation, or fallback.
- Reports show many fixed bugs in one area, but the outline still lacks a regression branch for that area.
- There are multiple sources of truth for the same state or parameter, but no cross-end consistency branch exists.
- The outline is organized by team ownership only and does not expose user journey or scenario chains.

## Low-priority but useful signals

- Competitor material suggests scenarios that the current product may soon need.
- The outline mixes current version and future ideas without a version-boundary branch.
- The structure is complete enough, but branch names are too vague to be actionable.

## Simple priority heuristic

Raise priority when several of these apply together:
- severe user impact
- high coupling across modules or ends
- frequent recent changes
- repeated historical defects
- difficult field recovery
- hard-to-observe failures

## Quantitative risk scoring (FMEA-style RPN)

Use `scripts/risk_scorer.py` for automated risk quantification.

### Model

Each node is scored on three dimensions (1–10 each):

| Dimension | Symbol | Meaning | 1 = best | 10 = worst |
|-----------|--------|---------|----------|------------|
| Severity | S | User/business impact if this area fails | Cosmetic | Safety / data loss / bricking |
| Probability | P | Likelihood of a defect existing here | Simple, well-tested | Complex, multi-end, weak-network dependent |
| Detectability | D | How hard to catch before release | Easy to test, obvious failure | Intermittent, timing-dependent, accumulative |

**RPN = S × P × D** (range 1–1000)

### Priority mapping

| RPN range | Priority | Action |
|-----------|----------|--------|
| >= 300 | P0 | Must test; block release if uncovered |
| 150–299 | P1 | High priority; cover in current sprint |
| 60–149 | P2 | Medium priority; plan for coverage |
| < 60 | P3 | Low priority; cover opportunistically |

### Scoring heuristics

Severity signals:
- **High (S=9)**: security, privacy, data loss, bricking, boot, pairing, OTA, power loss
- **Medium (S=6)**: sync, recovery, reboot, reconnect, permissions, remote, voice, exceptions
- **Low (S=3)**: compatibility, UI, display, animation, exploratory, diagnostics

Probability signals:
- **High (P=8)**: multi-end, concurrent, race conditions, state machines, boundary, weak-network
- **Medium (P=5)**: parameterized features, mode switching, timers, caching, persistence
- **Boost (+2)**: shallow node (no children but should have), low confidence

Detectability signals:
- **Hard to detect (D=9)**: race conditions, memory leaks, timing issues, intermittent, drift
- **Medium (D=6)**: recovery paths, reboot, reconnect, sync delays, degradation

### Usage

```bash
# Print top-20 risk report
python3 scripts/risk_scorer.py scope-tree.json

# Output annotated tree with risk_score on each node
python3 scripts/risk_scorer.py scope-tree.json --output scored-tree.json

# Machine-readable JSON report
python3 scripts/risk_scorer.py scope-tree.json --json-report --top 30
```

The annotated output writes `risk_score` and auto-computed `priority` back onto each node, ready for export to `.xmind`.
