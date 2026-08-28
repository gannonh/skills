# @gannonh/skills

Personal [Agent Skills](https://agentskills.io/) directory. It contains original skills and modified open source skills.

This repo is a **library**. Install named skills per project with Vercel `npx skills`.

## Installation

Install the repository's root-level skills with:

```bash
npx skills add gannonh/skills
```

Install the P-Stack skills from their package subdirectory with:

```bash
npx skills add gannonh/skills/pstack-skills
```

These commands run the installer interactively. Add `--list` to inspect the available skills without installing them. To install non-interactively to the local projects ./agents/skills directory:

```bash
npx skills add gannonh/skills/pstack-skills -y --agent codex
```

Remove project-local skills with:

```bash
npx skills remove
```

## License

This repository is licensed under the [MIT License](LICENSE).

Individual skills may carry their own licenses from upstream sources. Where a per-skill license exists, it takes precedence over the repository-level MIT license. Check each skill directory for a `LICENSE` file before use or redistribution.
