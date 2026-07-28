---
name: okf
description: Create, read, audit, validate, and maintain Open Knowledge Format documentation bundles in repositories. Use this skill when the user asks for /okf, OKF, Open Knowledge Format, docs-as-knowledge, reading project context from docs, converting a documentation repository into an agent-readable bundle, auditing documentation quality, updating durable documentation after work, or adding AGENTS.md instructions for agents to consume and maintain the bundle. Supports /okf read, /okf audit, /okf init, /okf update, and /okf validate workflows.
---

# OKF

Use this skill to read, audit, initialize, update, or validate an Open Knowledge Format bundle.

Before editing, read `references/SPEC.md` from this skill directory. Treat it as the source of truth for OKF v0.2. Keep these two layers separate:

1. **OKF conformance**: the minimal, portable rules defined by the specification.
2. **Repository profile**: optional conventions that make a particular documentation repository easier to maintain.

Do not present profile conventions as universal OKF requirements.

When validating a bundle, use the bundled helper when available:

```bash
python <skill-dir>/scripts/validate_okf.py <repo-root>
```

Useful options:

```bash
python <skill-dir>/scripts/validate_okf.py <repo-root> --level conformance
python <skill-dir>/scripts/validate_okf.py <repo-root> --level repository --profile documentation
python <skill-dir>/scripts/validate_okf.py <repo-root> --level editorial --strict-links
```

## Core idea

An OKF bundle is a directory tree of Markdown concept documents with YAML frontmatter. `index.md` and `log.md` are reserved navigation and history files when present. In repositories, use `./docs` as the bundle root unless the user or existing tooling chooses another path.

The skill has five workflows:

- `/okf read`: load only the context relevant to a task.
- `/okf audit`: diagnose structure, freshness, provenance, and editorial quality without editing by default.
- `/okf init`: add OKF structure to an existing documentation corpus.
- `/okf update`: preserve durable knowledge after meaningful work.
- `/okf validate`: run conformance, repository, or editorial checks.

## Repository profiles

Select a profile from the repository's actual purpose. Profiles guide organization; they do not change OKF conformance.

### `documentation`

Use for product documentation, policy libraries, handbooks, knowledge bases, learning material, and other documentation-first repositories. Infer the taxonomy from the subject matter and existing information architecture. Common sections include:

- `concepts/`
- `guides/`
- `reference/`
- `policies/`
- `examples/`
- `domains/`
- `research/`
- `sources/` or `references/`

Do not create `specs/` or `adrs/` unless the repository actually contains specifications or architecture decisions.

### `software-project`

Use for documentation embedded in or adjacent to a software codebase. Common sections include:

- `specs/` for plans, feature specifications, and roadmaps
- `adrs/` for durable architecture decisions
- `architecture/`
- `guides/`
- `reference/`
- `runbooks/`
- `domains/`

`specs/` and `adrs/` are recommended only when the project uses those document types. Never seed empty sections solely to satisfy a taxonomy.

### `research`

Use for evidence reviews, investigations, literature notes, experiments, and source-backed analysis. Common sections include:

- `questions/`
- `findings/`
- `methods/`
- `evidence/`
- `sources/` or `references/`
- `glossary/`

Prioritize provenance, verification state, and explicit separation between evidence and inference.

### `custom`

Use the repository's established taxonomy. Preserve existing URLs and navigation unless the user explicitly asks for redesign.

## Initialization strategies

Choose the least disruptive strategy that satisfies the request:

- **Overlay** (default): keep documents in place; add frontmatter, indexes, links, and agent instructions.
- **Normalize**: move clearly misplaced documents into a coherent taxonomy while preserving history and fixing links.
- **Migrate**: redesign the information architecture intentionally, including redirects or compatibility links when published paths matter.

Do not default to moving files in an established documentation site.

## Concept document rules

Every `.md` file in the bundle is a concept document unless its filename is `index.md` or `log.md`.

A minimal conformant concept is:

```yaml
---
type: Guide
---
```

Prefer richer v0.2 frontmatter when the information is known:

