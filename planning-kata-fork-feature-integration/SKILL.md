---
name: planning-kata-fork-feature-integration
description: Use this skill when analyzing upstream GSD changees to identify feature deltas with Kata, syncing features from GSD to Kata, comparing changelogs between projects, and creating feature integration plans. Triggers include "sync from GSD", "what's new in GSD", "GSD features", "feature delta", "integrate GSD feature", "GSD sync plan", and "GSD changes".
---

# GSD → Kata Feature Integration Planning

Analyze the upstream GSD project's changelog, compare it against Kata's changelog, identify functional deltas, and generate a prioritized integration plan for syncing features to Kata.

## Project Paths

| Project            | Path                                      |
| ------------------ | ----------------------------------------- |
| **GSD (upstream)** | `/Users/gannonhall/dev/oss/get-shit-done` |
| **Kata (fork)**    | `/Users/gannonhall/dev/oss/kata`          |

## Context

Kata is a hard fork of GSD (Get Shit Done). It diverged at approximately GSD v1.5.x and rebranded with version 0.1.0. Features added to GSD after the fork point may be valuable to integrate into Kata. 

### Primary functional differences

- Kata uses Skills where GSF uses Slash Commands

### Other differences

- Kata rebrands commands and agents from `gsd-*` to `kata-*`
- Kata has a different versioning scheme starting at 0.1.0
- Different default configurations and templates

### Project Docs

#### Kata
- @/Users/gannonhall/dev/oss/kata/README.md
- @/Users/gannonhall/dev/oss/kata/CHANGELOG.md

#### GSD
- @/Users/gannonhall/dev/oss/get-shit-done/README.md
- @/Users/gannonhall/dev/oss/get-shit-done/CHANGELOG.md


## Workflow

### Step 1: Load Changelogs

```
GSD:  /Users/gannonhall/dev/oss/get-shit-done/CHANGELOG.md
Kata: /Users/gannonhall/dev/oss/kata/CHANGELOG.md
```

Parse using Keep a Changelog format (see `./changelog-parsing-patterns.md`).

### Step 2: Establish Fork Point

Kata forked from GSD around **v1.5.21** (2026-01-16) based on:
- Kata v0.1.0 release date: 2026-01-18
- Feature parity analysis between projects

If this seems incorrect, ask the user to confirm the fork point version.

### Step 3: Extract GSD Features Since Fork

For each GSD version **after v1.5.21**, extract:

| Category             | What to Capture              |
| -------------------- | ---------------------------- |
| **New Commands**     | `/gsd:*` commands added      |
| **New Agents**       | `gsd-*` agents introduced    |
| **Workflow Changes** | Modified execution flows     |
| **Breaking Changes** | Items marked `**BREAKING:**` |
| **Bug Fixes**        | Fixes that may apply to Kata |

**Skip**:
- GSD-specific branding/naming (Kata has its own)
- Documentation-only changes
- Features Kata already has (check Kata changelog)

### Step 4: Assess Integration Complexity

For each GSD feature not in Kata:

| Complexity | Criteria                                   | Examples                            |
| ---------- | ------------------------------------------ | ----------------------------------- |
| **Low**    | Isolated addition, copy-paste viable       | New flag, template                  |
| **Medium** | Requires adaptation for Kata naming        | Command rename gsd→kata             |
| **High**   | Architectural change, multiple files       | New agent system, workflow redesign |
| **Skip**   | Not applicable or already done differently | GSD-specific tooling                |

### Step 5: Generate Integration Plan

Create plan using `./templates/integration-plan-template.md`:

1. **Summary**: Features available, by complexity
2. **Priority Backlog**: High-value features first
3. **Dependencies**: What must come before what
4. **Kata Adaptations**: Renaming gsd→kata, path changes

### Step 6: Prepare Output Files

Prepare these files for saving:

```
INTEGRATION-PLAN.md           # Main roadmap
DELTA-ANALYSIS.md             # Feature-by-feature breakdown
{date}-sync-from-v{x.y.z}.md  # Historical record (copy of plan)
```

Default save location: `/Users/gannonhall/dev/oss/kata/.planning/deltas/`

## Example Invocation

**User**: "What's new in GSD that Kata doesn't have?"

**Actions**:
1. Read GSD CHANGELOG.md
2. Read Kata CHANGELOG.md
3. Identify all GSD features from v1.5.22 onwards
4. Filter out features Kata already implemented
5. Categorize remaining features by complexity
6. Generate integration plan
7. Ask user to confirm save location
8. Save to `/Users/gannonhall/dev/oss/kata/.planning/deltas/` (if confirmed)

## Key GSD → Kata Translations

When integrating GSD features into Kata:

| GSD                     | Kata               |
| ----------------------- | ------------------ |
| `/gsd:*` commands       | `/kata:*` commands |
| `gsd-*` agents          | `kata-*` agents    |
| `.planning/` paths      | Same (no change)   |
| `get-shit-done` package | `kata` package     |
| GSD branding            | Kata branding      |

## Output

1. **Console Summary**: Quick delta count and highlights
2. **INTEGRATION-PLAN.md**: Prioritized feature backlog with phases
3. **DELTA-ANALYSIS.md**: Detailed feature comparison

### Step 7: Confirm Save Location

After generating the plan output, use AskUserQuestion to confirm:

```
Would you like me to save the integration plan to /Users/gannonhall/dev/oss/kata/.planning/deltas?
```

Options:
- **Yes, save to deltas/** — Save INTEGRATION-PLAN.md and DELTA-ANALYSIS.md to `.planning/deltas/`
- **Save to different location** — Let user specify custom path
- **Don't save** — Output only, no file creation

If user confirms, create the directory if needed and save the files.

## Acceptance Criteria

- [ ] GSD changelog parsed (all versions from v1.5.22+)
- [ ] Kata changelog parsed (v0.1.0+)
- [ ] Feature delta list generated
- [ ] Each feature assigned complexity rating
- [ ] User prompted for save location confirmation
- [ ] Integration plan saved to Kata's `.planning/deltas/` (if confirmed)
- [ ] Plan includes GSD→Kata naming adaptations
