---
name: incremental-development
description: Use when starting new features, making changes, or implementing tasks - enforces small incremental changes, immediate testing, and continuous integration with quality gates
---

# Incremental Development

## Overview

Small changes that compile and pass tests beat big-bang releases every time. This skill enforces incremental progress with strict quality gates.

**Core principle:** Every change is a potential regression. Minimize change surface. Verify immediately.

## When to Use

- Starting any new feature or task
- Making changes to existing code
- Implementing bug fixes
- Refactoring code
- Adding tests

## The Incremental Loop

```
Change → Test → Verify → Commit → Repeat
```

**Never do:**
- Multiple changes before testing
- "I'll test later" mentality
- Bundling unrelated changes

## Quality Gates

Every increment MUST pass:

1. **Compile/Parse** - Code must be syntactically valid
2. **Tests** - All existing + new tests pass
3. **Coverage** - New code requires >80% test coverage
4. **Linting** - No formatter/linter warnings

## Small Change Philosophy

**Good:**
- "Add validation to user input function"
- "Extract error handling to helper"
- "Add one test for the new parameter"

**Too big:**
- "Refactor the entire auth system"
- "Add user management module"
- "Fix all the bugs"

**If a task feels too large:** Break it into smaller steps. Use the writing-plans skill to decompose.

## Implementation Pattern

### 1. Understand First

Before writing any code:

```
- Find 3 similar implementations in codebase
- Identify common patterns and conventions
- Use same libraries/utilities
- Follow existing test patterns
```

### 2. Make the Smallest Change

```
- One file at a time (when possible)
- One function at a time
- One test at a time
```

### 3. Test Immediately

```bash
# Run tests after every change
pytest tests/ -v --cov=src --cov-report=term-missing
# or
npm test -- --coverage
```

### 4. Verify Coverage

```
Target: >80% coverage
If coverage drops: Write more tests or simplify the change
```

### 5. Commit When Green

```
- All tests passing ✓
- Coverage maintained ✓
- No linter warnings ✓
- Clear commit message ✓
```

## Test Failure Protocol

When tests fail:

1. **Read the output** - Don't skip past errors
2. **Reproduce locally** - Ensure you can trigger the failure
3. **Analyze the log** - Find root cause (use systematic-debugging if needed)
4. **Fix the issue** - One fix at a time
5. **Re-run tests** - Verify fix works
6. **Commit the fix** - Document what was broken

**Never:**
- Ignore test failures
- "It's just a flaky test"
- Commit with failing tests
- Disable tests instead of fixing

## Git Workflow

### Commit Size

**Each commit is ONE logical change:**
- ✓ "Add user validation"
- ✓ "Fix null pointer in auth"
- ✓ "Extract date helper"

**Not:**
- ✗ "Add auth and fix bugs"
- ✗ "Refactor and improve"
- ✗ "Various changes"

### Commit Message Format

```
<type>: <short description>

<body (if needed)>
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`

## Decision Framework

When unsure about approach, choose based on:

1. **Simplicity** - Simplest solution that works
2. **Reversibility** - Easy to undo if wrong
3. **Consistency** - Matches project patterns
4. **Testability** - Can be tested in isolation
5. **Readability** - Clear intent over clever code

## Red Flags - STOP

- Change affects >5 files (break it down)
- "I'll add tests after" (tests first)
- Coverage dropping below 80%
- "This is quick, don't need process"
- Multiple unrelated changes bundled

## Related Skills

- **superpowers:systematic-debugging** - When tests fail and root cause unclear
- **superpowers:test-driven-development** - For writing tests before implementation
- **superpowers:writing-plans** - When task is too large to do incrementally
- **superpowers:verification-before-completion** - Final check before claiming done

## Quick Reference

| Step | Action | Gate |
|------|--------|------|
| 1 | Make small change | <5 files |
| 2 | Write/update tests | Coverage >80% |
| 3 | Run full test suite | All green |
| 4 | Check linting | No warnings |
| 5 | Commit | Clean history |
