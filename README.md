# Agent Skills

Personal [Agent Skills](https://agentskills.io/) directory. It contains original skills and modified open source skills for iOS and macOS development, PR workflows, and general engineering tasks.

This repo is a **library**. Install named skills per project with Vercel `npx skills`.

## Installation

Run `npx skills` from a standalone terminal such as Ghostty, Terminal.app, or iTerm. Cursor's integrated agent terminal can pass agent markers to child processes. When the CLI detects those markers, it skips the interactive prompts and installs to the detected agent. A standalone terminal opens the skill, agent, and installation-method selectors.

Install the repository's root-level skills with:

```bash
npx skills add gannonh/skills
```

Install the P-Stack skills from their package subdirectory with:

```bash
npx skills add \
  https://github.com/gannonh/skills/tree/main/pstack-skills
```

The command installs project-local skills by default. It can create agent directories such as `.agents/skills` and write `skills-lock.json`. Add `--list` to inspect the available skills without installing them. Add `-g` only for a user-level installation.

Remove project-local skills with:

```bash
npx skills remove
```

## License

This repository is licensed under the [MIT License](LICENSE).

Individual skills may carry their own licenses from upstream sources. Where a per-skill license exists, it takes precedence over the repository-level MIT license. Check each skill directory for a `LICENSE` file before use or redistribution.
