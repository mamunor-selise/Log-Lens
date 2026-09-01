---
description: Resume an in-progress ticket from its plan file — finds the first unchecked item and continues the validation loop
---

Procedure for `/resume [ticket-key]`. Makes long tickets survivable across context compaction and session restarts.

> Identical in both repos. Resuming is always scoped to **this** repo's plan file, even if the ticket spans both.

### 1. Locate the plan

- Ticket key from the argument, or inferred from the current branch (`sprint-*/{TICKET_KEY}`).
- Read `PLAN_PATH`. If it doesn't exist, stop — tell the user to run `/ticket` instead. Don't reconstruct a plan from the diff.

### 2. Re-establish context

Read, in this order:

1. The plan's summary, approach, traceability table, and checklist.
2. The log section — the last entry is where work stopped.
3. `git log {BASE_BRANCH}..HEAD` — the commits actually made so far.
4. `git status` and the working diff — any uncommitted work in flight.

### 3. Reconcile plan against reality

The plan can disagree with the repo if a session died mid-item. Check both directions:

- **Ticked items with no corresponding commit** → the work may be lost. Verify it's actually present in the code before trusting the tick.
- **Commits with no ticked item** → the work happened but wasn't recorded. Tick it and log it.
- **Uncommitted changes** → determine which checklist item they belong to and finish that item first.

Report any mismatch rather than silently correcting it.

### 4. Confirm before resuming

State: current status, items done, the next item, and any mismatch from step 3.

If the plan status is still `awaiting-approval`, the gate was never cleared — **stop and wait for approval.** Do not start implementing.

### 5. Continue

Re-enter the `/ticket` step 7 loop at the first unchecked item. Same rules: inner tier per item, tick and commit on green, section tier at section end.

Finish with `/ticket` steps 8–10 (self-review, gate tier, report). A resumed session still owes the **full** gate even if a previous session ran it — the base branch and dependencies may have moved since.
