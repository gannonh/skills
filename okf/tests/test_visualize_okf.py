from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "visualize_okf.py"
spec = importlib.util.spec_from_file_location("visualize_okf", SCRIPT)
visualize_okf = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules["visualize_okf"] = visualize_okf
spec.loader.exec_module(visualize_okf)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_bundle(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    write(docs / "index.md", '---\nokf_version: "0.2"\n---\n\n# Docs\n')
    write(
        docs / "concepts" / "auth.md",
        """---
type: Domain Concept
title: Authentication
description: Identity and access.
generated: {by: human:gannonh, at: 2026-07-28T10:00:00Z}
verified:
  - by: human:gannonh
    at: 2026-07-28T10:00:00Z
sources:
  - id: setup
    resource: /guides/setup.md
---
# Authentication

See the [setup guide](/guides/setup.md).
""",
    )
    write(
        docs / "guides" / "setup.md",
        """---
type: Guide
title: Setup
status: draft
stale_after: 2026-07-01
---
# Setup

See [authentication](../concepts/auth.md).
""",
    )
    return docs


def test_generate_visualization_supports_absolute_and_relative_links(tmp_path: Path) -> None:
    docs = create_bundle(tmp_path)
    out = tmp_path / "viewer.html"

    stats = visualize_okf.generate_visualization(docs, out, bundle_name="Example")
    html = out.read_text(encoding="utf-8")

    assert stats["concepts"] == 2
    assert stats["edges"] == 2
    assert "concepts/auth__guides/setup" in html
    assert "guides/setup__concepts/auth" in html
    assert "human-reviewed" in html
    assert "cytoscape@3.28.1" in html
    assert "marked@12.0.0" in html


def test_malformed_concept_is_skipped_with_warning(tmp_path: Path, capsys) -> None:
    docs = create_bundle(tmp_path)
    write(docs / "broken.md", "# Missing frontmatter\n")

    stats = visualize_okf.generate_visualization(docs, tmp_path / "viewer.html")
    captured = capsys.readouterr()

    assert stats["concepts"] == 2
    assert stats["warnings"] == 1
    assert "broken.md: missing YAML frontmatter; skipped" in captured.err


def test_cli_defaults_to_repo_docs_and_viz_html(tmp_path: Path) -> None:
    create_bundle(tmp_path)

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert completed.returncode == 0
    assert (tmp_path / "docs" / "viz.html").exists()
    assert "Wrote 2 concept(s), 2 edge(s)" in completed.stderr
