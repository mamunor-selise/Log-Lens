---
description: Produce a PR-ready summary and reviewer walkthrough from the plan file and commit log
---

Procedure for `/handoff [ticket-key]`. Output goes to `.agents/plans/{TICKET_KEY}.handoff.md` and is consumed by `/pr` step 6 — so the PR body draws on real recorded work instead of being re-derived from `git log` each time.

Read-only with respect to source code. Identical in both repos.

### 1. Gather

- `PLAN_PATH` — summary, approach, traceability table, log, open questions.
- `git log {BASE_BRANCH}..HEAD --oneline` — the commit sequence.
- `git diff {BASE_BRANCH}...HEAD --stat` — files and churn.
- The most recent `/verify` result, if there is one in this session.

### 2. Compose

```md
## {TICKET_KEY} — {summary}

**Jira:** {TICKET_URL}
**Repo:** {this repo} · **Counterpart:** {other repo PR, or none}

### What changed
- {plain-language bullet per checklist item — what and why, not file-by-file}

### Why
{Root cause in 2–3 sentences. A reviewer should understand the problem before reading the diff.}

### How to review
{Ordered reading path — start here, then this. Call out the one or two commits carrying the actual behavior change vs. scaffolding.}

### Testing
- Added/updated: {test names}
- Gates: lint · typecheck · build · full suite — {results}

### AC coverage
| AC | Covered by | Status |
|----|-----------|--------|
| AC1 | `test_name` | ☑ |
| AC3 | manual QA | ☐ needs QA |

### Notes for the reviewer
- {assumptions made at the approval gate}
- {follow-ups raised and deliberately left out of scope}
- {anything still needing manual verification}
- {merge-order dependency, if cross-repo}
```

### 3. Rules

- Bullets describe **behavior**, not files. "Export now skips records with a null org id" beats "modified export.service.ts".
- Every assumption from the plan's open-questions section carries forward — the reviewer needs to see what was decided without them.
- Anything unverified stays visible. Never let a manual-QA AC disappear between plan and PR.
- If cross-repo, state the merge order explicitly and link the counterpart PR if it exists.
- If `/verify` hasn't run clean, say so at the top rather than writing a summary that implies readiness.

### 4. Output

Write the file, show it in chat, and note that `/pr` will use it as the PR body.
