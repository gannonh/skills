# Reviewing Pull Requests

Run comprehensive PR review and quality checks before merging.

## Objective

Ensure code quality, test coverage, and adherence to project standards.
Output: All review issues addressed, PR ready for merge.

## Context

PR Number: $ARGUMENTS (auto-detect from current branch if not provided)

## Process

Create a structured task list:

- [ ] Step 1: Identify PR to Review
- [ ] Step 2: Fetch Open Review Comments & Fix Issues
- [ ] Step 3: Run PR Review & Fix Issues
- [ ] Step 4: Run Quick Checks
- [ ] Step 5: Present Next Steps

### Step 1: Identify PR to Review

Get the PR number for the current branch:
```bash
GH_PAGER= gh pr view --json number --jq '.number'
```

Then get PR details:
```bash
GH_PAGER= gh pr view --json number,title,state,headRefName,url --jq '"PR #\(.number): \(.title)\nState: \(.state)\nBranch: \(.headRefName)\nURL: \(.url)"'
```

If PR is already merged or closed, inform user and exit.

### Step 2: Fetch Open Review Comments & Fix Issues

Run all `gh` commands with elevated network access.

Prereq: ensure `gh` is authenticated (for example, run `gh auth login` once), then run `gh auth status` with escalated permissions (include workflow/repo scopes) so `gh` commands succeed. If sandboxing blocks `gh auth status`, rerun it with `sandbox_permissions=require_escalated`.

#### 1: Inspect comments needing attention
- Run `./scripts/fetch_comments.py` which will print out all the comments and review threads on the PR. 

**NOTE: the script lives under the skill’s directory, not the current workspace.**

#### 2: Present findings and ask the user (required gate)
- Number all the review threads and comments and provide a short summary of what would be required to apply a fix for each.
- **You MUST then ask the user:** "Which of these comments (by number) should I address? Reply with numbers, 'none', or 'all'."
- Do not assume "none" or skip this question. Do not apply fixes or proceed to Step 3 until the user has answered.

#### 3: If user chooses comments
- Apply fixes only for the comments the user selected (by number). If the user said "none", skip applying fixes.
- Resolve or reply to those threads in the GitHub UI as you address them.

#### 4: Resolve/reply to comments
- As you address comments, close them out in the GitHub UI and reply to reviewers with your changes and any questions for clarification.
- For those comments not addressed (user said "none" or did not select them), reply to reviewers with your reasoning and ask for any clarification if needed.

Notes:
- If gh hits auth/rate issues mid-run, prompt the user to re-authenticate with `gh auth login`, then retry.

**Only after the user has answered which comments to address and you have applied (or skipped) those fixes and resolved/replied in GitHub, proceed to Step 3.**

### Step 3: Run PR Review & Fix Issues

**This step MUST run every time.** Do not substitute a brief manual review or skip it. Run the full review using specialized instruction sets, then aggregate and present by severity before asking the user how to proceed.

Depending on your capabilities, run as:

  1. **Agent Team** – parallel agents for each review type, then aggregate results
  (or, if agent teams not supported)
  2. **Sub-agents** – parallel instructions for each sub-agent, then aggregate results
  (or, if neither supported)
  3. **Sequential instructions** – run each review type one after another

1. Determine which to run based on the scope of the PR. The following are available (use at your discretion):

- **code-reviewer**: Code quality, bugs, logic errors → `./references/code-reviewer-instructions.md`
- **code-simplifier**: Code complexity and duplication → `./references/code-simplifier-instructions.md`
- **comment-analyzer**: Comment accuracy → `./references/comment-analyzer-instructions.md`
- **failure-finder**: Error handling patterns → `./references/failure-finder-instructions.md`
- **pr-test-analyzer**: Test coverage completeness → `./references/pr-test-analyzer-instructions.md`
- **type-design-analyzer**: Type design quality → `./references/type-design-analyzer-instructions.md`

2. **Aggregate results** from all review types, then compile a list of issues categorized by severity and present to the user:

   - **Critical issues** – Must fix immediately
   - **Important issues** – Should fix before merge
   - **Suggestions** – Consider fixing

3. **You MUST ask the user:** "How would you like to proceed? Which issues (by severity or item) should I address?" Do not assume or skip this question. Do not apply fixes until the user has answered.

4. Address the comments and issues the user selected.

5. Close and reply to gh comments as you address them, so reviewers can track progress. If you encounter any issues that require clarification, ask the user for clarification.

6. Commit your changes with a message like "fix: address PR review comments" and push to the branch.

### Step 4: Run Quick Checks

**If changes were made:**

```bash
# Run swiftlint on changed files and fix ANY issues
git diff --name-only origin/main...HEAD -- '*.swift' | xargs -r swiftlint lint --strict

# Run unit test suite to confirm no regressions
./scripts/test.sh unit 1
```

### Step 5: Present Next Steps

```
✅ PR Review Complete

PR #[PR_NUMBER]: [Title]
Branch: [branch_name]

Validation Results:
- PR Review Toolkit: ✅ All issues addressed
- CI Checks: ✅ Passing

Ready for merge when you are.
```

## Success Criteria

- [ ] PR identified and accessible
- [ ] PR review issues addressed
- [ ] All CI checks pass (lint, build, tests, coverage)
- [ ] User knows next steps

## Critical Rules

- **Re-run after fixes** - Confirm issues are resolved before proceeding
- **Don't skip steps** - Each review type catches different issues
- **Final validation required** - Confirm no regressions from fixes
