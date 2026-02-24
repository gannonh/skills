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
- [ ] Step 2: Fetch Open Review Comments
- [ ] Step 3: Run PR Review
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

### Step 2: Fetch Open Review Comments

Run all `gh` commands with elevated network access.

Prereq: ensure `gh` is authenticated (for example, run `gh auth login` once), then run `gh auth status` with escalated permissions (include workflow/repo scopes) so `gh` commands succeed. If sandboxing blocks `gh auth status`, rerun it with `sandbox_permissions=require_escalated`.

## 1) Inspect comments needing attention
- Run `scripts/fetch_comments.py` which will print out all the comments and review threads on the PR

## 2) Ask the user for clarification
- Number all the review threads and comments and provide a short summary of what would be required to apply a fix for it
- Ask the user which numbered comments should be addressed

## 3) If user chooses comments
- Apply fixes for the selected comments

## 4) Resolve/reply to comments
- As you address comments, close them out in the GitHub UI and reply to reviewers with your changes and any questions for clarification.
- For those comments not addressed, reply to reviewers with your reasoning and ask for any clarification if needed.

Notes:
- If gh hits auth/rate issues mid-run, prompt the user to re-authenticate with `gh auth login`, then retry.

Once the open review comments are addressed, proceed to Step 3:

### Step 3: Run PR Review & Fix Issues

Run comprehensive PR review using 1-5 specialized instruction sets. Depending on your capabilitites, run as:

  1. **Agent Team** - parallel agents for each review type, then aggregate results
  (or, if agent teams not supportedL)
  1. **Sub-agents** - parallel instructions for each sub-agent, then aggregate results
  (or, if neither supported)
  1. **Sequential instructions** - run each review type one after another 

1. Determine which to run based on the scope of the PR. The following are available to use at your discretion:

- **code-reviewer**: Code quality, bugs, logic errors → `./references/code-reviewer-instructions.md`
- **code-simplifier**: Code complexity and duplication → `./references/code-simplifier-instructions.md`
- **comment-analyzer**: Comment accuracy → `./references/comment-analyzer-instructions.md`
- **failure-finder**: Error handling patterns → `./references/failure-finder-instructions.md`
- **pr-test-analyzer**: Test coverage completeness → `./references/pr-test-analyzer-instructions.md`
- **type-design-analyzer**: Type design quality → `./references/type-design-analyzer-instructions.md`

**For each issue found:**

2. Compile a list of issues categorized by severity and present to the user with your recommendations.

   1. **Critical issues** - Must fix immediately
   2. **Important issues** - Should fix before merge
   3. **Suggestions** - Consider fixing

3. Ask the user how they would like to proceed.

4. Address the selected comments and issues.

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
