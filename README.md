# Agent Skills

Personal [Agent Skills](https://agentskills.io/) directory. A mix of original skills and modified open source skills for iOS/macOS development, PR workflows, and general engineering tasks.

This repo is a **library**. Install named skills per project with Vercel `npx skills`. Never install the whole pack, and never use global `-g` (cloud VMs need project-local installs).

## Installation

For product delivery on GitHub-issue repos (`devbox`, `kata-code`, `kata-agents`, `kata-symphony`), install only the plan-build-verify OS (plus Verify's review-thread helper):

```bash
bash plan-build-verify/scripts/install-skills.sh
# or, from a product repo that copied the script:
bash scripts/install-skills.sh
# raw equivalent:
npx skills add gannonh/skills --skill plan-build-verify --skill address-pr-comments -y
```

Do not install `ps`, `okf`, or `kata-linear` for those repos. OKF is retired. Cursor engineering execution is the **pstack** plugin, not npx-installed `ps`. See `plan-build-verify/SKILL.md` (coexistence section).

## Skills

Most directories here are self-contained; read the `SKILL.md` inside one to see what it does. A few carry a stronger product or engineering role:

- [`plan-build-verify`](./plan-build-verify/) — product operating system for GitHub-issue repos. Specs live as Issues; Plan / Build / Verify is the lifecycle.
- [`ps`](./ps/) — historical `/ps` port of pstack. Unwieldy; do not install for product delivery. Use the Cursor pstack plugin instead.
- [`okf`](./okf/) — retired. Kept for history only; not a live roadmap.

## License

This repository is licensed under the [MIT License](LICENSE).

Individual skills may carry their own licenses from upstream sources. Where a per-skill license exists, it takes precedence over the repository-level MIT license. Check each skill directory for a `LICENSE` file before use or redistribution.
