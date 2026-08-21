# ps

Rigorous engineering mode for coding agents. One skill that routes a task to a playbook, applies a named principle set, delegates to parallel subagents, and verifies against the real artifact before declaring done.

Works in Claude Code, pi, Cursor, and Codex without modification. Adapted from [pstack](https://github.com/cursor/plugins/tree/main/pstack); see `NOTICE.md`.

## Install

Copy the directory into your skills path:

```bash
cp -R ps ~/.agents/skills/     # universal
cp -R ps ~/.claude/skills/     # Claude Code
```

Then configure which models each role uses:

```
/ps setup
```

That reads your available models and writes a role-to-model roster into the `## Sub-agents` section of your global `AGENTS.md`. It does not create a config file of its own — the roster lives where every harness already loads it, so it applies to all your delegated work rather than only to `ps`.

The bundled scripts need [Bun](https://bun.sh). They self-install their one dependency on first run.

## Use

```
/ps <what you want done>
```

That is the normal path. It matches your request to a playbook, opens a todolist with that playbook's steps, and runs them.

```
/ps this pr has a subtle bug where the scroll drifts every 750ms even when idle.
    repro first, then fix and verify.

/ps build a small feature behind a flag. verify it really works.

/ps i'm going to bed. get the PR green and merge-ready by morning.
```

### Other forms

| Command | Does |
|---|---|
| `/ps --help` | Print the workflow and playbook tables. No work. |
| `/ps <workflow> <args>` | Skip playbook matching and run one workflow directly. |
| `/ps --herdr <task>` | Fan out into named Herdr panes instead of native subagents. |
| `/ps setup` | Write or update the model roster. |

Direct workflow calls are for when you already know what you want:

```
/ps how do we cancel runs? do we have an n+1 when we look up every run to cancel?
/ps why is this feature flag not on yet?
/ps interrogate review this pr
/ps arena build two markdown renderers so we can compare
```

## What's inside

**22 playbooks.** Investigation, bug fix, perf, hillclimb, runtime and trace forensics, feature, refactoring, prototype, visual parity, authoring a skill, eval, babysit, shipping, autonomous run, orchestrate, autopilot, session pickup, pause safely, multi-phase plan, worktree cleanup, opening a PR.

**21 principles.** Short, named rules the mode cites by name when one changes a decision. Grouped as core, architecture, verification, delegation, meta. A citation with no decision behind it means the principle was skipped.

**21 workflows.** `how` and `why` for understanding, `architect` and `arena` for design, `swarm` for fan-out, `interrogate` for adversarial review, `tdd`, `unslop`, `no-comments`, `blast-radius`, `reflect`, and the rest.

**4 scripts.** `watch-pr` polls a PR to a merge-ready or blocked verdict. `orch` is a plain-file coordination store for long programs. `worktree-audit.sh` finds reclaimable worktrees. `check-links.sh` validates that every path this skill references resolves.

Everything is reached from the dispatch table at the top of `SKILL.md`. Nothing else is registered as a skill, so none of it competes for auto-invocation.

## Dependencies

The skill itself is self-contained. The bundled scripts need [Bun](https://bun.sh), and `watch-pr` plus several playbooks shell out to `git` and the [`gh`](https://cli.github.com) CLI.

Six other skills are **optional** hand-offs. Each site that uses one names an inline fallback, so a missing skill degrades the step rather than blocking it. `SKILL.md` carries the table.

| Skill | Used for |
|---|---|
| `simplify` | Cleanup pass before commit |
| `skill-creator` | Authoring or editing a SKILL.md |
| `agent-browser`, `chrome-cdp` | Driving a browser or Electron surface |
| `automating-ios-simulator` | Driving the iOS simulator |
| `herdr` | The `--herdr` delegation mode only |

The `why` workflow queries MCP servers when they exist — source control, issue tracker, docs, chat, observability, error tracking, analytics — and ships a playbook per provider. None are required. It discovers what is connected at run time, flags any category it could not reach as an explicit gap, and always has `code-archaeology` working from git alone.

Check what you have:

```bash
for s in simplify skill-creator agent-browser chrome-cdp automating-ios-simulator herdr; do
	[ -d ~/.agents/skills/$s ] || [ -d ~/.claude/skills/$s ] \
		&& echo "  ok      $s" || echo "  missing $s"
done
```

## How delegation works

`references/delegation.md` is the only file that names a harness-specific mechanism. Workflows ask for a **role** — `explorer`, `code`, `judgment`, `panel`, `worker` — and that file resolves it against your `AGENTS.md` roster and the harness you are in.

| Harness | Mechanism | Cross-provider panels |
|---|---|---|
| Claude Code | `Agent` tool, `isolation: worktree` | No. Panels run same-family |
| pi | `subagent` tool (`pi-subagents`) | Yes |
| Cursor | `Task` tool | Yes |
| None | Runs inline, single-threaded, and says so | n/a |

`panel` is the role where model diversity matters: `interrogate`, `arena`'s cross-judge, and `how`'s critics get their signal from disagreement between model families, not from assigned personas. Where a harness cannot span families, the workflow runs anyway and weights the agreement signal down.

## Verifying an install

From the skill directory:

```bash
./scripts/check-links.sh     # every referenced path resolves
cd scripts && bun test       # 40 tests
cd scripts && bun run typecheck
```

## Notes

Stacked pull requests are out of scope. `shipping`, `autopilot`, and `orchestrate` assume PRs branch off trunk and land independently.

`ps` never auto-invokes. It is a mode you enter deliberately.
