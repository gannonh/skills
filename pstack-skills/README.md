# P-Stack skills

Provider-neutral Agent Skills port of Pstack, a Cursor plugin for rigorous software engineering workflows.

## Install

Run the installer from a standalone terminal such as Ghostty, Terminal.app, or iTerm. Cursor's integrated agent terminal can set agent-detection markers that make `npx skills` skip its interactive prompts.

Install the P-Stack package into the current repository with:

```bash
npx skills add gannonh/skills/pstack-skills
```

The command installs project-local skills by default. Use `--list` to preview the package without installing it. Use `-g` only when you want a user-level installation.

## Contents

The `skills/` directory contains the ported skills with the `ps-` prefix. The `pstack-port/` directory contains the source manifest, port scripts, and overlays used to regenerate them.

## Attribution

These skills are derived from [Pstack](https://github.com/cursor/plugins/tree/main/pstack), a Cursor plugin authored by [Lauren Tan](https://github.com/poteto). The upstream plugin is distributed under the MIT license.

This port uses Pstack 0.14.4 as its source baseline. The version and source tree hash are recorded in [`pstack-port/manifest.json`](pstack-port/manifest.json). Each generated skill retains its upstream `LICENSE.txt` and `NOTICE.md` files.

This directory is an independent Agent Skills port. It is not the original Cursor plugin.

## Regenerate

See [`pstack-port/README.md`](pstack-port/README.md) for the reproducible port and validation commands.
