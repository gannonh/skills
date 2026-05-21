# Plan Build Skill Improvement Plan
## Goal
Make `plan-build-verify` a clear three-phase workflow skill:

1. Plan creates an approved spec and build-ready handoff.
  
2. Build executes the approved spec through step-by-step implementation and review gates.
  
3. Verify validates the completed work with acceptance evidence.
  

The skill should stay small at the top level and load detailed workflow instructions from `references/`.
## Decisions
- Default new feature/product/architecture requests to Plan.
  
- Build starts only from an approved spec or explicit user override.
  
- Verify starts when the user asks for UAT, signoff, validation, merge readiness, or proof that work is complete.
  
- Use `/tdd` as the only TDD dependency.
  
- If `/tdd` is unavailable during Build, stop and alert the user.
  
- Remove embedded TDD docs from `plan-build-verify`.
  
- Prefer numbered Markdown steps over complex diagrams, especially in Build.
  
## Proposed changes
### 1. Tighten the top-level router
File: `plan-build-verify/SKILL.md`

- Add phase contracts:
  
  - Plan input: idea, vague request, or new build request.
    
  - Plan output: approved `docs/specs/YYYY-MM-DD-<topic>.md`.
    
  - Build input: approved spec or explicit user override.
    
  - Build output: implemented tasks, commits, review results, and build completion report.
    
  - Verify input: completed implementation plus spec/build report.
    
  - Verify output: acceptance evidence and signoff recommendation.
    
- Add status flow: `Draft → Approved → Implemented → Verified`.
  
- Move the trivial-edit exception into routing rules so small copy/config changes do not over-plan by default.
  
- Keep the file short and point to workflow references.
  
### 2. Make Plan produce a Build handoff
File: `plan-build-verify/references/plan.md`

- Add explicit approval recording after Roughdraft review.
  
- Require approved specs to include a Build handoff section:
  
  - Spec path.
    
  - Approved scope.
    
  - Non-goals.
    
  - Ordered task list.
    
  - Verification commands.
    
  - Required fixtures or test data.
    
  - Known risks.
    
  - Blocking open questions.
    
- State that Build must not start if blocking open questions remain.
  
- Keep Roughdraft review instructions.
  
### 3. Rewrite Build as step-by-step Markdown
File: `plan-build-verify/references/build.md`

- Reduce reliance on the large process diagram.
  
- Convert the core flow into numbered Markdown steps:
  
  1. Build preflight.
    
  2. Extract approved tasks from the spec.
    
  3. Create todo list.
    
  4. For each task, dispatch implementer with full task context.
    
  5. Require `/tdd` for implementation work.
    
  6. Run spec compliance review.
    
  7. Run code quality review.
    
  8. Loop fixes back through reviewers until approved.
    
  9. Mark task complete only after tests and reviews pass.
    
  10. Run final whole-branch review.
    
  11. Write Build completion report.
    
  12. Ask whether to continue to Verify.
    
- Add Build preflight checks:
  
  - Spec status is `Approved`, or user explicitly overrides.
    
  - Worktree state is understood.
    
  - Branch policy is safe.
    
  - Base SHA is captured.
    
  - Verification commands are known.
    
  - Required tools and subagent capability are available.
    
- Add a fallback if subagents are unavailable:
  
  - Preserve the same gates in a single-agent loop.
    
  - Do not skip spec compliance, code quality review, tests, or completion reporting.
    
- Add deviation policy:
  
  - If repo facts invalidate the plan, pause and ask before changing scope.
    
  - Update the spec when implementation decisions materially change.
    
- Add final review remediation:
  
  - Fix final-review issues.
    
  - Re-run final review before declaring Build complete.
    
### 4. Use `/tdd` instead of embedded TDD docs
Files:

- `plan-build-verify/references/build.md`
  
- `plan-build-verify/references/implementer-prompt.md`
  
- `plan-build-verify/references/test-driven-development.md`
  
- `plan-build-verify/references/testing-anti-patterns.md`
  

