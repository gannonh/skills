---
name: finalize
description: Finalize the current feature branch by running the `simplify` pass and `strict-quality-review` pass in order, each through its own subagent, automatically accepting in-scope fixes and committing after each phase. Use when the user says finalize, finish this branch, prep for PR, polish and review, run final cleanup, or asks to combine `/simplify` with `/strict-quality-review` before shipping.
---

# Finalize

Use this skill to finish a feature branch with two ordered passes:

1. Run `simplify` on the current branch and commit all fixes.
2. Run `strict-quality-review` on the current branch, address found issues, and commit all fixes.

The parent agent owns orchestration, acceptance, commits, and final reporting. Each pass must run in its own subagent so the cleanup and review happen from focused execution contexts.

## Assumptions

- The scope is the current branch against the repository's default base branch unless the user names a different base.
- The user has authorized automatic acceptance of changes produced by the two passes when they are in scope, behavior-preserving, and validation passes.
- Stop and ask before accepting product behavior changes, broad architecture changes outside the branch's intent, dependency changes, migrations, generated-file churn, or changes that touch secrets or credentials.

## Pre-flight

1. Confirm you are in a git repository.
2. Inspect:
   - `git status --short`
   - the current branch name
   - the likely base branch, usually `origin/main`, `main`, `origin/master`, or `master`
   - the branch diff against that base
3. If the working tree contains unrelated user changes that are clearly outside the feature branch, stop and ask how to handle them.
4. Identify the harness's general-purpose subagent mechanism, such as a delegate, worker, task, or general-purpose agent. Use the generic subagent available in the current environment rather than a harness-specific recipe.
5. Resolve the full absolute `SKILL.md` path for each dependency: `simplify` and `strict-quality-review`.
6. If subagents or either dependency skill file is unavailable, stop and report the missing capability. Do not emulate this workflow entirely in the parent session.

## Phase 1: `simplify` subagent

Spawn a subagent and give it the full absolute path to the `simplify` skill file. Do not inline, summarize, or reinterpret the skill content for the subagent.

Use this prompt for the phase 1 subagent, replacing `<SIMPLIFY_SKILL_PATH>` with the resolved absolute path to the `simplify` `SKILL.md` file:

```text
Finalize phase 1 for the current feature branch.

First read the `simplify` skill file at this exact path:

<SIMPLIFY_SKILL_PATH>

Then follow that skill's instructions on the current branch diff. Refine recently modified code for clarity, consistency, and maintainability while preserving behavior.

Scope:
- Current branch changes against the repository base branch.
- Do not expand product scope.
- Do not perform the strict quality review phase.
- Do not commit. The parent agent will inspect and commit accepted changes.
- Do not launch other subagents.

Acceptance:
- Apply safe, in-scope simplifications directly.
- Do not ask the user to accept each safe cleanup change.
- Stop and report any change that would alter behavior or exceed the branch intent.

Validation:
- Run focused formatting, lint, typecheck, or tests that match the changed files when available.
- Report commands run, results, changed files, and any remaining risks.
```

When the subagent completes:

1. Inspect `git status --short` and `git diff`.
2. Reject or revert only changes that violate scope or validation. Keep safe `simplify` changes.
3. Run any missing focused validation that is needed to trust the diff.
4. Commit the phase 1 changes if any exist.

Commit guidance:

- Stage files explicitly. Do not use `git add .` or `git add -A`.
- Use a conventional commit message, usually `refactor: simplify branch implementation` or a more specific scoped variant.
- If there are no changes, do not create an empty commit. Record that phase 1 produced no commit.

## Phase 2: strict quality review subagent

Spawn a separate subagent and give it the full absolute path to the `strict-quality-review` skill file. Do not inline, summarize, or reinterpret the skill content for the subagent. This subagent audits the post-`simplify` branch and applies fixes for accepted findings.

Use this prompt for the phase 2 subagent, replacing `<STRICT_QUALITY_REVIEW_SKILL_PATH>` with the resolved absolute path to the `strict-quality-review` `SKILL.md` file:

```text
Finalize phase 2 for the current feature branch.

First read the `strict-quality-review` skill file at this exact path:

<STRICT_QUALITY_REVIEW_SKILL_PATH>

Then follow that skill's instructions on the current branch diff after the `simplify` phase. Perform a strict maintainability review focused on abstraction quality, file growth, spaghetti-condition growth, type boundaries, canonical helpers, modularity, and code-judo simplifications.

Scope:
- Current branch changes against the repository base branch.
- Address high-confidence issues directly when the fix is in scope and behavior-preserving.
- Do not expand product scope or rewrite unrelated code.
- Do not commit. The parent agent will inspect and commit accepted changes.
- Do not launch other subagents.

Acceptance:
- Apply safe, in-scope fixes directly.
- Do not ask the user to accept each safe cleanup change.
- Stop and report blockers when a finding requires a product decision, broad redesign, risky migration, dependency change, or behavior change.

Validation:
- Run focused formatting, lint, typecheck, or tests that match the changed files when available.
- Report findings addressed, findings deferred with reasons, commands run, results, changed files, and any remaining risks.
```

When the subagent completes:

1. Inspect `git status --short` and `git diff`.
2. Accept safe, in-scope strict-review fixes by default.
3. Reject or revert only changes that violate scope, fail validation, or require user approval.
4. Run any missing focused validation that is needed to trust the diff.
5. Commit the phase 2 changes if any exist.

Commit guidance:

- Stage files explicitly. Do not use `git add .` or `git add -A`.
- Use a conventional commit message, usually `refactor: address strict quality review` or a more specific scoped variant.
- If there are no changes, do not create an empty commit. Record that phase 2 produced no commit.

## Final verification

After both phases:

1. Run `git status --short`.
2. Run a final validation command appropriate for the repository when one is discoverable and reasonably bounded, such as lint, typecheck, or targeted tests. If full validation is expensive, say what you ran and what remains unverified.
3. Confirm the branch has no uncommitted finalize changes unless a blocker remains.
4. Summarize:
   - phase 1 commit hash or `no changes`
   - phase 2 commit hash or `no changes`
   - validation commands and results
   - unresolved blockers or deferred issues

## Stop rules

Stop and ask the user before proceeding when:

- a subagent requests a product, architecture, dependency, migration, or behavior decision
- validation fails and the fix is unclear
- the worktree contains unrelated dirty changes that would be swept into finalize commits
- the branch has merge conflicts or cannot identify a reasonable base branch
- required subagent or skill support is unavailable

## Do not

- Do not run both phases in the same subagent.
- Do not run the `strict-quality-review` pass before the `simplify` pass.
- Do not ask the user to approve every safe cleanup change.
- Do not commit with broad staging commands.
- Do not leave subagent-applied fixes uncommitted unless there is a blocker.
- Do not let child subagents launch their own subagent workflows.

## Skills Dependencies

This skill depends on these companion skills:

- `simplify`
- `strict-quality-review`

Before starting phase work, verify both skills are available in the current system and resolve each one to a full absolute `SKILL.md` path. Pass that path to the relevant subagent and instruct the subagent to read the file first. If either skill file is unavailable, stop, alert the user which dependency is missing, and ask for next steps.
