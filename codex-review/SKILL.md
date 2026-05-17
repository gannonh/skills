---
name: codex-review
description: "Codex code review closeout: local dirty changes, PR branch vs main, parallel tests."
---

# Codex Review

Run Codex's built-in code review as a closeout check. This is code review (`codex review`), not Guardian `auto_review` approval routing.

Use direct `codex review` CLI commands only. Keep the exact review command visible so the review target and result are auditable.

Use when:
- user asks for Codex review / autoreview / second-model review
- after non-trivial code edits, before final/commit/ship
- reviewing a local branch or PR branch after fixes

## Contract

- Treat review output as advisory. Never blindly apply it.
- Verify every finding by reading the real code path and adjacent files.
- Read dependency docs/source/types when the finding depends on external behavior.
- Reject unrealistic edge cases, speculative risks, broad rewrites, and fixes that over-complicate the codebase.
- Prefer small fixes at the right ownership boundary; no refactor unless it clearly improves the bug class.
- Keep going until the final direct `codex review` command returns no accepted/actionable findings.
- If a review-triggered fix changes code, rerun focused tests and rerun Codex review.
- Never switch or override the review model. If the review hits model capacity, retry the same command a few times with the same model. If it hits sandbox/permission limits, surface the exact limit, resolve it explicitly, and retry the same review target.
- Stop as soon as the review command exits 0 with no accepted/actionable findings. Do not run an extra review just to get nicer closeout wording, a second opinion, or clearer summary text.
- If rejecting a finding as intentional/not worth fixing, add a brief inline code comment only when it explains a real invariant or ownership decision that future reviewers should know.
- Do not push just to review. Push only when the user requested push/ship/PR update.

## Pick Target

Dirty local work:

```bash
codex review --uncommitted
```

Use this only when the patch is actually unstaged/staged/untracked in the current checkout. For committed, pushed, or PR work, review the branch against its base instead. A clean `--uncommitted` review only proves there is no local patch.

Branch/PR work:

```bash
git fetch origin
codex review --base origin/main
```

Do not pass an inline prompt with `--base`; current CLI rejects `--base` + `[PROMPT]` even though help text is ambiguous. If custom instructions are needed, run the plain base review first, then do a local/manual follow-up pass.

If an open PR exists, use its actual base:

```bash
base=$(gh pr view --json baseRefName --jq .baseRefName)
git fetch origin "$base"
codex review --base "origin/$base"
```

Committed single change:

```bash
codex review --commit HEAD
```

## Parallel Closeout

Format first if formatting can change line locations. Then it is OK to run tests and review in parallel with normal shell jobs:

```bash
sh -c '<focused test command>' &
test_pid=$!

codex review --base origin/main
review_status=$?

wait "$test_pid"
test_status=$?

printf 'codex review status: %s\nfocused test status: %s\n' "$review_status" "$test_status"
test "$review_status" -eq 0
test "$test_status" -eq 0
```

Swap the review command for the correct target, such as `codex review --uncommitted` or `codex review --commit HEAD`.

Tradeoff: tests may force code changes that stale the review. If tests or review lead to code edits, rerun the affected tests and rerun review until no accepted/actionable findings remain. Once that rerun exits cleanly, stop.

## Context Efficiency

Codex review is usually noisy. Default to a subagent filter when subagents are available. Ask it to run the direct `codex review` CLI command and return only:
- actionable findings it accepts
- findings it rejects, with one-line reason
- exact files/tests to rerun
- the exact review command and exit status

Run inline only for tiny changes or when subagents are unavailable.

## Final Report

Include:
- exact review command used
- tests/proof run
- findings accepted/rejected, briefly why
- the clean review result from the final direct `codex review` run, or why a remaining finding was consciously rejected

Do not run another Codex review solely to improve the final report wording. If the final direct review run exited 0 and produced no accepted/actionable findings, report that exact run as clean.
