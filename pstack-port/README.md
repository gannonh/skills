# P-Stack Agent Skills port

This directory defines the reproducible port of Cursor Pstack 0.14.4 into independent Agent Skills.

The generated skill names use the lowercase `ps-` prefix because the Agent Skills specification rejects uppercase names. This is the standards-compliant form of the requested `PS-` grouping.

## Regenerate

From the `pstack-port` directory, run:

```bash
python3 scripts/port_pstack.py \
  --source /path/to/cursor-pstack-plugin \
  --destination ..
python3 scripts/validate_pstack_port.py ..
```

Use `--check` on the first command to detect drift without changing files. The source must match the version and content hash in [`manifest.json`](manifest.json).

The [port script](scripts/port_pstack.py) copies each source skill before it changes frontmatter, cross-skill references, invocation names, model routing, and harness-specific mechanics. It then applies the files under `overlays/`. The [validator](scripts/validate_pstack_port.py) checks the generated result. Generated directories contain `.ps-port.json`, `NOTICE.md`, and the upstream `LICENSE.txt`.

## Configure a consuming repository

Run the `ps-setup-pstack` skill after installing the desired `ps-*` skills. The skill verifies exact model identifiers and reasoning levels before it calls its bundled renderer.

The renderer writes one bounded P-Stack block in `AGENTS.md` and `.agents/pstack/models.json`. Codex, Pi, Cursor, and OpenCode load `AGENTS.md` directly. Claude Code receives a bounded `@AGENTS.md` import in `CLAUDE.md`. It also receives the same skills under `.claude/skills/` because Claude Code does not discover `.agents/skills/`.
