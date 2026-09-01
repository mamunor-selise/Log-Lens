---
description: Open a PR against BASE_BRANCH and comment the link on the Jira ticket — idempotent, aborts if PR and comment both already exist
---

Procedure for `/pr [jira-url-or-ticket-key]`. Runs **after** commits are pushed. Creates no commits.

> Identical in both repos. Scoped to **this** repo only — if the ticket spans both, run `/pr` in each repo separately. The repo label in the comment text is what keeps the two from colliding.

### 1. Resolve

- `TICKET_KEY` from the argument (raw key or full URL), else inferred from the branch (`sprint-*/{TICKET_KEY}`).
- If the branch doesn't match `BRANCH_PATTERN`, stop and ask which ticket this is for.
- `REPO_LABEL` ← from `AGENTS.md` (e.g. `Frontend` / `Backend`).

### 2. Preflight

- `git status` — uncommitted changes → stop and ask. Never auto-commit or discard.
- Local commits not on `origin` → push (no `--force`).
- Confirm `/verify` passed. If it hasn't run, or didn't return `READY FOR PR`, say so and ask before continuing — opening a PR on unverified work wastes reviewer time.

### 3. Check for an existing PR

Query the GitHub/GitLab connector (or `gh pr list` / `glab mr list`) for an **open** PR in **this** repo with head = current branch, base = `BASE_BRANCH`.

- `PR_EXISTS` ← true/false
- `PR_URL` ← the URL, if found

Scope the query to this repo explicitly. With both repos in one workspace, an unscoped query can return the counterpart's PR and produce a false "already exists".

### 4. Check for an existing Jira comment

Fetch comments on `TICKET_KEY`.

- If `PR_EXISTS` → `COMMENT_EXISTS` is true only if some comment contains `PR_URL` **verbatim**.
- If not `PR_EXISTS` → `COMMENT_EXISTS` is false (no PR link exists for a comment to match).

Match on the URL, not on the phrase "PR opened" — otherwise the counterpart repo's comment would read as this repo's.

### 5. Decide

| `PR_EXISTS` | `COMMENT_EXISTS` | Action |
|---|---|---|
| ✓ | ✓ | **Abort.** Report: {REPO_LABEL} PR already exists ({PR_URL}) and is already linked on {TICKET_KEY} — nothing to do. Create nothing, post nothing, modify nothing. **Stop.** |
| ✓ | ✗ | Skip step 6. Post the missing comment (step 7). |
| ✗ | — | Step 6, then step 7. |

### 6. Create the PR

- Execute `node .agents/scripts/create-pr.js "{TICKET_KEY}: {ticket summary}" "{PR body}" "{BASE_BRANCH}" "{TICKET_BRANCH}"` (or `gh pr create`):
  - Automatically loads `GH_TOKEN` from `.env.local` or environment.
  - Base `BASE_BRANCH`, head the ticket branch.
  - Title: `{TICKET_KEY}: {ticket summary}`
  - Body: Drawn from `.agents/plan/{TICKET_KEY}.md` plan summary, checklist, and verification results.
  - Normal PR, not draft, unless told otherwise. **Never enable auto-merge.**
  - Capture `PR_URL` from the command output.
- `PR_URL` ← the new PR's URL.

### 7. Comment on Jira

- Text: `{REPO_LABEL} PR opened: {PR_URL}`
- Show the exact text in chat before posting.
- Post via the Jira connector, then **confirm** it landed. Never report success without confirmation.

### 8. Report

`TICKET_KEY` · `REPO_LABEL` · branch · PR status (created / already existed / skipped) · comment status (posted / already existed / skipped) · final `PR_URL`. Update the plan status to `pr-open`.

If cross-repo and the counterpart PR isn't open yet, remind the user to run `/pr` there too.