Changes:

- Tell implementers to load and follow `/tdd` before writing implementation code.
  
- Remove fallback wording for `test-driven-development`.
  
- Delete `plan-build-verify/references/test-driven-development.md`.
  
- Delete `plan-build-verify/references/testing-anti-patterns.md`.
  
- Remove internal links to those deleted files.
  
### 5. Replace Verify placeholder with a real workflow
File: `plan-build-verify/references/verify.md`

- Fix typos and remove placeholder-only behavior.
  
- Use `/user-acceptance` when available.
  
- If `/user-acceptance` is unavailable, run a standalone Verify workflow:
  
  1. Read the approved spec and Build completion report.
    
  2. Build an acceptance matrix from acceptance criteria.
    
  3. Run automated verification commands.
    
  4. Perform manual or UAT checks when relevant.
    
  5. Inspect the diff against approved scope.
    
  6. Classify issues as blocker, important, or minor.
    
  7. Produce a pass, pass with issues, or fail recommendation.
    
- Include required evidence paths, commands, screenshots, logs, or URLs when available.
  
### 6. Clean up reviewer and implementer prompts
Files:

- `plan-build-verify/references/implementer-prompt.md`
  
- `plan-build-verify/references/spec-reviewer-prompt.md`
  
- `plan-build-verify/references/code-quality-reviewer-prompt.md`
  
- `plan-build-verify/references/code-reviewer.md`
  

Changes:

- Add fields for spec path, task ID, base SHA, head SHA, acceptance criteria, test evidence, and approved deviations.
  
- Update `code-quality-reviewer-prompt.md` to reference local `references/code-reviewer.md`.
  
- Replace biased spec-review wording like “finished suspiciously quickly” with neutral guidance to verify independently.
  
- Ensure reviewers evaluate actual code and diff ranges, not only implementer reports.
  
### 7. Fix reference paths and naming
Files: all `plan-build-verify/references/*.md`

- Use one path convention, preferably skill-root-relative paths such as `references/implementer-prompt.md`.
  
- Remove stale `./...` paths when they are ambiguous.
  
- Remove references to unavailable external workflow names unless they are explicit dependencies like `/tdd` and `/user-acceptance`.
  
- Check for typos and stale terms.
  
### 8. Expand eval coverage
File: `plan-build-verify/evals/evals.json`

Add evals for:

- Plan routing for a new “build this feature” request.
  
- Build routing from an approved spec path.
  
- Build refusal or pause for an unapproved spec.
  
- Verify routing for UAT or signoff.
  
- Trivial edit behavior.
  
- TDD delegation to `/tdd` instead of embedded docs.
  
- Build workflow expressed as step-by-step Markdown.
  
### 9. Run validation
Commands:

```bash
cd /Users/gannonhall/dev/skills
python3 converting-commands-to-skills/scripts/validate-frontmatter.py plan-build-verify/SKILL.md
python3 -m json.tool plan-build-verify/evals/evals.json >/tmp/plan-build-verify-evals.json
rg -n "test-driven-development.md|testing-anti-patterns.md|requesting-code-review|suspiciously|alter the user|missingL" plan-build-verify || true
```

Expected:

- Frontmatter passes.
  
- Eval JSON parses.
  
- No stale embedded TDD docs are referenced.
  
- No known typo or broken reference remains.
  
## Implementation order
1. Update `SKILL.md` phase contracts.
  
2. Update `references/plan.md` with approval recording and Build handoff.
  
3. Rewrite `references/build.md` into step-by-step Markdown and `/tdd` delegation.
  
4. Update implementer and reviewer prompts.
  
5. Replace `references/verify.md` with a complete workflow.
  
6. Delete embedded TDD reference files.
  
7. Fix paths and stale references across `plan-build-verify`.
  
8. Expand evals.
  
9. Run validation.
  
## Approval question
{==Approve this full improvement plan?==}{>>approved. proceed<<}{id="c1" by="user" at="2026-05-21T17:59:13.786Z"}