```yaml
---
type: Guide
title: Configure authentication
description: How administrators configure authentication providers.
tags: [authentication, administration]
status: stable
generated:
  by: human:gannonh
  at: 2026-07-28T15:00:00Z
verified:
  - by: human:gannonh
    at: 2026-07-28T15:00:00Z
stale_after: 2026-10-28
sources:
  - id: auth-policy
    resource: /policies/authentication.md
    title: Authentication policy
---
```

Rules:

- `type` is the only always-required key.
- Preserve unknown frontmatter keys when editing.
- Prefer descriptive, stable type names such as `Guide`, `Reference`, `Policy`, `Domain Concept`, `Research Note`, `Spec`, `ADR`, or `Runbook`.
- Do not introduce a centrally controlled type vocabulary.
- Use `status` only with the v0.2 values `draft`, `stable`, or `deprecated`. Absence means `stable`.
- Use `stale_after` only when a meaningful review or expiry date exists.
- `timestamp` is a legacy v0.1 field. For new or migrated v0.2 content, use `generated: { by, at }`.
- Update `generated.at` only after a meaningful content change, not formatting, link repair, generated-index refreshes, or typo-only edits.
- Use the actor convention: `<producer>/<version>` for agents/tools, `human:<id>` for people, and `process:<id>` for automated processes.
- Keep `generated` and `verified` distinct. A writer is not automatically a verifier.

Producer-defined extension keys are allowed. For documentation repositories, useful extensions may include `canonical`, `canonical_for`, `supersedes`, `owners`, or `audience`. Clearly treat them as repository conventions, not OKF v0.2 fields.

## Provenance and claim support

OKF v0.2 records provenance in `sources` frontmatter.

Each source entry must contain `resource`. Add a stable `id` when the body attributes a claim to that source. Attribute claims with a Markdown footnote whose label matches `sources[].id`:

```markdown
The service retains audit events for 90 days.[^retention-policy]

[^retention-policy]: Audit retention policy
```

Do not add a new `# Citations` list to v0.2 concepts. Preserve legacy citation sections when migrating cautiously, but move new provenance into `sources` and keyed footnotes.

When updating source-backed documentation:

- Preserve existing source identifiers and citations when possible.
- Never turn an unsupported assertion into a documented fact.
- Mark inference explicitly.
- Preserve meaningful disagreement between sources.
- Prefer primary or canonical sources when selecting what to verify.
- Use source credibility signals such as `author`, `last_modified`, `usage_count`, and `usage_window` only when supported by evidence.

## Cross-linking

Use standard Markdown links to express durable relationships between concepts.

Prefer bundle-relative absolute links such as `/concepts/authentication.md` when an OKF-aware consumer will interpret them relative to the bundle root. Preserve the repository's existing link style when a static-site generator or publisher requires another convention.

Add reciprocal links only when both concepts benefit from traversal. Do not manufacture relationships merely to increase link density.

Typical relationships include:

- a guide explaining a domain concept
- a policy constraining a procedure
- a reference page supporting a tutorial
- a spec constrained by an ADR
- a runbook operating a system described by an architecture concept
- a current concept superseding a deprecated concept

## Canonicality and overlap

Documentation repositories often contain multiple pages about the same subject. Do not merge them merely because they overlap.

First distinguish their purpose: concept, procedure, reference, policy, rationale, example, or historical record. Then:

- Prefer one clearly discoverable canonical concept for each durable subject.
- Replace duplicate explanations with short summaries and links when practical.
- Preserve historical material with `status: deprecated` and explicit links to the current concept.
- Use producer-defined `supersedes` or `canonical_for` only when the repository adopts those extensions.
- Surface contradictions instead of silently choosing or inventing a resolution.

## Indexes

Use `index.md` for progressive disclosure. A bundle-root index is strongly recommended by this skill even though OKF conformance does not require one.

The root index may declare the version:

```yaml
---
okf_version: "0.2"
---
```

No other index frontmatter is permitted by v0.2.

Distinguish two index styles:

