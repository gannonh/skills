# Attribution

`ps` is adapted from [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan (poteto), a Cursor plugin, used under the MIT License. The upstream license is in `LICENSE` and takes precedence over the repository-level license for this directory.

## What changed in this port

- Collapsed from a 44-skill Cursor plugin into one harness-agnostic skill. The former skills are `references/`, reached through the dispatch table in `SKILL.md`.
- All Cursor-specific delegation (`Task` tool parameters, `subagent_type`, `readonly`, cloud agents) replaced by `references/delegation.md`, which adapts to Claude Code, pi, Cursor, or no subagent mechanism at all.
- Model configuration moved from `~/.cursor/rules/pstack-models.mdc` to the `## Sub-agents` roster in `AGENTS.md`, maintained by `/ps setup`.
- Stacked-pull-request support removed. The `autopilot-stack` playbook is dropped, `shipping` and `autopilot` rewritten around independent PRs, and the `frontier` subcommand deleted from `scripts/orch`.
- Bugbot-specific triage generalized to any review bot, with CodeRabbit detection added to `scripts/watch-pr`.
- The `benny` Slack-automation pack was not ported.
