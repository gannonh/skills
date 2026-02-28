---
name: gh-address-comments
description: Help address review/issue comments on the open GitHub PR for the current branch using gh CLI; verify gh auth first and prompt the user to authenticate if not logged in.
metadata:
  short-description: Address comments in a GitHub PR review
---

# PR Comment Handler

Guide to find the open PR for the current branch and address its comments with gh CLI. Run all `gh` commands with elevated network access.

Prereq: ensure `gh` is authenticated (for example, run `gh auth login` once), then run `gh auth status` with escalated permissions (include workflow/repo scopes) so `gh` commands succeed. If sandboxing blocks `gh auth status`, rerun it with `sandbox_permissions=require_escalated`.

## Step 1: Inspect comments needing attention

- Run `<path-to-skill>/scripts/fetch_comments.py` which will print out all the comments and review threads on the PR

## Step 2: Enumarate issues identified in comments and review threads

- Number all the review threads and comments 
- Provide a short summary of each "issue candidate," including any suggested fixes from the reviewer

## Step 3: Identify actionable issues to address

- For each issue candidate, analyze against the codebase to distinguish actionable items from false positives or comments that do not require code changes (for example, questions, suggestions, or style comments).

## Step 4: Apply fixes to all actionable issues

- Use TDD when possible: write a failing test that captures the issue, then apply the fix to make the test pass.

## Step 5: Run checks, commit and push changes

- After applying fixes, run the relevant tests and checks locally to confirm the issue is resolved.
- Summarize the changes made, commit with a clear message referencing the PR and issue numbers, and push the changes to the PR branch.

### Step 5: Monitor CI Actions and address any new failures

- After pushing, monitor the PR's CI checks for any new failures that may arise from the changes.
- If new failures occur, use the `gh-fix-ci` skill to analyze the CI logs, identify the root cause, and apply necessary fixes.

Notes:

- If gh hits auth/rate issues mid-run, prompt the user to re-authenticate with `gh auth login`, then retry.
