# Plan Workflow

Use this workflow to turn an idea into an approved spec and implementation plan that another agent or future session can execute with minimal guessing.

The result is a durable Markdown spec in the local project at:

```text
docs/specs/YYYY-MM-DD-<topic>.md
```

The spec includes the implementation plan and a Build handoff. Do not start implementation until the user approves the written spec, unless the user explicitly asks to skip planning.

## Workflow

When a todo tool is available, create a task for each item and complete them in order. The order matters because alignment and approach approval happen before spec-writing:

1. Explore project context.
2. Align on intent and constraints.
3. Propose approaches.
4. Draft the spec and Build handoff.
5. Self-review the spec.
6. Open the spec in Roughdraft for user review.
7. Resolve Roughdraft comments.
8. Record approval in the spec.
9. Ask whether to continue to Build.

## 1. Explore project context

Inspect the current project before asking detailed questions. Avoid asking about facts already visible in the repo.

Review the smallest useful set of files:

- `README.md`, `AGENTS.md`, `CLAUDE.md`, or equivalent project instructions.
- Existing docs under `docs/`, especially `docs/specs/`, `docs/plans/`, `docs/adr/`, and roadmaps.
- Existing code paths related to the request.
- Package scripts and test commands when implementation is likely.
- Recent commits if they clarify direction.

If the request spans multiple independent systems, flag that early and propose a decomposition before refining details.

## 2. Align on intent and constraints

After exploring project context, enter an alignment phase before drafting the spec. The purpose is to show the user how you are framing the work and give them a chance to correct assumptions before the plan hardens.

Continue the alignment dialogue one focused question at a time until you can clearly state:

- The user's goal.
- Success criteria.
- Scope boundaries and non-goals.
- Key UX, API, data, or integration constraints.
- The main implementation choice the plan depends on.

This is a loop with an exit condition, not a one-question minimum. Ask the next question when the user's answer reveals another decision that could change scope, architecture, UX, data, integration, rollout, or acceptance.

Do not ask about facts the repo already answers. If no factual clarification is needed, ask an alignment question instead of inventing a weak question. Useful alignment questions confirm the agent's read of the task, expose assumptions, or ask the user to choose between viable directions.

Examples:

- `I think the core goal is X, with Y out of scope. Is that right?`
- `The main choice seems to be A versus B. I recommend A because <reason>. Do you want to go with that?`
- `I am assuming success means <observable outcome>. Should I plan around that?`

Do not draft the spec until the user has responded to the alignment phase, unless the user explicitly asks to skip planning dialogue or the task is a tiny edit.

## 3. Propose approaches

After the alignment phase, present 2-3 viable approaches with trade-offs and a recommendation before drafting the spec. If the user has already fixed the implementation direction or only one viable approach exists, present that direction as the recommendation and ask for approval or redirection before drafting.

Use this shape:

```markdown
Recommended: <approach name>
- Why: <short reason>
- Trade-offs: <short caveats>

Alternative: <approach name>
- Why it might fit: <short reason>
- Trade-offs: <short caveats>
```

Recommend the option that gives the clearest implementation path with the least unnecessary scope. Avoid hybridizing approaches unless the combination has a clear reason.

Ask the user to choose or approve the recommendation before drafting the full spec. If one approach is clearly best, still state the recommendation and wait for approval or redirection.

## 4. Write the spec and Build handoff

Create `docs/specs/` if it does not exist. Name the file with the current date and a short slug:

```text
docs/specs/YYYY-MM-DD-<topic>.md
```

Use this structure unless the repo has a stronger existing spec format:

```markdown
# <Feature or Change> Spec

## Status
Draft

## Goal
<What outcome this work should produce.>

## Background
<Project context and why this is needed.>

## Requirements
- <Observable requirement>

## Non-goals
- <Explicitly excluded work>

## Proposed approach
<The selected approach and why it fits.>

## User experience / workflow
<Relevant screens, commands, API flows, or behavior.>

## Technical design
<Components, modules, routes, data model, integrations, and boundaries.>

## Data and API changes
<Schema, DTO, endpoint, config, migration, or storage changes. Use “None” if none.>

## Error handling and edge cases
<Failure modes and expected behavior.>

## Test strategy
<Unit, integration, e2e, manual acceptance, fixtures, mocks.>

## Implementation plan
### Phase 1: <name>
- [ ] <Task with files or modules involved>
- [ ] <Verification for this phase>

### Phase 2: <name>
- [ ] <Task with files or modules involved>
- [ ] <Verification for this phase>

## Acceptance criteria
- [ ] <User-visible or testable outcome>

## Build handoff
- Spec path: <docs/specs/YYYY-MM-DD-<topic>.md>
- Approved scope: <What Build may change>
- Non-goals: <What Build must not change>
- Ordered task list: <Task IDs or phase list>
- Verification commands: <Commands Build must run>
- Required fixtures or test data: <Fixtures, mocks, accounts, credentials, or “None”>
- Known risks: <Risks Build must watch for>
- Blocking open questions: <Questions that block Build, or “None”>

## Open questions
- <Only unresolved questions that do not block Build. Use “None” if none.>
```

### Implementation plan quality bar

Make the plan executable by another agent:

