# Verify Workflow

Use this workflow to validate completed implementation against the approved spec, Build completion report, and acceptance criteria.

Verify is the third phase in Plan → Build → Verify. It produces acceptance evidence and a signoff recommendation.

## Required inputs

- Approved spec path.
- Completed implementation or branch to verify.
- Build completion report when available.
- Acceptance criteria from the spec.

If the user asks for UAT, signoff, merge readiness, or proof that work is complete, start here.

## Preferred workflow

Use `/user-acceptance` when it is available. Follow its instructions for evidence capture, UAT reporting, screenshots, recordings, command output, and human test guides.

If `/user-acceptance` is unavailable, stop and alert the user that the preferred verification workflow is missing, then offer to run the standalone workflow below.

The `/user-acceptance` skill is available here if it needs to be installed: <https://github.com/gannonh/skills/tree/main/user-acceptance>

## Standalone Verify workflow

Use this fallback only when `/user-acceptance` is unavailable and the user wants to continue.

### 1. Read source material

Read:

- Approved spec.
- Build completion report.
- Relevant implementation diff.
- Project instructions and verification commands.

Do not rely only on the implementer summary.

### 2. Build an acceptance matrix

Create a checklist from the spec's acceptance criteria.

For each criterion, track:

- Criterion.
- Evidence required.
- Verification method.
- Result: Pass, Fail, Blocked, or Not tested.
- Evidence path, command output, screenshot, URL, log, or notes.

### 3. Run automated checks

Run the verification commands from the spec and repo instructions.

Examples:

```bash
pnpm typecheck
pnpm build
pnpm lint
pnpm test
pnpm test:e2e
```

Use only commands that apply to the current repo. Record exact commands and results.

Do not claim tests pass if a command was skipped, unavailable, or failed.

### 4. Inspect scope and implementation

Compare the implementation to the approved scope:

- Confirm required behavior exists.
- Confirm non-goals were preserved.
- Check for unapproved deviations.
- Check relevant UI, API, data, migration, config, and docs changes.
- Review tests for intent, not just coverage.

### 5. Run manual or UAT checks

When the work has user-visible behavior, run manual checks that match the acceptance criteria.

Use browser automation, CLI commands, screenshots, logs, API calls, or terminal recordings when useful and available.

Save evidence paths when artifacts are produced.

### 6. Classify findings

Classify issues as:

- Blocker: prevents acceptance or risks data loss/security/regression.
- Important: should be fixed before merge or release.
- Minor: does not block acceptance but should be tracked.

If evidence is missing, mark the item as Not tested or Blocked. Do not infer success.

### 7. Produce the verification report

Return a concise report:

```markdown
# Verification Report: <work item>

## Verdict
Pass | Pass with issues | Fail | Blocked

## Summary
<1-3 sentence result>

## Acceptance matrix
- [Pass/Fail/Blocked/Not tested] <criterion>: <evidence>

## Commands run
- `<command>`: <result>

## Manual/UAT evidence
- <artifact path, screenshot, URL, log, or note>

## Issues
### Blocker
- <issue or None>

### Important
- <issue or None>

### Minor
- <issue or None>

## Recommendation
<Ready to merge/sign off, ready after fixes, or not ready>
```

### 8. Update status when appropriate

If verification passes and the user accepts the result, update the spec status from `Implemented` to `Verified` when project instructions allow editing the spec.

If verification fails, leave status unchanged and report what must be fixed.

## Stop and ask

Ask before proceeding when:

- The approved spec cannot be found.
- Acceptance criteria are missing or ambiguous.
- Required credentials, services, or devices are unavailable.
- Verification would run destructive commands.
- The branch has unrelated changes that make evidence unreliable.
