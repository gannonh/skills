# Agent Skills

Personal [Agent Skills](https://agentskills.io/) directory. A mix of original skills and modified open source skills for iOS/macOS development, PR workflows, and general engineering tasks.

## Installation

Copy individual skill directories into your skills path, typically `~/.claude/skills/` or `~/.agents/skills/`.

For product delivery on GitHub-issue repos (`devbox`, `kata-code`, `kata-agents`, `kata-symphony`), install **plan-build-verify** as the product operating system, not the whole pack:

```bash
npx skills add https://github.com/gannonh/skills --skill plan-build-verify
```

A full-pack install also pulls in `okf`, `kata-linear`, and `ps`, which use different roadmap models. Those skills remain in this repo for other workflows; do not treat them as the product OS for those four repos. See `plan-build-verify/SKILL.md` (coexistence section).

## Skills

Most directories here are self-contained; read the `SKILL.md` inside one to see what it does. A few carry a stronger product or engineering role:

- [`plan-build-verify`](./plan-build-verify/) — product operating system for GitHub-issue repos. Specs live as Issues; Plan / Build / Verify is the lifecycle.
- [`ps`](./ps/) — rigorous engineering mode (Build/Verify engine when used with plan-build-verify). Routes a task to one of 22 playbooks, applies 21 named principles, delegates to parallel subagents, and verifies against the real artifact. Harness-agnostic.

## License

This repository is licensed under the [MIT License](LICENSE).

Individual skills may carry their own licenses from upstream sources. Where a per-skill license exists, it takes precedence over the repository-level MIT license. Check each skill directory for a `LICENSE` file before use or redistribution.
