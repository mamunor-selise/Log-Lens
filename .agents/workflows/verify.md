---
description: Run all verification gates for the current ticket and report acceptance-criteria coverage — no code changes
---

Procedure for `/verify [ticket-key]`. Read-and-run only: **this command never modifies source code.** If a gate fails, report it — don't fix it here. Fixing happens in `/ticket` or `/resume`.

> Identical in both repos. Per-stack command mappings and extra checks live in `AGENTS.md` / `GUARDRAILS.md`.

### 1. Setup

- Ticket key from argument or branch name.
- `git diff {BASE_BRANCH}...HEAD --name-only --stat` → file count and churn, for the diff-size check.
- Read `PLAN_PATH` for the traceability table.

### 2. Gates

Run in this order, stopping the chain if an earlier gate makes later results meaningless:

| Order | Command | On failure |
|-------|---------|-----------|
| 1 | `CMD_LINT` | Report the violations. Do **not** run `CMD_LINT_FIX` — that's a code change, and this command doesn't make those. |
| 2 | `CMD_TYPECHECK` | Report the errors. |
| 3 | `CMD_BUILD` | Report. If it fails for environment reasons (missing secrets/env vars), label it an **environment** problem, not a code problem. |
| 4 | `CMD_TEST_FULL` | Report failures by name. |

If the build fails, don't report test results at all when the test command depends on build output — they're meaningless.

Also run this repo's **pre-commit greps** listed in `AGENTS.md` (focused-test markers, debug output, unreferenced TODOs) against the diff.

### 3. Regression triage

For each failure, classify:

- **Caused by this branch** → blocks done.
- **Pre-existing** → prove it. Run the same test on `BASE_BRANCH` (worktree or stash) and show it fails identically. An unproven "pre-existing" claim is treated as caused by this branch.

### 4. AC coverage

For each AC in the plan's traceability table:

- ☑ only if a **passing** automated test covers it.
- Otherwise ☐, with the reason: not implemented / test failing / manual QA only.

### 5. Cross-repo check

If the plan names a counterpart repo:

- State whether the counterpart's work is done, in review, or not started.
- If this repo's changes depend on a contract the counterpart hasn't merged, flag it — this repo may pass all gates and still be unmergeable on its own.

### 6. Report

```
Repo:       {this repo}
Ticket:     {TICKET_KEY}
Diff:       N files, M lines  (limit: MAX_DIFF_LINES)

Gates       lint ✓ · typecheck ✓ · build ✓ · tests ✗ (2 failed)
Greps       clean | <findings>

Failures    <names, caused-by-branch vs. proven pre-existing>

AC coverage
  AC1 ☑ test_name
  AC2 ☐ manual QA — no automated coverage

Cross-repo  none | counterpart {status}, merge order: {which first}

Verdict:    READY FOR PR | BLOCKED — <reason>
```

Only `READY FOR PR` clears the way for `/pr`. Anything else, say what has to happen first. Update the plan status to `verified` only on a clean pass.
