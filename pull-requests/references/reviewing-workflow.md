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
- [ ] Step 2: Run PR Review
- [ ] Step 3: Run Quick Checks
- [ ] Step 4: Update Project State
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

### Step 2: Run PR Review & Fix Issues

Run comprehensive PR review using 1-5 specialized instruction sets. Depending on your capabilitites, run as:

1. **Agent Team** - parallel agents for each review type, then aggregate results
(or, if agent teams not supportedL)
1. **Sub-agents** - parallel instructions for each sub-agent, then aggregate results
(or, if neither supported)
3. **Sequential instructions** - run each review type one after another 

Determine which to run based on the scope of the PR. The following are available to use at your discretion:

- **code-reviewer**: Code quality, bugs, logic errors → `./references/code-reviewer-instructions.md`
- **code-simplifier**: Code complexity and duplication → `./references/code-simplifier-instructions.md`
- **comment-analyzer**: Comment accuracy → `./references/comment-analyzer-instructions.md`
- **failure-finder**: Error handling patterns → `./references/failure-finder-instructions.md`
- **pr-test-analyzer**: Test coverage completeness → `./references/pr-test-analyzer-instructions.md`
- **type-design-analyzer**: Type design quality → `./references/type-design-analyzer-instructions.md`

**For each issue found:**

1. **Critical issues** - Must fix immediately
2. **Important issues** - Should fix before merge
3. **Suggestions** - Consider fixing

**Address ALL issues**, not just critical ones. Continue iterating until no issues remain.

### Step 3: Run Quick Checks

**If changes were made:**

```bash
# Run swiftlint on changed files and fix ANY issues
git diff --name-only origin/main...HEAD -- '*.swift' | xargs -r swiftlint lint --strict

# Run unit test suite to confirm no regressions
./scripts/test.sh unit 1
```

### Step 4: Update Project State

Update STATE.md to record pre-merge completion:

```markdown
Status: PR Review complete - ready for milestone completion
Last activity: [today's date] - PR Review complete (CI + reviews passed)
```

Commit the state update:

```bash
git add .planning/STATE.md
git commit -m "chore: mark PR review complete"
git push
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

- **Fix ALL issues** - Don't skip "minor" issues; they compound
- **Re-run after fixes** - Confirm issues are resolved before proceeding
- **Don't skip steps** - Each review type catches different issues
- **Final validation required** - Confirm no regressions from fixes
