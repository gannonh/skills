from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONFIGURE = ROOT / "ps-setup-pstack" / "scripts" / "configure.py"
VALIDATE = ROOT / "pstack-port" / "scripts" / "validate_pstack_port.py"


def plan() -> dict:
    harnesses = {}
    models = {
        "pi": ("openai-codex/gpt-5.6-luna", "openai-codex/gpt-5.6-terra", "openai-codex/gpt-5.6-sol"),
        "codex": ("gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol"),
        "cursor": ("gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol"),
        "opencode": ("openai/gpt-5.6-luna", "openai/gpt-5.6-terra", "openai/gpt-5.6-sol"),
        "claude": ("claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-7"),
    }
    for harness, identifiers in models.items():
        tiers = {}
        for tier, model in zip(("small", "medium", "large"), identifiers, strict=True):
            tiers[tier] = {
                "label": model,
                "model": model,
                "reasoning": "high",
                "verified_by": "test fixture",
                "verified_on": "2026-08-27",
            }
        harnesses[harness] = {"harness_version": "test", "tiers": tiers}
    return {"schema_version": 1, "harnesses": harnesses}


class PStackPortTests(unittest.TestCase):
    def test_generated_port_validates(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATE), str(ROOT)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("validated 45", result.stdout)

    def test_setup_renders_all_harnesses_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            plan_path = repo / "plan.json"
            plan_path.write_text(json.dumps(plan()))
            (repo / "AGENTS.md").write_text("# Existing instructions\n")
            first = subprocess.run(
                [sys.executable, str(CONFIGURE), "--repo", str(repo), "--plan", str(plan_path)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            expected = (
                repo / ".agents" / "pstack" / "models.json",
                repo / ".pi" / "agents" / "ps-small.md",
                repo / ".codex" / "agents" / "ps-medium.toml",
                repo / ".cursor" / "agents" / "ps-large.md",
                repo / ".opencode" / "agents" / "ps-small.md",
                repo / ".claude" / "agents" / "ps-large.md",
                repo / ".codex" / "config.toml",
                repo / "CLAUDE.md",
            )
            self.assertTrue(all(path.exists() for path in expected))
            before = {path: path.read_bytes() for path in expected + (repo / "AGENTS.md",)}
            second = subprocess.run(
                [sys.executable, str(CONFIGURE), "--repo", str(repo), "--plan", str(plan_path)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            after = {path: path.read_bytes() for path in before}
            self.assertEqual(before, after)
            check = subprocess.run(
                [sys.executable, str(CONFIGURE), "--repo", str(repo), "--plan", str(plan_path), "--check"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)

    def test_setup_rejects_malformed_markers_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            plan_path = repo / "plan.json"
            plan_path.write_text(json.dumps(plan()))
            (repo / "AGENTS.md").write_text(
                "<!-- ps-pstack:begin -->\nold\n<!-- ps-pstack:begin -->\n<!-- ps-pstack:end -->\n"
            )
            result = subprocess.run(
                [sys.executable, str(CONFIGURE), "--repo", str(repo), "--plan", str(plan_path)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((repo / ".agents" / "pstack" / "models.json").exists())

    def test_setup_mirrors_only_owned_claude_skills(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "repo"
            source = root / "skills"
            repo.mkdir()
            source.mkdir()
            plan_path = root / "plan.json"
            plan_path.write_text(json.dumps(plan()))
            owned = source / "ps-example"
            owned.mkdir()
            (owned / ".ps-port.json").write_text("{}\n")
            (owned / "SKILL.md").write_text("first\n")
            unowned = source / "ps-personal"
            unowned.mkdir()
            (unowned / "SKILL.md").write_text("do not copy\n")

            command = [
                sys.executable,
                str(CONFIGURE),
                "--repo",
                str(repo),
                "--plan",
                str(plan_path),
                "--mirror-claude-skills",
                "--skills-source",
                str(source),
            ]
            first = subprocess.run(command, check=False, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            mirrored = repo / ".claude" / "skills" / "ps-example"
            self.assertEqual((mirrored / "SKILL.md").read_text(), "first\n")
            self.assertFalse((repo / ".claude" / "skills" / "ps-personal").exists())

            (owned / "SKILL.md").write_text("second\n")
            second = subprocess.run(command, check=False, capture_output=True, text=True)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual((mirrored / "SKILL.md").read_text(), "second\n")


if __name__ == "__main__":
    unittest.main()
