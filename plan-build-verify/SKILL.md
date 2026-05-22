---
name: plan-build-verify
description: Use this skill for multi-step, spec-driven, or acceptance-gated implementation work that should move through Plan, Build, and Verify phases. Plan turns ideas or vague build requests into project-grounded Markdown specs and implementation plans. Build executes an approved plan. Verify validates completed work against a spec, Build report, and acceptance criteria. Default to Plan for new feature, product, or architecture requests unless the user explicitly points to an existing plan for implementation or asks for verification or UAT. Use it for requests like plan this, write a spec, build an analytics dashboard, execute this plan, verify this work, run UAT, ready to merge, or check whether this is done. For tiny edits, ask whether the full workflow is desired.
---

# Plan Build Verify

Use this skill to route implementation work through a sequential path:

1. **Plan**: turn an idea into a project-grounded spec and implementation plan.
2. **Build**: execute an approved spec or implementation plan.
3. **Verify**: validate completed work against the spec, plan, and acceptance criteria.

Most work should move through Plan → Build → Verify. Default to **Plan** unless the user explicitly directs you to execute an existing plan or verify completed work.

## Phase contracts

| Phase  | Input                                                | Output                                                                                                  | Status                        |
| ------ | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ----------------------------- |
| Plan   | Idea, vague request, or new build request            | Draft `docs/specs/YYYY-MM-DD-<topic>.md` with Build handoff, then Approved after explicit user approval | `Idea` → `Draft` → `Approved` |
| Build  | Approved spec, or explicit user override             | Implemented tasks, commits, review results, Build completion report                                     | `Approved` → `Implemented`    |
| Verify | Implemented spec plus completed work or Build report | Acceptance evidence and signoff recommendation                                                          | `Implemented` → `Verified`    |

Build must not start from a draft spec unless the user explicitly overrides the approval gate. Verify must not claim signoff without evidence.

## Select the workflow

Determine the current phase from the user's request and project state. If the user gives a new build request, start with Plan even if they use the word “build”.

Use **Plan** when:

- The user asks to plan, scope, design, spec, shape, or prepare work.
- The user asks to build a new feature, product surface, integration, or architecture change without pointing to an approved plan.
- There is no approved spec or implementation plan for the requested work.
- The safest next step is writing a Markdown spec before coding.

Examples that start with Plan:

- `/plan-build-verify "Let's build an analytics dashboard for foo bar."`
- `/plan-build-verify "Add API-backed project creation."`
- `/plan-build-verify "We need a Slack integration for agent updates."`

Use **Build** when:

- The user asks to execute, implement, build, or continue from an approved spec or plan.
- The request points to an existing plan/spec and asks for code changes.
- The current task is implementation rather than discovery or acceptance review.

Examples that start with Build:

- `/plan-build-verify "Execute this plan: docs/specs/foo-plan.md"`
- `/plan-build-verify "Implement docs/specs/2026-05-21-analytics-dashboard.md"`
- `/plan-build-verify "Continue the approved billing settings plan."`

Use **Verify** when:

- The user asks to verify, validate, review, test, sign off, run UAT, or prove work is complete.
- Implementation appears done and the next step is acceptance evidence.
- The user asks whether a branch, feature, or plan is ready to merge or hand off.

Examples that start with Verify:

- `/plan-build-verify "Run UAT on foobar."`
- `/plan-build-verify "Verify the analytics dashboard work is complete."`
- `/plan-build-verify "Check whether this branch is ready to merge."`

For tiny, clearly bounded edits such as a copy change or single config tweak, do not force the full Plan workflow. State the assumption and ask whether the user wants the full Plan → Build → Verify process.

If the phase remains ambiguous after applying these rules, ask one focused question that resolves the phase.

## Load the workflow instructions

After selecting the workflow, read the corresponding reference file completely and follow it:

- Plan: `references/plan.md`
- Build: `references/build.md`
- Verify: `references/verify.md`

Only load the workflow you need. If the selected workflow's reference file is empty or incomplete, say so and ask the user whether to draft that workflow before proceeding.

## Shared principles

- Inspect the repo before making claims about project structure or commands.
- Use a todo list when the work has multiple steps.
- Ask one question at a time when clarification is needed.
- Prefer small, verifiable phases over broad unverified changes.
- Keep scope tied to the selected spec, plan, or acceptance criteria.
- Surface uncertainty instead of filling gaps with guesses.
