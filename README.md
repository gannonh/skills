# Agent Skills

Personal [Agent Skills](https://agentskills.io/) directory. It contains original skills and modified open source skills for iOS and macOS development, PR workflows, and general engineering tasks.

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

Do not install `okf` or `kata-linear` for those repos. OKF is retired. See the coexistence section in `plan-build-verify/SKILL.md`.

## Install P-Stack

The `ps-*` directories are a provider-neutral port of the Pstack Cursor plugin. They work with harnesses that implement the [Agent Skills standard](https://agentskills.io/specification). For a complete P-Stack installation, select every `ps-*` skill. For a smaller installation, include `ps-poteto-mode`, `ps-setup-pstack`, and every leaf skill that the selected workflows reference.

```bash
npx skills add gannonh/skills
```

Run `ps-setup-pstack` after installation. The setup skill asks which harnesses the project uses. It then records a verified small, medium, and large model identifier and a reasoning level for each harness.

The port generator copies Pstack 0.14.4, applies bounded compatibility changes, and validates all 45 generated skills. See [`pstack-port/README.md`](./pstack-port/README.md) for the refresh command and adapter details.

## Skills

Most directories here are self-contained; read the `SKILL.md` inside one to see what it does. A few carry a stronger product or engineering role:

- [`plan-build-verify`](./plan-build-verify/): product operating system for GitHub-issue repos. Specs live as Issues. Plan, Build, and Verify form the lifecycle.
- [`ps-poteto-mode`](./ps-poteto-mode/): common P-Stack routing and execution policy.
- [`ps-setup-pstack`](./ps-setup-pstack/): deterministic model-tier and harness adapter setup.
- [`pstack-port`](./pstack-port/): source manifest, overlays, and port maintenance notes.
- [`okf`](./okf/): retired and kept only for history.

## License

This repository is licensed under the [MIT License](LICENSE).

Individual skills may carry their own licenses from upstream sources. Where a per-skill license exists, it takes precedence over the repository-level MIT license. Check each skill directory for a `LICENSE` file before use or redistribution.
