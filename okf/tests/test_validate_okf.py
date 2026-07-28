from __future__ import annotations

import importlib.util
import subprocess
import sys
from datetime import date
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_okf.py"
spec = importlib.util.spec_from_file_location("validate_okf", SCRIPT)
validate_okf = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules["validate_okf"] = validate_okf
spec.loader.exec_module(validate_okf)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_documentation_bundle(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    write(
        docs / "index.md",
        "---\nokf_version: \"0.2\"\n---\n\n# Documentation\n\n* [Authentication](concepts/authentication.md) - authentication model\n",
    )
    write(
        docs / "concepts" / "authentication.md",
        """---
type: Domain Concept
title: Authentication
description: The product authentication model.
status: stable
generated: { by: human:gannonh, at: 2026-07-28T15:00:00Z }
verified: { by: human:gannonh, at: 2026-07-28T15:00:00Z }
sources:
  - id: auth-policy
    resource: /policies/authentication.md
    title: Authentication policy
---

# Authentication

Authentication follows the policy.[^auth-policy]

[^auth-policy]: Authentication policy
""",
    )
    write(
        docs / "policies" / "authentication.md",
        "---\ntype: Policy\ntitle: Authentication policy\ndescription: Canonical authentication policy.\n---\n\n# Policy\n\nUse federated identity.\n",
    )
    return docs


def test_documentation_profile_does_not_require_specs_or_adrs(tmp_path: Path) -> None:
    docs = create_documentation_bundle(tmp_path)

    result = validate_okf.validate_bundle(docs, level="repository", profile="documentation")

    assert result.errors == []
    assert not (docs / "specs").exists()
    assert not (docs / "adrs").exists()


def test_conformance_allows_missing_index(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    write(docs / "concept.md", "---\ntype: Reference\n---\n\n# Concept\n")

    result = validate_okf.validate_bundle(docs, level="conformance")

    assert result.errors == []


def test_repository_level_requires_root_index(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    write(docs / "concept.md", "---\ntype: Reference\n---\n\n# Concept\n")

    result = validate_okf.validate_bundle(docs, level="repository")

    assert "Missing repository index: index.md" in result.errors


def test_concept_missing_frontmatter_fails(tmp_path: Path) -> None:
    docs = create_documentation_bundle(tmp_path)
    write(docs / "guides" / "usage.md", "# Usage\n\nRun the CLI.\n")

    result = validate_okf.validate_bundle(docs)

    assert "guides/usage.md: missing YAML frontmatter" in result.errors


def test_concept_missing_type_fails(tmp_path: Path) -> None:
    docs = create_documentation_bundle(tmp_path)
    write(docs / "guides" / "usage.md", "---\ntitle: Usage\n---\n\n# Usage\n")

    result = validate_okf.validate_bundle(docs)

    assert "guides/usage.md: missing non-empty frontmatter field 'type'" in result.errors


def test_malformed_log_date_fails_when_log_exists(tmp_path: Path) -> None:
    docs = create_documentation_bundle(tmp_path)
    write(docs / "log.md", "# Update log\n\n## July 28, 2026\n* Updated docs.\n")

    result = validate_okf.validate_bundle(docs)

    assert "log.md:3: log date headings must use YYYY-MM-DD" in result.errors


def test_nested_index_frontmatter_fails(tmp_path: Path) -> None:
    docs = create_documentation_bundle(tmp_path)
    write(docs / "guides" / "index.md", "---\ntitle: Guides\n---\n\n# Guides\n")

    result = validate_okf.validate_bundle(docs)

    assert "guides/index.md: reserved index.md may contain only root-level okf_version frontmatter" in result.errors


def test_broken_local_links_warn_by_default(tmp_path: Path) -> None:
    docs = create_documentation_bundle(tmp_path)
    write(
        docs / "guides" / "usage.md",
        "---\ntype: Guide\ntitle: Usage\ndescription: Usage guide.\n---\n\nSee [missing](/missing.md).\n",
    )

    result = validate_okf.validate_bundle(docs)

    assert result.errors == []
    assert "guides/usage.md: broken local link: /missing.md" in result.warnings


def test_strict_links_turns_broken_links_into_errors(tmp_path: Path) -> None:
    docs = create_documentation_bundle(tmp_path)
    write(
        docs / "guides" / "usage.md",
        "---\ntype: Guide\n---\n\nSee [missing](/missing.md).\n",
    )

    result = validate_okf.validate_bundle(docs, strict_links=True)

    assert "guides/usage.md: broken local link: /missing.md" in result.errors


def test_valid_v02_provenance_trust_and_lifecycle_pass(tmp_path: Path) -> None:
    docs = create_documentation_bundle(tmp_path)

    result = validate_okf.validate_bundle(docs, level="conformance")

    assert result.errors == []


def test_invalid_status_fails(tmp_path: Path) -> None:
    docs = create_documentation_bundle(tmp_path)
    write(docs / "bad.md", "---\ntype: Guide\nstatus: current\n---\n\n# Bad\n")

    result = validate_okf.validate_bundle(docs, level="conformance")

    assert "bad.md: status must be one of draft, stable, deprecated" in result.errors


def test_source_requires_resource(tmp_path: Path) -> None:
    docs = create_documentation_bundle(tmp_path)
    write(
        docs / "bad-source.md",
        "---\ntype: Research Note\nsources:\n  - id: source-one\n    title: Missing resource\n---\n\n# Note\n",
    )

    result = validate_okf.validate_bundle(docs, level="conformance")

    assert "bad-source.md: sources[0].resource must be a non-empty string" in result.errors


def test_verified_bare_mapping_is_accepted(tmp_path: Path) -> None:
    docs = create_documentation_bundle(tmp_path)
    write(
        docs / "verified.md",
        "---\ntype: Policy\nverified: { by: human:gannonh, at: 2026-07-28T15:00:00Z }\n---\n\n# Verified\n",
    )

    result = validate_okf.validate_bundle(docs, level="conformance")

    assert result.errors == []


def test_verified_event_requires_valid_datetime(tmp_path: Path) -> None:
    docs = create_documentation_bundle(tmp_path)
    write(
        docs / "verified.md",
        "---\ntype: Policy\nverified: { by: human:gannonh, at: yesterday }\n---\n\n# Verified\n",
    )

    result = validate_okf.validate_bundle(docs, level="conformance")

    assert "verified.md: verified[0].at must be an ISO 8601 datetime" in result.errors


def test_attested_computation_requires_runtime(tmp_path: Path) -> None:
    docs = create_documentation_bundle(tmp_path)
    write(
        docs / "computation.md",
        "---\ntype: Attested Computation\n---\n\n# Computation\n\n```sql\nselect 1\n```\n",
    )

    result = validate_okf.validate_bundle(docs, level="conformance")

    assert "computation.md: frontmatter.runtime must be a non-empty string" in result.errors


def test_editorial_level_warns_about_legacy_v01_patterns(tmp_path: Path) -> None:
    docs = create_documentation_bundle(tmp_path)
    write(
        docs / "legacy.md",
        "---\ntype: Reference\ntitle: Legacy\ndescription: Legacy reference.\ntimestamp: 2026-05-28T14:30:00Z\n---\n\n# Legacy\n\n# Citations\n\n- https://example.com\n",
    )

    result = validate_okf.validate_bundle(docs, level="editorial")

    assert any("legacy v0.1 'timestamp'" in warning for warning in result.warnings)
    assert any("legacy # Citations section" in warning for warning in result.warnings)


def test_editorial_level_warns_about_stale_orphan_and_duplicate_titles(tmp_path: Path) -> None:
    docs = create_documentation_bundle(tmp_path)
    write(
        docs / "orphan-one.md",
        "---\ntype: Guide\ntitle: Duplicate\ndescription: First duplicate.\nstale_after: 2026-07-01\n---\n\n# One\n",
    )
    write(
        docs / "orphan-two.md",
        "---\ntype: Guide\ntitle: Duplicate\ndescription: Second duplicate.\n---\n\n# Two\n",
    )

    result = validate_okf.validate_bundle(docs, level="editorial", today=date(2026, 7, 28))

    assert any("stale_after 2026-07-01 has passed" in warning for warning in result.warnings)
    assert any("orphan-one.md: concept has no inbound local links" in warning for warning in result.warnings)
    assert any("Duplicate title across concepts" in warning for warning in result.warnings)


def test_cli_returns_nonzero_on_conformance_errors(tmp_path: Path) -> None:
    docs = create_documentation_bundle(tmp_path)
    write(docs / "broken.md", "# Missing frontmatter\n")

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path), "--level", "conformance"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert completed.returncode == 1
    assert "broken.md: missing YAML frontmatter" in completed.stderr
