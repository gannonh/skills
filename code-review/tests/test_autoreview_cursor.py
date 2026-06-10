#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.machinery
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTOREVIEW = ROOT / "scripts" / "autoreview"


def load_autoreview():
    loader = importlib.machinery.SourceFileLoader("autoreview_under_test", str(AUTOREVIEW))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None:
        raise RuntimeError("unable to load autoreview")
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class CursorEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.autoreview = load_autoreview()

    def test_cursor_is_registered_as_review_engine(self) -> None:
        self.assertIn("cursor", self.autoreview.ENGINES)
        with mock.patch.object(sys, "argv", ["autoreview", "--engine", "cursor"]):
            args = self.autoreview.parse_args()
        self.assertEqual(args.engine, "cursor")

    def test_cursor_agent_strips_status_text_before_review_json(self) -> None:
        report = {
            "findings": [],
            "overall_correctness": "patch is correct",
            "overall_explanation": "No actionable findings.",
            "overall_confidence": 0.9,
        }
        wrapper = {"type": "result", "result": "Inspecting files.\n" + json.dumps(report)}

        normalized = self.autoreview.normalize_cursor_output(json.dumps(wrapper))

        self.assertEqual(json.loads(normalized), report)

    def test_cursor_agent_uses_pinned_composer_model(self) -> None:
        captured = {}

        def fake_run_with_heartbeat(command, cwd, **kwargs):
            captured["command"] = command
            captured["cwd"] = cwd
            captured.update(kwargs)
            report = {
                "findings": [],
                "overall_correctness": "patch is correct",
                "overall_explanation": "No actionable findings.",
                "overall_confidence": 0.9,
            }
            stdout = json.dumps({"type": "result", "result": json.dumps(report)})
            captured["stdout"] = stdout
            return subprocess.CompletedProcess(command, 0, stdout, "")

        self.autoreview.run_with_heartbeat = fake_run_with_heartbeat
        self.autoreview.resolve_command = lambda command, repo: command
        args = argparse.Namespace(
            cursor_bin="cursor-agent",
            model=None,
            thinking=None,
            stream_engine_output=False,
            tools=True,
            web_search=True,
        )
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            output = self.autoreview.run_cursor(args, repo, "review prompt")

        command = captured["command"]
        self.assertEqual(json.loads(output)["findings"], [])
        self.assertIn("--model", command)
        self.assertEqual(command[command.index("--model") + 1], "composer-2.5")
        self.assertNotIn("--thinking", command)
        self.assertEqual(command[:3], ["cursor-agent", "--print", "--mode"])
        self.assertIn("--workspace", command)
        self.assertEqual(captured["input_text"], "review prompt")
        self.assertEqual(captured["label"], "cursor")


if __name__ == "__main__":
    unittest.main()
