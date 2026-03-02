---
name: user-acceptance
description: Use when finishing a ticket or pull request and the user asks to validate, demo, or sign off on delivered behavior, including non-user-facing changes.
---

# Running User Acceptance Walkthroughs

## Overview

Acceptance at delivery time should be experiential, not just a test summary.
Primary goal: help the human directly see and feel what changed before merge.
If work is not user-facing, run and show executable proof with user-impact translation.
For user-facing work, run an end-to-end demo with `agent-browser` skill (use `electron` skill if an electron app) as the default validation method.

## When to Use

- End of PR/ticket prompts: "UAT", "verify", "walk me through", "show what changed", "can we merge?"
- Sign-off requests where confidence requires direct observation, not only CI output
- Mixed work (UI + backend/infrastructure) that needs both walkthrough and proof

Do not use for mid-implementation debugging or code-quality review without acceptance intent.

## Decision Flow

```dot
digraph uat_flow {
  "End-of-ticket or PR acceptance?" [shape=diamond];
  "Any user-facing behavior changed?" [shape=diamond];
  "Can agent execute proof locally?" [shape=diamond];
  "Run agent-browser end-to-end demo" [shape=box];
  "Run executable demo evidence" [shape=box];
  "Provide reproducible proof plan + user run steps" [shape=box];

  "End-of-ticket or PR acceptance?" -> "Any user-facing behavior changed?" [label="yes"];
  "Any user-facing behavior changed?" -> "Run agent-browser end-to-end demo" [label="yes"];
  "Any user-facing behavior changed?" -> "Can agent execute proof locally?" [label="no"];
  "Can agent execute proof locally?" -> "Run executable demo evidence" [label="yes"];
  "Can agent execute proof locally?" -> "Provide reproducible proof plan + user run steps" [label="no"];
}
```

## Step-by-Step Workflow

1. Identify scope and mode.
   - Confirm what behavior is being accepted.
   - Declare `Mode`: `user-facing`, `non-user-facing`, or `mixed`.
2. Define acceptance slices.
   - Break validation into small slices (2-5), each with clear pass/fail criteria.
3. Execute validation.
   - `user-facing`: run an end-to-end demo using `agent-browser` (or `electron` for Electron apps).
   - `non-user-facing`: run executable proof commands (tests, logs, traces, metrics).
   - `mixed`: run user-facing demo first, then technical proof tied to the same outcome.
4. Capture evidence.
   - Save screenshots/video for user-facing slices.
   - Save exact commands and key output lines for technical slices.
5. Report results to the user.
   - Start with overview and scope bullets.
   - List each slice with explicit `Pass`/`Fail`.
   - End with `Recommendation`: `GO`, `GO with follow-ups`, or `NO-GO`.
6. If recommendation is `GO` or `GO with follow-ups`, update the ticket with UAT evidence.
   - This is mandatory after successful completion.
   - Include mode, slice-by-slice results, evidence paths/links, and recommendation.
   - If no ticket is known, ask for the ticket ID before closing UAT.

## Mode Playbooks

### User-facing mode

- Use `agent-browser` (or `electron`) skill to execute and demonstrate the full user flow end-to-end.
- Start with `agent-browser` (or `electron`) skill setup/connection commands, then perform each scenario with concrete commands (`open`, `snapshot`, `click`, `fill`, `wait`, `screenshot`).
- Provide explicit run commands and expected checkpoints for each step.
- Capture demo evidence (at minimum screenshots; include recording when useful).
- Report pass/fail per scenario based on observed UI behavior from the live demo.

- Example:

```bash
# Step 1: Start app with remote debugging enabled
npm run dev -- --remote-debugging-port=9222
# Step 2: Connect agent-browser and inspect UI
npx agent-browser connect 9222
npx agent-browser tab 0
npx agent-browser snapshot -i
# Step 3: Execute scenario and capture evidence
npx agent-browser click @e1
npx agent-browser fill @e2 "sample prompt"
npx agent-browser click @e3
npx agent-browser wait 1500
npx agent-browser screenshot /tmp/uat-scenario-1.png
```

- Guide one scenario at a time: user action -> expected result -> what to report.
- Wait for user confirmation before moving to next scenario.
- Ask at least one "does this feel right?" UX confidence question.
- Prefer hands-on preview over abstract summary.

### Non-user-facing mode

- Execute demonstrable proof: targeted tests, runnable commands, logs, traces, or metrics.
- Show exact commands and key result lines (not raw dump).
- Translate technical output into user impact.
- Offer one short trust-check the user can run independently.

### Mixed mode

- Run user-facing layer first via `agent-browser` end-to-end demo.
- Then run backend/infrastructure proof tied to the same user outcome.

## Ticket Update (Required on Success)

After `GO` or `GO with follow-ups`, post a ticket comment in the project system of record (Linear/Jira/GitHub issue) with:

1. UAT verdict (`GO` / `GO with follow-ups`)
2. Scope validated (2-5 bullets)
3. Mode used (`user-facing` / `non-user-facing` / `mixed`)
4. Slice-by-slice pass/fail summary
5. Evidence links or file paths (screenshots, videos, logs)
6. Commands run (for non-user-facing or mixed technical slices)
7. Any follow-ups or residual risks

Do not mark acceptance complete until this ticket update is posted.

## Quick Reference

| Mode            | First step                   | Evidence required                         | Done when                                 |
| --------------- | ---------------------------- | ----------------------------------------- | ----------------------------------------- |
| user-facing     | Run `agent-browser` scenario 1 | `agent-browser` command trace + screenshots/video + observed behavior | User confirms pass/fail for all scenarios |
| non-user-facing | Run proof command(s)         | Command output + impact translation       | Reproducible evidence reviewed            |
| mixed           | User scenario first via `agent-browser` | Both `agent-browser` demo evidence and technical proof | Both layers accepted                      |

## Common Mistakes

- Dumping a static checklist with no interaction
- Reporting only test counts with no demonstration
- Skipping `agent-browser` demo for user-facing changes
- Skipping non-UI demo because there is no frontend change
- Declaring merge readiness before collecting explicit pass/fail signals

## Rationalization Table

| Excuse                                             | Reality                                                                          |
| -------------------------------------------------- | -------------------------------------------------------------------------------- |
| "No UI changes, so UAT is just unit tests."        | Non-user-facing work still needs demonstrable proof and user-impact explanation. |
| "We are in a rush, give a fast merge checklist."   | Time pressure increases need for clear GO/NO-GO evidence.                        |
| "I already summarized everything; that is enough." | Summaries do not replace user experience or executable demonstration.            |
| "User can test later after merge."                 | Acceptance belongs before merge unless explicitly deferred by user.              |

## Red Flags - Stop and Correct

- You are about to send only a summary/checklist.
- You cannot point to any observed behavior or executed proof.
- You are treating CI green status as equivalent to acceptance.
- You are asking for merge without an explicit acceptance signal.