- **Curated indexes**: human-authored framing, learning paths, priorities, and explanations.
- **Generated indexes**: exhaustive listings derived from frontmatter.

When a repository mixes them, preserve prose and regenerate only marked regions:

```markdown
<!-- okf:auto:start type="Guide" tag="authentication" -->
...
<!-- okf:auto:end -->
```

Do not overwrite unmarked editorial content.

## Logs

`log.md` is optional. Git already records file-level history; use an OKF log only for useful semantic history.

- Prefer one bundle-level log unless a section has a distinct release or editorial history.
- Use newest-first `YYYY-MM-DD` headings.
- Log meaningful additions, deprecations, reorganizations, and policy changes.
- Do not log formatting, typo-only edits, link-only repairs, or generated-index refreshes.
- Prefer one session-level entry over repetitive entries in many directories.

## `/okf read` workflow

Use this read-only workflow to load context before answering, editing, planning, or implementing.

1. Locate the bundle.
   - Use the named root, otherwise `./docs`.
   - If no root index exists, scan the bundle shallowly rather than assuming no OKF bundle exists; indexes are optional in the specification.
   - Do not edit documents or logs.

2. Read the map.
   - Read the root index when present.
   - Read relevant section indexes.
   - Identify canonical, stable, deprecated, stale, verified, and unverified concepts from frontmatter.

3. Traverse for the task.
   - For explanation: read the canonical concept, prerequisites, terminology, examples, and supported sources.
   - For editing: read the target, inbound and outbound links, siblings, sources, and superseded coverage.
   - For software work: read relevant specs, ADRs, architecture notes, runbooks, domain concepts, and references.
   - For a question: prefer canonical and verified sources; report conflicts instead of silently choosing one.
   - Stop when context is sufficient. Do not ingest the whole bundle unless requested.

4. Report loaded context.
   - Summarize the relevant concepts and constraints.
   - State which source-of-truth documents were used.
   - Call out stale, deprecated, contradictory, unsupported, or missing knowledge.
   - Recommend the next documents or source files only when needed.

## `/okf audit` workflow

Audit is read-only unless the user explicitly asks for fixes.

1. Run validation at repository and editorial levels.
2. Inventory the taxonomy, index coverage, and link graph.
3. Identify and prioritize:
   - malformed or missing frontmatter
   - orphaned or unreachable concepts
   - broken links
   - missing titles or descriptions
   - duplicate titles or likely duplicate concepts
   - inconsistent type names
   - stale or deprecated content without a current replacement
   - legacy `timestamp` or `# Citations` usage
   - missing or invalid source attribution
   - conflicting concepts
   - oversized concepts that mix distinct purposes
   - tiny fragments that probably belong in a larger concept
   - index summaries that no longer match their targets
4. Report findings by severity and avoid rewriting the entire corpus automatically.

## `/okf init` workflow

1. Confirm repository state.
   - Inspect `git status --short` when working locally.
   - Preserve unrelated changes.
   - Do not move root files such as `README.md`, `CONTRIBUTING.md`, or `AGENTS.md` unless explicitly requested.

2. Inventory existing documentation.
   - Search the established docs tree, root Markdown files, and common locations.
   - Read enough to classify purpose, canonicality, freshness, provenance, and publication constraints.

3. Select a profile and strategy.
   - Infer `documentation`, `software-project`, `research`, or `custom` from the repository.
   - Default to overlay.
   - Do not create empty `specs/`, `adrs/`, or other profile sections.

4. Normalize concepts.
   - Add v0.2 frontmatter to non-reserved Markdown files.
   - Preserve unknown keys and published paths.
   - Migrate legacy `timestamp` to `generated.at` only when the producer identity and meaningful-change time can be represented honestly.
   - Migrate legacy body citations to `sources` and keyed footnotes without losing provenance.
   - Add durable links without inventing relationships.

5. Create navigation.
   - Create a root `index.md` with `okf_version: "0.2"` unless the existing publishing system makes another approach preferable.
   - Add section indexes where they materially improve traversal.
   - Use generated regions only when regeneration is repeatable.
   - Create logs only when they add semantic value.

