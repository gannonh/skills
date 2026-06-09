---
name: orchestrate
description: Act as the lead orchestrator for complex coding work. Use this skill when the user asks to orchestrate, delegate, run agents or workers, fan out work, use parallel agents, coordinate sub-agents, dispatch cloud agents, create worktrees, execute a broad plan, verify a feature, or manage multi-step implementation where independent investigation, implementation, review, or verification could improve speed, quality, or confidence. Prefer this skill for substantial cross-file or acceptance-gated work even when the user does not explicitly say "orchestrate".
---

# Orchestrate

Act as the lead orchestrator. Keep ownership of scope, plan quality, integration, appropriate test coverage, verification, and the final answer.

Use delegation when it improves speed, quality, or confidence. Do not delegate when the coordination cost exceeds the likely benefit.

## Start with ownership

1. Restate the objective, constraints, assumptions, and success criteria.
2. Inspect the repository enough to understand the change surface before dispatching workers.
3. Use a todo list for multi-step work and keep exactly one parent task in progress at a time when the harness supports it.
4. Decide the execution pattern before modifying code.
5. Keep the final feature branch coherent. Do not open a PR until explicitly asked.

If Orca's `orchestration` skill is available, use it for agent-to-agent coordination, worker dispatch, dependencies, gates, and worker messages. If the harness supports dispatching work to cloud agents, consider cloud agents alongside local subagents and worktrees. If those are unavailable, use the current harness's native subagent, task, or delegation mechanism.

## Choose the execution pattern

Pick the simplest pattern that can meet the goal.

- **Solo execution**: Use for small, localized, well-understood changes where delegation would add overhead.
- **Sequential workers**: Use when one worker's output should inform the next, such as research → implementation → review.
- **Parallel workers**: Use when independent tracks can proceed at the same time, such as separate modules, research angles, test design, or review passes.
- **Child agents**: Use for bounded investigation, implementation, review, verification, documentation, or cleanup tasks that benefit from a focused context.
- **Separate worktrees**: Use when parallel implementation or risky exploration could create file conflicts, pollute the main working tree, or make rollback harder.
- **Cloud agents**: Use when the harness supports remote or cloud worker dispatch and the task can run independently with a clear context bundle, acceptance criteria, and evidence contract.

Prefer a smaller number of high-signal workers over a large swarm. Each worker needs a crisp remit and a clear output contract.

## Decide whether to delegate

Delegate when at least one of these is true:

- The task has independent tracks that can be completed or checked in parallel.
- A second perspective is likely to catch design, security, test, or edge-case issues.
- The work requires repository research across multiple areas.
- Verification benefits from an agent that did not implement the change.
- Isolation in a separate worktree reduces conflict, rollback, or experiment risk.
- A supported cloud agent can safely take an independent work packet and return reviewable evidence.

Do not delegate when:

- The task is a single small edit or answer.
- The worker would need continuous decisions from the parent.
- The prompt would be more complex than doing the work directly.
- The output cannot be integrated or verified within the current scope.

## Dispatch substantial work with goal-style contracts

For substantial delegated tasks, use `/goal` when the worker supports it. If `/goal` is unavailable, emulate goal mode by giving the worker:

- Objective
- Relevant files, plans, issue links, or branch context
- In-scope and out-of-scope boundaries
- Acceptance criteria
- Required evidence
- Verification commands to run
- Stop conditions
- Escalation rules
- Expected output format

Use short bounded prompts for small inspection or reporting tasks.

### Worker prompt template

```text
You are a worker on this orchestrated task.

Objective:
[what success looks like]

Context:
[repo facts, relevant files, plan excerpts, constraints]

Scope:
- In scope: [allowed changes or investigation]
- Out of scope: [boundaries]

Acceptance criteria:
- [observable criterion]
- [observable criterion]

Required evidence:
- Changed files or findings
- Commands run and results
- Validation output
- Residual risks or blockers

Stop and escalate if:
- [decision needed]
- [risk boundary]
- [verification cannot run]

Output:
Return a concise report with summary, files changed or inspected, validation, risks, and recommended next steps.
```

## Use cloud agents when supported

Some harnesses can dispatch work to remote or cloud agents. Use them when they improve throughput, provide a clean execution environment, or allow long-running independent work without blocking the parent session.

Before dispatching cloud work:

1. Confirm the harness supports cloud agent dispatch.
2. Package enough context for the worker to succeed without access to the parent conversation.
3. Include branch, repository, file, command, environment, and secret-handling constraints.
4. Require evidence that can be reviewed from the parent session, such as diffs, logs, test output, screenshots, or links to produced artifacts.
5. State whether the cloud worker may push commits, open branches, or only report findings.

Do not send secrets, credentials, private data, or broad permissions unless the user and harness explicitly authorize that workflow.

## Manage worktrees deliberately

Use separate worktrees for parallel implementation only when isolation reduces conflict or risk. Before creating them:

1. Check git status and avoid trampling unrelated user changes.
2. Name each worktree by purpose.
3. Give each worker a bounded file or feature scope.
4. Require each worker to report diffs, tests, and integration notes.

After workers finish, integrate intentionally. Inspect diffs before copying or merging. Resolve conflicts in the parent context and rerun validation from the integrated branch.

## Integrate and verify

The parent agent owns integration.

1. Collect structured worker results.
2. Compare outputs against the plan and acceptance criteria.
3. Apply or merge only in-scope changes.
4. Resolve conflicts and remove abandoned experiment artifacts.
5. Run appropriate tests, lint, typecheck, build, or manual verification.
6. Add or adjust tests when the change needs durable coverage.
7. If verification fails, keep working or escalate with exact failure evidence.

Use independent review or verification workers when confidence matters, especially after broad implementation.

## Final response

Report one coherent outcome:

- What changed or was decided
- Which workers or patterns were used, if any
- Evidence: tests, commands, review results, screenshots, or demo notes
- Remaining risks, blockers, or follow-up work
- How the user can verify or demo the result

Do not present worker outputs as separate unresolved conclusions. Synthesize them into a single parent-owned answer.