- Order tasks by dependency.
- Prefer vertical slices over broad horizontal layers when possible.
- Name likely files or directories, but do not invent exact APIs before checking the repo or installed docs.
- Include verification commands and expected outcomes.
- Include test data, mocks, or fixtures when needed.
- Call out migration, rollout, and cleanup steps.
- Mark out-of-scope work clearly.
- Avoid large pasted implementation code. Use concise examples only when they remove ambiguity.

Build must not start while `Blocking open questions` contains anything other than `None`, unless the user explicitly overrides that gate.

## 5. Self-review before asking the user

After writing the spec, read it again and fix issues inline.

Check for:

- Placeholders such as `TBD`, `TODO`, or vague “handle errors” language.
- Internal contradictions between requirements, design, and plan.
- Scope creep or tasks unrelated to the goal.
- Ambiguous terms that two implementers could read differently.
- Missing verification for important behavior.
- Plan steps that depend on unverified library APIs.
- Missing or incomplete Build handoff fields.

If a question remains open, make it explicit and explain whether implementation can proceed without answering it.

## 6. Open the spec in Roughdraft

After the self-review passes, open the written Markdown spec in Roughdraft before asking the user to review it.

The user may refer to Roughdraft as `rd` in natural language. Treat `rd` as shorthand for Roughdraft, but do not create or modify any shell alias, executable, symlink, or command named `rd`.

First check whether Roughdraft is installed:

```bash
command -v roughdraft >/dev/null
```

If Roughdraft is missing, ask the user before installing anything. If the user declines installation or installation is not possible, ask whether to continue with ordinary Markdown review in the chat.

Then open the spec with an absolute path:

```bash
roughdraft open "/absolute/path/to/docs/specs/YYYY-MM-DD-<topic>.md"
```

Roughdraft is currently a single-file Markdown viewer/editor. Open one `.md` file at a time.

If Roughdraft is not running, `roughdraft open` starts it automatically. Leave the command running. Do not interrupt, kill, background, detach, or treat the waiting process as cleanup. The wait is intentional: Roughdraft exits the command after the user clicks Done Reviewing, and that exit is the signal to resume.

After `roughdraft open` exits, read the Markdown file from disk and respond to any CriticMarkup comments or suggested changes. If the user requested changes, edit the spec, run the self-review again, and reopen it in Roughdraft.

Use a concise message before the command if useful:

```markdown
Spec written to `docs/specs/YYYY-MM-DD-<topic>.md`. Opening it in Roughdraft for review now.
```

### Roughdraft CriticMarkup

Use Roughdraft-flavored CriticMarkup when reading or writing inline review feedback in Markdown. The base markers are:

```text
Comment: {>>comment<<}
Insertion: {++new text++}
Deletion: {--old text--}
Substitution: {~~old text~>new text~~}
Highlight: {==text==}
```

When adding a new comment or suggested change, use the extended Roughdraft format with an attribute block, such as `{id="c1" by="AI" at="2026-04-28T12:00:00.000Z"}`. Generate a stable document-local id, such as `c1`, `c2` for comments and `s1`, `s2` for suggestions. Set `by` to your agent or author label, set `at` to the current ISO timestamp, and set `re` when replying to an existing comment or suggestion.

Preserve existing Roughdraft attribute blocks unless intentionally removing the associated comment or suggestion. Common attributes are `id`, `by`, `at`, and `re`.

Anchored comments usually look like:

```text
{==selected text==}{>>Comment text<<}{id="c1" by="AI" at="2026-04-28T12:00:00.000Z"}
```

Suggested changes usually look like:

```text
{++new text++}{id="s1" by="AI" at="2026-04-28T12:10:00.000Z"}
{~~old text~>new text~~}{id="s2" by="AI" at="2026-04-28T12:11:00.000Z"}
```

Replies usually look like:

```text
{>>Reply text<<}{id="c2" by="AI" at="2026-04-28T12:05:00.000Z" re="c1"}
```

Use `roughdraft help` and `roughdraft help criticmarkup` for local command and syntax details when needed.

## 7. Record approval

After the user approves the spec:

1. Update `## Status` from `Draft` to `Approved`.
2. Ensure `Blocking open questions` is `None`, unless the user explicitly approved proceeding with listed questions.
3. Note approval in the response with the spec path.

Do not mark a spec approved just because it was written. Approval requires explicit user confirmation after review.

## 8. Transition to Build

After final, explicit plan approval, ask the user if they would like to move to the Build phase.

If the user is ready to build, transition to `references/build.md` and follow it for implementation.

## Stop and ask

Ask before proceeding when:

- The user has not responded to the alignment phase or approved the recommended approach.
- The request is too broad for one spec and needs decomposition.
- Project docs or code conflict and the source of truth is unclear.
- The plan would require credentials, paid services, destructive migrations, or irreversible actions.
- The user appears to want implementation immediately but key requirements are still unknown.

## Examples

Input: “Plan the next milestone for adding API-backed threads.”
Output: Inspect repo context, ask focused questions, compare approaches, then write `docs/specs/YYYY-MM-DD-api-backed-threads.md` with requirements, design, implementation phases, tests, acceptance criteria, and Build handoff.

Input: “Build a billing settings page.”
Output: Use this workflow first because the request needs product and technical decisions. Clarify billing provider, user roles, states, and success criteria before writing the spec and plan.

Input: “Make a tiny copy change in the footer.”
Output: Do not over-plan. State the assumption and ask whether the user wants the full workflow. If they just want the edit, proceed without this workflow’s full process.