6. Update AGENTS.md.
   - Tell agents where the bundle root is.
   - Tell them to read the root and relevant section indexes before substantial work.
   - Tell them to follow source, lifecycle, and cross-link signals.
   - Tell them to update durable concepts rather than creating session notes indiscriminately.
   - Keep project-specific instructions intact.

7. Validate and report.
   - Run conformance, repository, and relevant editorial checks.
   - Run existing docs lint or site builds when available.
   - Summarize files created, updated, moved, or intentionally preserved.

## `/okf update` workflow

1. Determine what changed.
   - Review diffs, commits, PR context, source changes, or the user's completed work.
   - Identify durable changes to behavior, policy, terminology, architecture, operations, product decisions, evidence, or procedures.

2. Read before editing.
   - Read the current index and relevant concepts.
   - Inspect lifecycle and provenance fields.
   - Check for canonical, duplicate, deprecated, or conflicting coverage.

3. Update the right concepts.
   - Prefer updating an existing canonical concept.
   - Create a new concept only for durable knowledge with a distinct purpose.
   - Add source attribution for new factual claims.
   - Mark obsolete concepts `deprecated` and link to the replacement rather than deleting useful history.
   - Update `generated` only for meaningful content changes.
   - Add `verified` only when an actual verification occurred.

4. Maintain navigation.
   - Refresh affected curated or generated indexes.
   - Preserve unmarked editorial prose.
   - Add or repair useful cross-links.

5. Maintain semantic history when used.
   - Add one concise log entry for meaningful bundle changes.
   - Do not create repetitive section logs.

6. Validate and report.
   - Run the appropriate validation levels.
   - Report concepts created, updated, deprecated, indexes refreshed, provenance changed, and remaining gaps.

## `/okf validate` workflow

Choose the narrowest useful level:

- `conformance`: actual OKF v0.2 structural requirements and optional-family shape checks.
- `repository`: conformance plus this skill's repository usability checks, such as a root index and declared version.
- `editorial`: repository checks plus quality diagnostics such as orphaned concepts, duplicate titles, missing summaries, stale content, and legacy v0.1 patterns.

Broken links are warnings by default because OKF consumers must tolerate them. Use `--strict-links` when the repository requires all local links to resolve.

## AGENTS.md snippet

Adapt this during `/okf init`:

```markdown
## Open Knowledge Format docs

This repository maintains an OKF v0.2 bundle at `./docs`.

- Read `./docs/index.md` and the relevant section indexes before substantial work.
- Follow links into the concepts, guides, policies, references, specs, ADRs, runbooks, research, and sources relevant to the task; not every repository uses every section.
- Treat `sources`, `generated`, `verified`, `status`, and `stale_after` as context for provenance, trust, lifecycle, and freshness.
- Update an existing canonical concept when possible. Create a new concept only for durable knowledge with a distinct purpose.
- After meaningful behavior, policy, architecture, operational, or documentation changes, update affected concepts and navigation. Add log entries only when they provide useful semantic history.
- Preserve unknown frontmatter fields and existing publication paths.
- Every non-reserved Markdown concept must have parseable YAML frontmatter with a non-empty `type`. `index.md` and `log.md` are reserved.
```

## Helper script

`scripts/validate_okf.py` supports:

- OKF v0.2 conformance checks
- repository profiles without forcing a fixed taxonomy
- provenance, trust, lifecycle, and Attested Computation shape checks
- optional strict link validation
- editorial warnings for freshness, legacy fields, duplicate titles, and orphaned concepts

## Before finishing

Verify:

- the repository taxonomy matches its actual purpose
- no empty profile sections were created merely by convention
- concept frontmatter is v0.2-compatible
- source-backed claims retain provenance
- `generated` and `verified` represent real events
- deprecated concepts point readers to current material
- indexes support progressive disclosure without overwriting editorial prose
- logs exist only where useful
- validation and existing docs checks were run

Ask before destructive or URL-changing actions such as deleting documentation, moving published paths without redirects, replacing an established taxonomy, or resolving unsupported product or policy conflicts by invention.
