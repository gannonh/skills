#!/usr/bin/env python3
"""Validate the generated P-Stack Agent Skills and their internal references."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


NAME = re.compile(r"^ps-[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FORBIDDEN = re.compile(
    r"AskQuestion|subagent_type|run_in_background|Task tool|Task subagent|Task schema|"
    r"generalPurpose|is_background|readonly/Ask|Cursor cloud agent|"
    r"grok-4\.6-fast-xhigh|gpt-5\.6-sol-max|claude-fable-5-thinking-max|"
    r"claude-opus-5-thinking-xhigh"
)
ALLOWED_FRONTMATTER = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, nargs="?", default=Path.cwd())
    return parser.parse_args()


def frontmatter_fields(text: str) -> tuple[dict[str, str], set[str]]:
    match = FRONTMATTER.match(text)
    if not match:
        return {}, set()
    fields = {}
    keys = set()
    for line in match.group(1).splitlines():
        key = re.match(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$", line)
        if key:
            keys.add(key.group(1))
            fields[key.group(1)] = (key.group(2) or "").strip().strip('"')
    return fields, keys


def validate_link(markdown: Path, raw: str) -> str | None:
    target = raw.strip().split("#", 1)[0]
    if not target or target == "url" or "://" in target or target.startswith(("mailto:", "#", "/")):
        return None
    if any(character in target for character in ("<", ">", "*", "{", "}")):
        return None
    target = target.split()[0]
    resolved = (markdown.parent / target).resolve()
    if not resolved.exists():
        return f"{markdown}: unresolved link {raw}"
    return None


def validate(root: Path) -> list[str]:
    manifest_path = root / "pstack-port" / "manifest.json"
    if not manifest_path.exists():
        return [f"missing manifest: {manifest_path}"]
    manifest = json.loads(manifest_path.read_text())
    expected = {item["target"] for item in manifest["skills"]}
    actual = {
        path.name
        for path in root.glob("ps-*")
        if path.is_dir() and (path / ".ps-port.json").exists()
    }
    errors = []
    if actual != expected:
        errors.append(f"skill set mismatch; missing={sorted(expected - actual)} extra={sorted(actual - expected)}")
    old_names = {item["source"].rsplit("/", 1)[-1] for item in manifest["skills"]}
    slash_pattern = re.compile(
        r"(?<![A-Za-z0-9_.-])/("
        + "|".join(re.escape(name) for name in sorted(old_names, key=len, reverse=True))
        + r")\b"
    )
    for name in sorted(expected & actual):
        directory = root / name
        skill = directory / "SKILL.md"
        if not NAME.fullmatch(name):
            errors.append(f"invalid directory name: {name}")
        if not skill.exists():
            errors.append(f"missing SKILL.md: {name}")
            continue
        fields, keys = frontmatter_fields(skill.read_text())
        if fields.get("name") != name:
            errors.append(f"frontmatter name mismatch: {name}")
        description = fields.get("description", "")
        if not description or len(description) > 1024:
            errors.append(f"invalid description: {name}")
        unknown = keys - ALLOWED_FRONTMATTER
        if unknown:
            errors.append(f"nonstandard frontmatter in {name}: {sorted(unknown)}")
        for required in ("LICENSE.txt", "NOTICE.md", ".ps-port.json"):
            if not (directory / required).exists():
                errors.append(f"missing {required}: {name}")
        marker = json.loads((directory / ".ps-port.json").read_text())
        if marker.get("source_tree_sha256") != manifest["upstream"]["tree_sha256"]:
            errors.append(f"stale generation marker: {name}")
        for markdown in directory.rglob("*.md"):
            text = markdown.read_text()
            relative = markdown.relative_to(root)
            adapter_doc = name == "ps-setup-pstack" or markdown.name == "NOTICE.md"
            if not adapter_doc:
                match = FORBIDDEN.search(text)
                if match:
                    errors.append(f"{relative}: forbidden harness mechanic {match.group(0)}")
                slash = slash_pattern.search(text)
                if slash:
                    errors.append(f"{relative}: unprefixed skill invocation {slash.group(0)}")
            for raw in LINK.findall(text):
                problem = validate_link(markdown, raw)
                if problem:
                    errors.append(problem)
    return errors


def main() -> int:
    root = parse_args().root.resolve()
    errors = validate(root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(f"P-Stack validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    count = len(json.loads((root / "pstack-port" / "manifest.json").read_text())["skills"])
    print(f"validated {count} P-Stack Agent Skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
