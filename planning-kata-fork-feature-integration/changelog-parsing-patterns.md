# Changelog Parsing Patterns

Reference for parsing changelogs following [Keep a Changelog](https://keepachangelog.com/) format.

## Structure Recognition

### Version Headers
```markdown
## [Unreleased]
## [1.2.3] - 2024-01-15
## [1.2.2] - 2024-01-10
```

**Regex**: `^## \[([^\]]+)\](?: - (\d{4}-\d{2}-\d{2}))?$`
- Group 1: Version (e.g., "1.2.3" or "Unreleased")
- Group 2: Date (optional, e.g., "2024-01-15")

### Change Categories
```markdown
### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security
```

**Regex**: `^### (Added|Changed|Deprecated|Removed|Fixed|Security)$`

### Entry Items
```markdown
- New feature description
- **BREAKING:** Change that breaks compatibility
- `command-name` now does something different
```

## Parsing Algorithm

```
1. Split file by version headers
2. For each version section:
   a. Extract version number and date
   b. Split by category headers
   c. For each category:
      - Extract bullet points
      - Identify breaking changes (contains "**BREAKING:**")
      - Extract command/feature references (backticks)
3. Build structured representation
```

## Feature Extraction Heuristics

### Identifying Distinct Features

**New Features** (from `### Added`):
- Look for: "New", "Added", command names in backticks
- Each top-level bullet = one feature
- Nested bullets = feature details

**Behavioral Changes** (from `### Changed`):
- Look for: "now", "instead of", "refactored"
- May indicate breaking changes without explicit marker

**Breaking Changes**:
- Explicit: Contains `**BREAKING:**`
- Implicit: "Removed", "Renamed", "Changed ... API"

### Filtering Non-Features

Skip entries that are:
- Documentation only: "Updated README", "Added docs"
- Internal: "Refactored internals", "Code cleanup"
- Housekeeping: "Updated dependencies", "Fixed typo"
- Test-only: "Added tests for", "Improved test coverage"

## Comparison Logic

### Matching Features Between Changelogs

Features are considered **equivalent** if:
1. Same command/function name referenced
2. Same functional description (fuzzy match)
3. Implemented in same version range

Features are considered **different implementations** if:
1. Same goal but different approach
2. Fork-specific adaptation noted

### Delta Calculation

```
upstream_features = parse(upstream_changelog)
fork_features = parse(fork_changelog)

for feature in upstream_features:
    if feature.version > fork_point:
        if not has_equivalent(fork_features, feature):
            delta.append(feature)
```

## Example Parsed Structure

```json
{
  "version": "1.5.18",
  "date": "2026-01-16",
  "categories": {
    "Added": [
      {
        "text": "Plan verification loop — Plans are now verified before execution",
        "breaking": false,
        "references": ["gsd-plan-checker"],
        "complexity_hint": "high"
      }
    ],
    "Changed": [
      {
        "text": "/gsd:plan-phase refactored to thin orchestrator pattern",
        "breaking": false,
        "references": ["/gsd:plan-phase", "gsd-planner", "gsd-plan-checker"]
      }
    ]
  }
}
```

## Complexity Estimation

| Indicator | Complexity |
|-----------|------------|
| "New command" | Medium |
| "New agent" | High |
| "refactored", "redesigned" | High |
| "flag", "option" | Low |
| "**BREAKING:**" | High |
| "Fixed" | Low (unless architectural) |
| "workflow" | Medium-High |
| "template" | Low |
