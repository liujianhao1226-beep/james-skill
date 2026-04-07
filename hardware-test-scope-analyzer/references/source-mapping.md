# Source mapping for smart hardware test-scope analysis

Use this file to decide what each artifact is good for and how much weight it should carry.

## Source roles

| Source type | Best for extracting | Typical traps | How to use it |
| --- | --- | --- | --- |
| Existing XMind / current scope doc | what is already covered, current test organization, missing branch depth | branch names may be generic, outdated, or inconsistent with latest version | treat as baseline, not source of truth for product scope |
| PRD / MRD / requirement spec | committed features, user journeys, operating modes, version boundaries, exclusions | may lag implementation details or omit low-level recovery behavior | use to decide what should exist in the scope |
| Requirement matrix / parameter table | feature lists, mode lists, numeric ranges, defaults, units, actors, module ownership | values may drift across versions; table can look complete but miss state transitions | use to expand parameterized and mode-based branches |
| Interface / protocol / API doc | fields, states, error codes, retries, timeout, sync rules, offline behavior | may reflect backend or firmware intent without matching final UX | use to expand state, exception, sync, and compatibility coverage |
| Defect list / bug tracker export | repeated weak areas, fragile regressions, misunderstood ownership, bad interactions | bug data is noisy and skewed toward what was already tested | use to raise priority and identify weak branches |
| Test report / iteration summary | what was tested recently, remaining open issues, known unstable areas | report scope is constrained by that iteration and does not equal full coverage | use to detect over-focus or chronic blind spots |
| Release note / version scope note | current-release inclusion, removal, deferment, risk acceptance | may be incomplete or too high level | use to separate real misses from out-of-scope items |
| Competitor analysis / benchmark notes | scenario inspiration, parity checks, UX alternatives, hidden expectations | competitor features are not automatic commitments | treat as benchmark inspiration unless product sources confirm them |

## Conflict handling

When sources disagree, do not silently pick one. State the conflict and classify it.

### Recommended precedence

1. **version scope / signed requirement / current PRD** for whether a feature belongs in the current release
2. **requirement table / interface spec** for parameters, states, fields, and behavior details
3. **defects / recent reports** for risk and priority
4. **competitor materials** for optional expansion ideas

## Practical extraction hints

### From PRD or requirement docs

Always try to extract these buckets:
- user-visible features
- modes or scenes
- parameters and ranges
- actors and permissions
- dependencies on network, cloud, sensors, or accessories
- explicit exclusions or future-version notes

### From interface docs

Always look for:
- request / response fields
- enum values and state transitions
- error codes
- timeout and retry strategy
- sync and reporting cadence
- local vs cloud behavior

### From defect and report materials

Cluster by symptom instead of reading issue-by-issue only:
- state sync mismatch
- missing boundary checks
- recovery failure after reboot or reconnect
- UI and backend state inconsistency
- mixed-control conflicts across device / app / cloud / voice
- version upgrade or migration regressions

## What counts as strong evidence for adding a branch

A recommendation is strong when at least one of these is true:
- the feature is explicitly present in PRD or requirement tables
- the interface doc defines fields or states that the outline does not cover
- multiple defects or reports cluster around the same missing dimension
- the current outline has a shallow generic node while evidence shows several concrete subdomains

## What belongs under version boundary instead of missing scope

Move an item to **version boundary / pending confirmation** when:
- the feature is marked future, deferred, removed, or not in this release
- the only evidence is a competitor benchmark
- evidence conflicts and current-release ownership is unclear
