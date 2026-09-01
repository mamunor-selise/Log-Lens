---
description: Pick up a Jira ticket for a sprint — branch, fetch, explore, plan, await approval, implement with tiered validation, commit per checklist item
---

Procedure for `/ticket <jira-url> <sprint-number>`.
Example: `/ticket https://mamunorselise.atlassian.net/browse/LL-1 sprint-1`

Constants and commands are defined in this repo's `AGENTS.md` — use them by name. `GUARDRAILS.md` overrides everything here.

> This file is identical in both the frontend and backend repos. Per-stack differences live in `AGENTS.md` only. If you edit this file, copy it to the counterpart repo unchanged.

---

### 1. Parse

- `TICKET_KEY` ← the segment after `/browse/`.
- Normalize the sprint argument to `sprint-N` if given as a bare number.
- Compute the branch from `BRANCH_PATTERN`.

### 2. Establish repo scope

Determine whether this ticket needs **this repo only** or **both repos**, from the ticket description and the exploration in step 4.

- **This repo only** → proceed normally.
- **Both repos** → follow the cross-repo rules in `AGENTS.md`. Same branch name in both. Each repo gets its own plan file, its own commits, and its own PR. Note the counterpart in the plan's Counterpart field.
- **Actually the other repo's work** → say so and stop. Don't implement a backend change from the frontend repo, or vice versa, even if both are open in the workspace.

### 3. Branch

- `git fetch origin`
- If `origin/{branch}` exists → checkout, pull.
- Else → create from latest `origin/{BASE_BRANCH}`, push with `-u`.
- Report which case occurred.

### 4. Fetch the ticket

Via the Atlassian MCP connector: summary, description, acceptance criteria, status, labels, linked issues. On failure, stop and report — see the fabrication guardrail.

### 5. Explore (parallelize this)

Read-only, and the slowest phase — fan out to subagents in Manager view, one question each:

- Where does the relevant logic live in **this** repo?
- What tests already cover it, and what contract do they assert?
- Any prior commits or PRs referencing `TICKET_KEY` or this area?
- What conventions does the surrounding module follow?
- Does this cross the repo boundary — an API contract, DTO shape, or endpoint either side depends on?

That last question decides repo scope. Get it right here; discovering it mid-implementation is expensive.

### 6. Write the plan → **STOP**

- Copy `.agents/plans/TEMPLATE.md` to `PLAN_PATH` and fill every section.
- Every AC gets a traceability row. Every checklist item names its test and target file.
- Split open questions into **blocking** and **assumptions**. Write `none` explicitly where there are none.
- If cross-repo: state the contract at the boundary precisely (endpoint, payload shape, status codes) and which side owns it.
- Set status to `awaiting-approval`.
- Post a condensed version in chat (summary, approach, checklist, blocking questions) and link the file.

**Stop here.** No source file is created or modified until the user approves or answers the blocking questions. Writing the plan file itself is the only permitted write.

### 7. Implement — tiered validation loop

Set status to `in-progress`. Then, for each checklist item in order:

1. Write or update the test for that behavior.
2. Implement the change.
3. **Inner tier:** run `CMD_TEST_ONE` scoped to that file only.
4. Red → fix and re-run. After `MAX_FIX_ATTEMPTS` consecutive failures, stop and ask.
5. Green → tick the item in `PLAN_PATH`, append to the log, and **commit** (`COMMIT_FORMAT`).

At the end of each plan section, run the **section tier**: the containing test directory / test project.

Watch the diff size against `MAX_DIFF_LINES` as you go.

### 8. Self-review

Before the first commit — and again at the end — read the full working diff against the plan and the ACs. Report anything out of scope, leftover debug output, incidental reformatting, or dependency/lockfile changes.

### 9. Gate tier

Run `CMD_LINT` → `CMD_TYPECHECK` → `CMD_BUILD` (per this repo's rules on when the build is required) → `CMD_TEST_FULL`. All must pass.

Tick the traceability table's Verified column only for ACs actually covered by a passing automated test.

### 10. Report

Set status to `verified`. Summarize:

- Branch, and the commit list (one per checklist item)
- Files changed
- Gate results
- **AC coverage**, including any AC still needing manual/QA verification
- Cross-repo state, if applicable: what the counterpart repo still owes, and the merge order
- Anything raised for follow-up

Then suggest `/verify` and `/pr` — do not run them automatically.

---

**If interrupted at any point after step 6, `/resume` picks up from `PLAN_PATH`.**